import string, numpy, argparse, sys

parser = argparse.ArgumentParser(description='A generator program.')
parser.add_argument("-m", "--model", default="database.txt",
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

def generate_random(begin=""):
    choice = []
    input_file = open(args.model)
    for line in input_file: 
        pair = list(map(str, line.rstrip().split()))
        if (pair[0] == begin):
            choice.append(pair[1])
        elif (begin == ""):
            choice.append(pair[0])
    input_file.close()
    if len(choice) > 0:
        word = numpy.random.choice(choice, 1)[0]
    else:
        word = generate_random()
    return word
         

for i in range(args.length):
    if link != None:
        output_file.write(link + ' ')
    link = generate_random(link)


if output_file is not sys.stdout:
    output_file.close()
