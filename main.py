import argparse
import sys
import os
from algo import *

parser = argparse.ArgumentParser()
parser.add_argument("file", help="parse the input file", type=str)
parser.add_argument("-f", "--forward", help="Solve with forward chaining algorithm", action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="Solve with detailed explanations", action="store_true", default=False)
parser.add_argument("-q", "--quick", help="Solve without checking all incoherences first", action="store_true", default=False)
args = parser.parse_args()
if not os.path.isfile(args.file):
    sys.stderr.write('Wrong input \n')
    exit
print(args)
Algo(args.file, args.forward, args.verbose, args.quick)