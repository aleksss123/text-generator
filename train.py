"""Program for training the text-generator model.
Has some options; more info in --help."""

import string
import re
import argparse
import sys
import os
import operator
from collections import defaultdict


class Trainer:
    """
Main class. Here are the most important variables.
    """
    def __init__(self):
        self.lst_files_amount = 1
        self.index_dict = dict()
        self.frequency = dict()
        self.input_files = []

    def train(self):
        """
Main function.
        """
        self.prepare_input()
        self.prepare_model()

        if self.input_files[0] == sys.stdin:
            self.read_input()
        else:
            for path in self.input_files:
                input_file = open(path)
                self.read_input(input_file)

        self.update_model()

    def prepare_input(self):
        """
Works with --input_dir parameter.
Function returns list with paths to all input files in input_dir.
        """
        if args.input_dir:
            os.chdir(args.input_dir)
            list_of_files = os.listdir()
            for f_name in list_of_files:
                if f_name[len(f_name)-3:] == "txt":
                    self.input_files.append(os.path.join(os.getcwd(), f_name))
        else:
            self.input_files.append(sys.stdin)
        """
Now creates directory "model" for our database based on --model parameter.
        """
        model_dir = "model"
        if args.model is not None:
            os.makedirs(args.model, exist_ok=True)
            os.chdir(args.model)
        if model_dir not in os.listdir():
            os.mkdir(model_dir)
        os.chdir(model_dir)

    def prepare_model(self):
        """
Works a bit with old model, if it exists.
In model we have an important "index"-file. There are pairs "string - number"
in this file. String is a unique common word from input text,
number points to the file with all information about this word.
All such files have names "listX", where X is this number.
Returns the biggest X number used in current model + an array.
        """
        model_files = os.listdir()
        if "index.txt" in model_files:
            index_file = open("index.txt")
            for f_name in model_files:
                if f_name[0:4] == "list":
                    tmp = int(f_name[4:len(f_name)-4])
                    self.lst_files_amount = max(self.lst_files_amount, tmp)
        else:
            with open("index.txt", "w"):
                pass
        """
Saves into dict our "index"-file for quicker access.
        """
        with open("index.txt") as index_file:
            for line in index_file:
                pair = [x for x in line.split()]
                self.index_dict[pair[0]] = int(pair[1])

    def read_input(self, input_file=sys.stdin):
        """
Big function, reads input file. Input parameter - amount of files in old model.
We add pairs "string-string" for each pair of concesutive words in dict called
frequency. It looks like this:
frequency[word] = dict of words which were met after it in model;
frequency[word][second_word] = N - the number of times when a pair
"word-second_word" appeared in model.
Returns the biggest X-number out of all possible "list"-files + 2 arrays.
        """
        first_word = None
        chars = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')
        files_before = max(self.lst_files_amount//10, 1)
        files_now = max(self.lst_files_amount//10, 1)
        words_number = 0
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
                match = chars.search(word)
                if match:
                    succ_word = match.group()
                    if succ_word == "-":
                        continue
                    if first_word is None:
                        first_word = succ_word
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
Numbers "7" and "50" below are the magic constants that control this process.
                    """
                    if first_word in self.index_dict:
                        file_number = self.index_dict[first_word]
                    else:
                        words_number += 1
                        if words_number > 7*min(50, files_now-files_before+1):
                            words_number = 1
                            files_now += 1
                        file_number = files_now
                        self.index_dict[first_word] = file_number
                    """
Writes a pair to the dict.
                    """
                    if first_word not in self.frequency:
                        self.frequency[first_word] = defaultdict(int)
                    self.frequency[first_word][succ_word] += 1
                    first_word = succ_word

        if input_file is not sys.stdin:
            input_file.close()
        """
Updates "index"-file with new info.
        """
        with open("index.txt", "w") as index_file:
            sorti = sorted(self.index_dict.items(), key=operator.itemgetter(1))
            for pair in sorti:
                index_file.write(pair[0]+" "+str(pair[1])+" \n")

        self.lst_files_amount = max(self.lst_files_amount, files_now)

    def update_model(self):
        """
Update our "list"-files with new info stored in dict.
Info consists of words and their frequences.
        """
        index_file = open("index.txt")
        for file_number in range(1, self.lst_files_amount + 1):
            lst_words = [x for x in self.index_dict.keys()
                         if self.index_dict[x] == file_number]

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
                    beg_w = lst[0]
                    if beg_w not in self.frequency:
                        self.frequency[beg_w] = defaultdict(int)
                    words = lst[1].rstrip().split('#')
                    for w in words:
                        if w != '':
                            w_freq = [x for x in w.split()]
                            suc_w = w_freq[0]
                            self.frequency[beg_w][suc_w] += int(w_freq[1])
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
                    for word in self.frequency[first_word]:
                        curr_file.write("#"+word+" ")
                        curr_file.write(str(self.frequency[first_word][word]))
                    curr_file.write(' \n')
                    del self.frequency[first_word]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A trainee program.')
    parser.add_argument("-in", "--input_dir",
                        help="""Input dir path.
                        If not specified, stdin is used.""")
    parser.add_argument("-m", "--model", default=None,
                        help="Received model file path (where to save).")
    parser.add_argument("-nlc", action="store_true",
                        help="""Don't bring texts to lowercase.
                        False by default.""")
    args = parser.parse_args()

    trainer = Trainer()
    trainer.train()
