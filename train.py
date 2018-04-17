import string, re, argparse, sys

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

if args.input_dir:
    input_file = open(args.input_dir)
else:
    input_file = sys.stdin
output_file = open(args.model, 'w')
link = '*start*'
low = '*start*'
chars = re.compile('[\'\w-]+|[А-ЯЁёа-я-]+')

for line in input_file:
    text = [x for x in line.rstrip().split()]
    for word in text:
        low = word
        if not args.nlc:
            low = low.lower()
        if (low == '*end*' and input_file == sys.stdin):
            break
        match = chars.search(low)
        if match:
            output_file.write(link + ' ' + match.group() + '\n')
            link = match.group()
    if (low == '*end*' and input_file == sys.stdin):
        break

if input_file is not sys.stdin:
    input_file.close()
output_file.close()
