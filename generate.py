"""Program for generating the text using the model.
Has some options; more info in --help."""

import string
import numpy as np
import argparse
import sys
import os


class Generator:
    """
Main class.
    """
    def __init__(self):
        self.output_file = ""
        self.index_dict = dict()
        self.gen_text = []

    def generate(self):
        """
Main function.
        """
        word = self.prepare_args()
        """
Saves into dict our "index"-file for quicker access.
        """
        with open("index.txt") as index_file:
            for line in index_file:
                pair = [x for x in line.split()]
                self.index_dict[pair[0]] = int(pair[1])
        """
Generator cycle. Each step generates one word.
        """
        outcnt = 0
        rand = np.random.randint(2, 11)
        while outcnt < args.length:
            if word in self.index_dict:
                self.gen_text.append(word)
            word = self.generate_random(word)
            """
Prints generated text splitted by strings. Each string has random length
(2-10 words).
            """
            if len(self.gen_text) == rand:
                for i in range(min(rand, args.length - outcnt)):
                    self.output_file.write(self.gen_text[i] + " ")
                self.output_file.write("\n")
                self.gen_text.clear()
                outcnt += rand
                rand = np.random.randint(2, 11)

    def prepare_args(self):
        """
    Works with called args. Returns the first word of generated text.
        """
        if args.output:
            self.output_file = open(args.output, 'w')
        else:
            self.output_file = sys.stdout

        model_dir = os.path.normpath(os.path.join(os.getcwd(), args.model))
        model_dir = os.path.normpath(os.path.join(model_dir, "model"))
        os.chdir(model_dir)

        return args.seed

    def generate_random(self, begin=""):
        """
The most important function. Takes a word, returns generated word.
If it's not possible to generate a word from taken word, returns
random word from "index"-file.
        """
        if begin is None or begin == "" or begin not in self.index_dict:
            out = np.random.choice(list(self.index_dict.keys()), 1)[0]
        else:
            file_number = self.index_dict[begin]
            with open("list"+str(file_number)+".txt") as curr_file:
                """
Parses a string with taken word, it is located in some "list"-file.
                """
                for line in curr_file:
                    pair = [x for x in line.split(':')]
                    if pair[0] == begin:
                        cont_words = pair[1].split('#')
                        """
I use 2 arrays: choice_arr for all possible words for output,
frequency - for their frequences.
Variable "summ" is a sum of all frequences.
                        """
                        freqs = []
                        choice_arr = []
                        summ = 0
                        for pair_word_freq in cont_words:
                            if pair_word_freq != '':
                                pair = [x for x in pair_word_freq.split()]
                                succ_word = pair[0]
                                choice_arr.append(succ_word)
                                freqs.append(float(pair[1]))
                                summ += int(pair[1])
                        """
Normalize the frequences, then generate a random word from choice_arr.
                        """
                        for i in range(len(freqs)):
                            freqs[i] = freqs[i]/summ
                        out = np.random.choice(choice_arr, None, True, freqs)

        return out

    def print_generated(self):
        outcnt = 0
        while outcnt < len(self.gen_text):
            rand = np.random.randint(2, 11)
            for i in range(min(rand, len(self.gen_text) - outcnt)):
                self.output_file.write(self.gen_text[outcnt+i] + " ")
            outcnt += rand
            self.output_file.write("\n")

        if self.output_file is not sys.stdout:
            self.output_file.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A generator program.')
    parser.add_argument("-m", "--model", default="model",
                        help="Input model path.")
    parser.add_argument("-l", "--length", type=int, default=100,
                        help="Length of output text.")
    parser.add_argument("-s", "--seed",
                        help="Start word. Random word by default.")
    parser.add_argument("-out", "--output",
                        help="""Where to print generated text.
                        Standart output by default.""")
    args = parser.parse_args()

    generator = Generator()
    generator.generate()
