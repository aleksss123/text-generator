import string
import re
import argparse
import sys

parser = argparse.ArgumentParser(description='A trainee program.')
parser.add_argument("-in", "--input_dir",
                    help="""Input file path.
                    If not specified, stdin is used;
                    type then *end* to end the input.""")
parser.add_argument("-m", "--model", default="database.txt",
                    help="Received model file path.")
parser.add_argument("-nlc", action="store_true",
                    help="Don't bring texts to lowercase. False by default.")
args = parser.parse_args()

if (args.input_dir):
    f = open(args.input_dir)
else:
    f = sys.stdin
g = open(args.model, 'w')
link = '*start*'
low = '*start*'
p = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')

for line in f:
    text = [x for x in line.rstrip().split()]
    for word in text:
        low = word
        if (not args.nlc):
            low = low.lower()
        if (low == '*end*' and f == sys.stdin):
            break
        match = p.search(low)
        if (match):
            g.write(link + ' ' + match.group() + '\n')
            link = match.group()
        # maybe will do end-words later
    if (low == '*end*' and f == sys.stdin):
        break

if f is not sys.stdin:
    f.close()
g.close()
