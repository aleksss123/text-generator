import string
import numpy as np
import argparse
import sys
import os

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='A generator program.')
    parser.add_argument("-m", "--model", default="\\model",
                        help="Input model path.")
    parser.add_argument("-l", "--length", type=int, default=100,
                        help="Length of output text.")
    parser.add_argument("-s", "--seed",
                        help="Start word. Random word by default.")
    parser.add_argument("-out", "--output",
                        help="""Where to print generated text.
                        Standart output by default.""")
    args = parser.parse_args()

    if args.output:
        output_file = open(args.output, 'w')
    else:
        output_file = sys.stdout

    link = args.seed

    model_dir = os.getcwd()
    if args.model == "\\model":
        model_dir += "\model"
    else:
        model_dir = args.model

    os.chdir(model_dir)

    index_dict = dict()
    with open("index.rtf") as index_file:
        for line in index_file:
            pair = [x for x in line.split()]
            index_dict[pair[0]] = int(pair[1])


def generate_random(begin=""):
    if begin is None or begin == "":
        word = np.random.choice(list(index_dict.keys()), 1)[0]
    else:
        file_number = index_dict[begin]
        with open("list"+str(file_number)+".rtf") as curr_file:
            for line in curr_file:
                pair = [x for x in line.split(':')]
                if pair[0] == begin:
                    words = pair[1].split('#')
                    frequency = []
                    choice_arr = []
                    summ = 0
                    for w in words:
                        if w != '':
                            lst2 = [x for x in w.split()]
                            succ_word = lst2[0]
                            choice_arr.append(succ_word)
                            frequency.append(float(lst2[1]))
                            summ += int(lst2[1])
                    for i in range(len(frequency)):
                        frequency[i] = frequency[i]/summ
                    word = np.random.choice(choice_arr, None, True, frequency)

    return word


if __name__ == "__main__":

    for i in range(args.length):
        if link is not None:
            output_file.write(link + ' ')
        link = generate_random(link)

    if output_file is not sys.stdout:
        output_file.close()
