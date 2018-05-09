"""Program for generating the text using the model.
Has some options; more info in --help."""

import string
import numpy as np
import argparse
import sys
import os


def prepare_args():
    """
Works with called args. Returns the first word of generated text.
    """
    global output_file
    if args.output:
        output_file = open(args.output, 'w')
    else:
        output_file = sys.stdout

    first = args.seed

    model_dir = os.getcwd()
    if args.model == "model":
        model_dir = os.path.join(model_dir, args.model)
    else:
        model_dir = args.model

    os.chdir(model_dir)

    return first


def generate_random(begin=""):
    """
The most important function. Takes a word, returns generated word.
If it's not possible to generate a word from taken word, returns
random word from "index"-file.
    """
    if begin is None or begin == "" or begin not in index_dict:
        out = np.random.choice(list(index_dict.keys()), 1)[0]
    else:
        file_number = index_dict[begin]
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
                    frequency = []
                    choice_arr = []
                    summ = 0
                    for pair_word_freq in cont_words:
                        if pair_word_freq != '':
                            pair = [x for x in pair_word_freq.split()]
                            succ_word = pair[0]
                            choice_arr.append(succ_word)
                            frequency.append(float(pair[1]))
                            summ += int(pair[1])
                    """
Normalize the frequences, then generate a random word from choice_arr.
                    """
                    for i in range(len(frequency)):
                        frequency[i] = frequency[i]/summ
                    out = np.random.choice(choice_arr, None, True, frequency)

    return out


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

    word = prepare_args()

    """
Saves into dict our "index"-file for quicker access.
    """
    index_dict = dict()
    with open("index.txt") as index_file:
        for line in index_file:
            pair = [x for x in line.split()]
            index_dict[pair[0]] = int(pair[1])

    """
Generator cycle. Each step generates one word.
    """
    for i in range(args.length):
        if word is not None:
            output_file.write(word + ' ')
        word = generate_random(word)

    if output_file is not sys.stdout:
        output_file.close()
