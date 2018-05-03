"""Program for training the text-generator model.
Has some options; more info in --help."""

import string
import re
import argparse
import sys
import os


def prepare_input():
    """
Works with --input_dir parameter.
    """
    global input_file
    if args.input_dir:
        input_file = open(args.input_dir)
    else:
        input_file = sys.stdin
    """
Now creates directory "model" for our database based on --model parameter.
    """
    model_dir = "model"
    os.chdir(args.model)
    if model_dir not in os.listdir():
        os.mkdir(model_dir)
    os.chdir(args.model + "\\" + model_dir)

def prepare_model():
    """
Works a bit with old model, if it exists.
In model we have an important "index"-file. There are pairs "string - number"
in this file. String is a unique common word from input text,
number points to the file with all information about this word.
All such files have names "listX", where X is this number.
Returns the biggest X number used in current model.
    """
    file_count = 1
    list_of_files = os.listdir()
    if "index.rtf" in list_of_files:
        index_file = open("index.rtf")
        for f_name in list_of_files:
            if f_name[0:4] == "list":
                file_count = max(file_count, int(f_name[4:len(f_name)-4]))
    else:
        with open("index.rtf", "w"), open("tmp1.rtf", "w"):
            pass
    """
Saves into RAM our "index"-file for quicker access.
    """
    global index_dict
    with open("index.rtf") as index_file:
        for line in index_file:
            pair = [x for x in line.split()]
            index_dict[pair[0]] = int(pair[1])

    return file_count
        

def read_input(file_count):
    """
Big function, reads input file. Input parameter - amount of files in old model.
At the end we will have some tmp files. We store there pairs "string-string".
All these pairs are pairs of consecutive words in input text.
In file "tmpX", X - number, there are only pairs with first word having 
number X in "index"-file.
Returns the biggest X-number out of all "tmp"-files.
    """
    first_word = '*start*'
    chars = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')
    files_before = file_count
    words_number = 0
    
    for line in input_file:
        text = [x for x in line.rstrip().split()]
        for raw_word in text:
            word = raw_word
            """
Check for -nlc (? bring texts to lowercase ?) parameter.
            """
            if not args.nlc:
                word = word.lower()
            if word == '*end*' and input_file == sys.stdin:
                break
            match = chars.search(word)
            if match:
                succ_word = match.group()
                if succ_word == "-":
                    continue
                file_number = 0
                """
Calculates the number of file, where we should write a pair.

    Explanation of this calculating+storing process:
You know that in every language some words are much popular than others.
Because of that, they have more info and require more storage.
But for me it's important for all "list"-files to consume approximately
the same amount of storage. 
So my "list"-files aren't storing the same amount of words. Instead of that,
the number of words stored in file increases with the number of that file.
First few files store only about 5-20 words, last files can have >500 words
inside. It is based on idea that the "popular" words will appear in input
earlier than others.
Number "5" below is the magic constant that controls this process.
                """
                if first_word in index_dict:
                    file_number = index_dict[first_word]
                else:
                    words_number += 1
                    if words_number > 5*(file_count-files_before+1):
                        words_number = 1
                        file_count += 1
                        with open("tmp"+str(file_count)+".rtf", "w"):
                            pass
                    with open("index.rtf", "a") as index_file:
                        index_file.write(first_word+" "+str(file_count)+" \n")
                    file_number = file_count
                    index_dict[first_word] = file_number
                """
Writes a pair to the right "tmp"-file.
                """
                succ_word = match.group()
                with open("tmp"+str(file_number)+".rtf", "a") as curr_file:
                    curr_file.write(first_word + ":" + succ_word + "\n")
                first_word = succ_word
        if raw_word == '*end*' and input_file == sys.stdin:
            break

    if input_file is not sys.stdin:
        input_file.close()

    return file_count


def update_model():
    """
Update our "list"-files with info stored in "tmp"-files.
Info consists of words and their frequences.
    """
    index_file = open("index.rtf")
    frequency = dict()
    file_number = 0
    for input_line in index_file:
        pair = [x for x in input_line.split()]
        first_word = pair[0]
        """
^ We take every single word from "index"-file and try to update
the "list"-file of this word with new info about it in "tmp"-file.
v If "tmpX" doesn't exist, we don't need to update "listX"-file.
        """
        try:
            curr_file = open("tmp"+pair[1]+".rtf")
        except IOError as e:
            continue
        else:
            curr_file.close()
        """
When we meet new "list"-file, we collect all info from it to a dict called
frequency. It looks like this:
frequency[word] = dict of words which were met after it in model;
frequency[word][second_word] = N - the number of times when a pair
"word-second_word" appeared in model.
        """
        if int(pair[1]) > file_number:
            file_number = int(pair[1])
            frequency.clear()
            """
Checks if "list"-file is not empty. If it is, skips the dict-filling.
            """
            try:
                base_file = open("list"+str(file_number)+".rtf")
            except IOError as e:
                with open("list"+str(file_number)+".rtf", "w"):
                    pass
            else:
                """
Fills the dict. Parses every string from "list"-file.
A string in "list"-file looks like this:
"word:#word_1 N1 #word_2 N2 ... \n"
                """
                for line in base_file:
                    lst = [x for x in line.split(':')]
                    begin_word = lst[0]
                    if begin_word not in frequency:
                        frequency[begin_word] = dict()
                    words = lst[1].rstrip().split('#')
                    for w in words:
                        if w != '':
                            word_freq = [x for x in w.split()]
                            succ_word = word_freq[0]
                            frequency[begin_word][succ_word] = int(word_freq[1])
                base_file.close()
                """
Don't forget to clear "list"-file in order to write into it after.
                """
                with open("list"+str(file_number)+".rtf", "w"):
                    pass
        """
Updates our dict with new pairs from "tmp"-file. 
        """
        try:
            curr_file = open("tmp"+str(file_number)+".rtf")
        except IOError as e:
            pass
        else:
            if first_word not in frequency:
                frequency[first_word] = dict()
            for line in curr_file:
                pair_of_words = [x for x in line.split(':')]
                if pair_of_words[0] == first_word:
                    succ_word = pair_of_words[1].rstrip()
                    if succ_word in frequency[first_word]:
                        frequency[first_word][succ_word] += 1
                    else:
                        frequency[first_word][succ_word] = 1
            curr_file.close()
        """
Writes updated info from dict into a "list"-file.
        """
        with open("list"+str(file_number)+".rtf", "a") as curr_file:
            curr_file.write(first_word + ":")
            for word in frequency[first_word]:
                curr_file.write("#"+word+" "+str(frequency[first_word][word]))
            curr_file.write(' \n')
            del frequency[first_word]


def delete_tmp(file_number):
    """
Deletes all "tmp"-files, they are not useful anymore.
    """
    for n in range(1, file_number+1):
        try:
            curr_file = open("tmp"+str(n)+".rtf")
        except IOError as e:
            pass
        else:
            curr_file.close()
            os.remove("tmp"+str(n)+".rtf")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A trainee program.')
    parser.add_argument("-in", "--input_dir",
                        help="""Input file path.
                        If not specified, stdin is used;
                        type then *end* to end the input.""")
    parser.add_argument("-m", "--model", default=os.getcwd(),
                        help="Received model file path.")
    parser.add_argument("-nlc", action="store_true",
                        help="""Don't bring texts to lowercase.
                        False by default.""")
    args = parser.parse_args()

    prepare_input()
    index_dict = dict()
    files_in_model = prepare_model()  
    
    tmp_files_amount = read_input(files_in_model)

    update_model()

    delete_tmp(tmp_files_amount)
