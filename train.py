import string
import re
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='A trainee program.')
parser.add_argument("-in", "--input_dir",
                    help="""Input file path.
                    If not specified, stdin is used;
                    type then *end* to end the input.""")
parser.add_argument("-m", "--model", default=os.getcwd(),
                    help="Received model file path.")
parser.add_argument("-nlc", action="store_true",
                    help="Don't bring texts to lowercase. False by default.")
args = parser.parse_args()

if args.input_dir:
    input_file = open(args.input_dir)
else:
    input_file = sys.stdin

model_dir = "model"
os.chdir(args.model)
if model_dir not in os.listdir():
    os.mkdir(model_dir)
os.chdir(args.model + "\\" + model_dir)

cnt = 1
lst = os.listdir()
if "index.rtf" in lst:
    index_file = open("index.rtf")
    for file in lst:
        if file[0:4] == "list":
            cnt = max(cnt, int(file[4:len(file)-4]))
else:
    with open("index.rtf", "w"), open("tmp1.rtf", "w"):
        pass

link = '*start*'
chars = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')
words_number = 0
index_dict = dict()
with open("index.rtf") as index_file:
    for line in index_file:
        pair = [x for x in line.split()]
        index_dict[pair[0]] = int(pair[1])

for line1 in input_file:
    text = [x for x in line1.rstrip().split()]
    for raw in text:
        word = raw
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
            if link in index_dict:
                file_number = index_dict[link]
            else:
                words_number += 1
                if words_number > 5*cnt:
                    words_number = 1
                    cnt += 1
                    with open("tmp"+str(cnt)+".rtf", "w"):
                        pass
                with open("index.rtf", "a") as index_file:
                    index_file.write(link + " " + str(cnt) + " \n")
                file_number = cnt
                index_dict[link] = file_number

            succ_word = match.group()
            with open("tmp"+str(file_number)+".rtf", "a") as curr_file:
                curr_file.write(link + ":" + succ_word + " \n")
            link = succ_word
    if word == '*end*' and input_file == sys.stdin:
        break

if input_file is not sys.stdin:
    input_file.close()

index_file = open("index.rtf")
frequency = dict()
file_number = 0
for line1 in index_file:
    pair = [x for x in line1.split()]
    link = pair[0]
    if int(pair[1]) > file_number:
        file_number = int(pair[1])
        frequency.clear()
        try:
            base_file = open("list"+str(file_number)+".rtf")
        except IOError as e:
            with open("list"+str(file_number)+".rtf", "w"):
                pass
        else:
            for line in base_file:
                lst = [x for x in line.split(':')]
                first_word = lst[0]
                if first_word not in frequency:
                    frequency[first_word] = dict()
                words = lst[1].split('#')
                for w in words:
                    if w != '':
                        lst2 = [x for x in w.split()]
                        succ_word = lst2[0]
                        frequency[first_word][succ_word] = int(lst2[1])
            base_file.close()
            with open("list"+str(file_number)+".rtf", "w"):
                pass

    try:
        curr_file = open("tmp"+str(file_number)+".rtf")
    except IOError as e:
        pass
    else:
        if link not in frequency:
            frequency[link] = dict()
        for line in curr_file:
            lst = [x for x in line.split(':')]
            if lst[0] == link:
                succ_word = lst[1].rstrip()
                if succ_word in frequency[link]:
                    frequency[link][succ_word] += 1
                else:
                    frequency[link][succ_word] = 1
        curr_file.close()

    with open("list"+str(file_number)+".rtf", "a") as curr_file:
        curr_file.write(link + ":")
        for word in frequency[link]:
            curr_file.write("#" + word + " " + str(frequency[link][word]))
        curr_file.write(' \n')

for n in range(1, file_number + 1):
    try:
        curr_file = open("tmp"+str(n)+".rtf")
    except IOError as e:
        pass
    else:
        curr_file.close()
        os.remove("tmp"+str(n)+".rtf")
