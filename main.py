import argparse
import sys
import os
from algo import *

parser = argparse.ArgumentParser()
parser.add_argument("file", help="parse the input file", type=str)
parser.add_argument("-F", "--forward", help="Solve with forward chaining algorithm", action="store_true", default=False)
parser.add_argument("-v", "--verbose", help="Solve with detailed explanations", action="store_true", default=False)
parser.add_argument("-Q", "--quick", help="Solve without checking all incoherences first", action="store_true", default=False)
parser.add_argument("-f", "--facts", help="The facts that are true at the start of the programm", type=str, default=None)
parser.add_argument("-q", "--query", help="The facts to solve using the knowledge base", type=str, default=None)
args = parser.parse_args()
if not os.path.isfile(args.file):
    sys.stderr.write('Wrong input \n')
    sys.exit(1)
Algo(args.file, args.forward, args.verbose, args.quick, args.facts, args.query)