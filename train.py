"""Program for training the text-generator model.
Has some options; more info in --help."""

import string
import re
import argparse
import sys
import os
import operator


def prepare_input():
    """
Works with --input_dir parameter.
    """
    global input_files
    global input_file
    if args.input_dir:
        os.chdir(args.input_dir)
        list_of_files = os.listdir()
        for f_name in list_of_files:
            if f_name[len(f_name)-3:] == "txt":
                input_files.append(os.path.join(os.getcwd(), f_name))
    else:
        input_file = sys.stdin
    """
Now creates directory "model" for our database based on --model parameter.
    """
    model_dir = "model"
    os.chdir(args.model)
    if model_dir not in os.listdir():
        os.mkdir(model_dir)
    os.chdir(os.path.join(args.model, model_dir))


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
    model_files = os.listdir()
    if "index.txt" in model_files:
        index_file = open("index.txt")
        for f_name in model_files:
            if f_name[0:4] == "list":
                file_count = max(file_count, int(f_name[4:len(f_name)-4]))
    else:
        with open("index.txt", "w"):
            pass
    """
Saves into dict our "index"-file for quicker access.
    """
    global index_dict
    with open("index.txt") as index_file:
        for line in index_file:
            pair = [x for x in line.split()]
            index_dict[pair[0]] = int(pair[1])

    return file_count


def read_input(file_count):
    """
Big function, reads input file. Input parameter - amount of files in old model.
We add pairs "string-string" for each pair of concesutive words in dict called
frequency. It looks like this:
frequency[word] = dict of words which were met after it in model;
frequency[word][second_word] = N - the number of times when a pair
"word-second_word" appeared in model.
Returns the biggest X-number out of all possible "list"-files.
    """
    first_word = '*start*'
    chars = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')
    files_before = file_count
    words_number = 0
    global frequency
    for line in input_file:
        text = [x for x in line.rstrip().split()]
        word = ""
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
Numbers "5" and "50" below are the magic constants that control this process.
                """
                if first_word in index_dict:
                    file_number = index_dict[first_word]
                else:
                    words_number += 1
                    if words_number > 5*min(50, file_count-files_before+1):
                        words_number = 1
                        file_count += 1
                    file_number = file_count
                    index_dict[first_word] = file_number
                """
Writes a pair to the dict.
                """
                if first_word not in frequency:
                    frequency[first_word] = dict()
                if succ_word not in frequency[first_word]:
                    frequency[first_word][succ_word] = 1
                else:
                    frequency[first_word][succ_word] += 1

                first_word = succ_word
        if word == '*end*' and input_file == sys.stdin:
            break

    if input_file is not sys.stdin:
        input_file.close()
    """
Updates "index"-file with new info.
    """
    with open("index.txt", "w") as index_file:
        sorted_index = sorted(index_dict.items(), key=operator.itemgetter(1))
        for pair in sorted_index:
            index_file.write(pair[0]+" "+str(pair[1])+" \n")

    return file_count


def update_model(file_count):
    """
Update our "list"-files with new info stored in dict.
Info consists of words and their frequences.
    """
    index_file = open("index.txt")
    for file_number in range(1, file_count + 1):
        lst_words = [x for x in index_dict.keys() if index_dict[x] == file_number]

        """
^ We take every word from "index"-file which belongs to the same filenumber
and update the "list"-file of these word with new info about it.
v Checks if "list"-file is not empty. If it is, skips the dict-filling.
        """
        try:
            base_file = open("list"+str(file_number)+".txt")
        except IOError as e:
            with open("list"+str(file_number)+".txt", "w"):
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
                        suc_word = word_freq[0]
                        if suc_word not in frequency[begin_word]:
                            frequency[begin_word][suc_word] = int(word_freq[1])
                        else:
                            frequency[begin_word][suc_word] += int(word_freq[1])
            base_file.close()
            """
Don't forget to clear "list"-file in order to write into it after.
            """
            with open("list"+str(file_number)+".txt", "w"):
                pass
        """
Writes updated info from dict into a "list"-file.
        """
        with open("list"+str(file_number)+".txt", "w") as curr_file:
            for first_word in lst_words:
                curr_file.write(first_word + ":")
                for word in frequency[first_word]:
                    curr_file.write("#"+word+" "+str(frequency[first_word][word]))
                curr_file.write(' \n')
                del frequency[first_word]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A trainee program.')
    parser.add_argument("-in", "--input_dir",
                        help="""Input dir path.
                        If not specified, stdin is used;
                        type then *end* to end the input.""")
    parser.add_argument("-m", "--model", default=os.getcwd(),
                        help="Received model file path.")
    parser.add_argument("-nlc", action="store_true",
                        help="""Don't bring texts to lowercase.
                        False by default.""")
    args = parser.parse_args()

    input_files = []
    files_amount = 0
    index_dict = dict()
    frequency = dict()
    prepare_input()

    cnt_files_in_model = prepare_model()

    for path in input_files:
        input_file = open(path)
        files_amount = max(files_amount, read_input(cnt_files_in_model))

    update_model(files_amount)
