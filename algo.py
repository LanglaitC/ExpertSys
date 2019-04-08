import re
import sys
from operators import *

COMMENT_CHAR = '#'
FACT_CHAR = '='
QUERY_CHAR = '?'
NOT_OPERATOR = '!'
OR_OPERATOR = '|'
AND_OPERATOR = '+'
XOR_OPERATOR = '^'
OPERATORS = [NOT_OPERATOR, AND_OPERATOR, OR_OPERATOR, XOR_OPERATOR]
OPERATORS_FUNC = {
    NOT_OPERATOR: Not,
    AND_OPERATOR: And,
    OR_OPERATOR: Or,
    XOR_OPERATOR: Xor
}
POSSIBLE_FACTS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class Algo:
    def __init__(self, input_file, forward, verbose):
        self.forward = forward
        self.verbose = verbose
        self.facts = {}
        self.queries = []
        self.parse(input_file)
        return

    def parse(self, input_file):
        self.kb ={}
        with open(input_file, 'r') as fd:
            content = fd.read().split('\n')
        try:
            self.parse_clauses(content)
        except Exception as e:
            raise(e)
            sys.stderr.write('Parsing error \n')
            exit
        print(len(self.kb))

            
    def parse_clauses(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or (line != '' and line[0] == COMMENT_CHAR):
                continue
            if (line == '' and jump == True):
                return self.parse_facts(content)
            elif line[0] == FACT_CHAR:
                return parse_facts(content[index:])
            else:
                #TODO Deal with equivalence <=>
                jump = True
                splited = re.compile('<?=>').split(line)
                if (len(splited) != 2):
                    Exception()
                self.kb[self.parse_rules(splited[1].split(COMMENT_CHAR)[0])] = self.parse_rules(splited[0].split(COMMENT_CHAR)[0])
        Exception()

    def parse_facts(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or (line != '' and line[0] == COMMENT_CHAR):
                continue
            elif line[0] == FACT_CHAR:
                for char in line[1:]:
                    if char == COMMENT_CHAR or char == ' ':
                        break
                    self.facts[char] = True
                return self.parse_queries(content[index + 1:])
            else:
                Exception()
        Exception()

    def parse_queries(self, content):
        jump = None
        query = False
        for line in content:
            line = line.strip()
            if line == '' or line[0] == COMMENT_CHAR:
                continue
            elif line[0] == QUERY_CHAR:
                for char in line[1:]:
                    if char == COMMENT_CHAR or char == ' ':
                        break
                    self.queries.append(char)
                query = True
            else:
                Exception()
        if not query:
            Exception()

    def parse_rules(self, term):
        result = None
        tmp = []
        not_op = False
        operator = None
        i = 0
        while i < len(term):
            char = term[i]
            i += 1
            if char.isspace():
                continue
            elif char == '(':
                opened = i - 1
                i = term.rindex(')') + 1
                tmp.append(self.parse_rules(term[opened + 1:i - 2]))
            elif char in OPERATORS:
                if char == operator:
                    continue
                elif char == NOT_OPERATOR:
                    not_op = True
                elif operator == None:
                    operator = char
                else:
                    result = OPERATORS_FUNC[operator](self.facts, tmp)
                    tmp = []
                    tmp.append(result)
                    operator = char
            elif char in POSSIBLE_FACTS:
                tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, Fact(self.facts, char)) if not_op else Fact(self.facts, char))
            else:
                Exception()
        if operator is None:
            if len(tmp):
                result = tmp[0]
            else:
                Exception()
        else:
            result = OPERATORS_FUNC[operator](self.facts, tmp)
        return result