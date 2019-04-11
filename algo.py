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
    def __init__(self, input_file, forward, verbose, fast):
        self.forward = forward
        self.verbose = verbose
        self.facts = []
        self.queries = []
        self.parse(input_file)
        if not fast:
            self.check_incoherences()
        for query in self.queries:
            self.solve(query)
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
                return self.parse_facts(content[index:])
            elif line[0] == FACT_CHAR:
                return self.parse_facts(content[index:])
            else:
                #TODO Deal with equivalence <=>
                jump = True
                splited = re.compile('<?=>').split(line)
                if (len(splited) != 2):
                    raise Exception()
                key = self.parse_rules(splited[1].split(COMMENT_CHAR)[0])
                val = self.parse_rules(splited[0].split(COMMENT_CHAR)[0])
                if key in self.kb:
                    self.kb[key].append(val)
                else:
                    values = []
                    values.append(val)
                    self.kb[key] = values
        raise Exception()

    def parse_facts(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or (line != '' and line[0] == COMMENT_CHAR):
                continue
            elif line[0] == FACT_CHAR:
                space = False
                for char in line[1:]:
                    if char == COMMENT_CHAR:
                        break
                    if char == ' ':
                        space = True
                        continue
                    if char != COMMENT_CHAR and space == True and char != ' ':
                        raise Exception()
                    fact = Fact(self.facts, char, True)
                    if fact in self.facts:
                        sub_index = self.facts.index(fact)
                        self.facts[sub_index].checked = True
                        self.facts[sub_index].status = True
                    else:
                        fact.checked = True
                        self.facts.append(fact)
                return self.parse_queries(content[index + 1:])
            else:
                raise Exception()
        raise Exception()

    def parse_queries(self, content):
        jump = None
        query = False
        for line in content:
            line = line.strip()
            if line == '' or line[0] == COMMENT_CHAR:
                continue
            elif line[0] == QUERY_CHAR:
                space = False
                for char in line[1:]:
                    if char == COMMENT_CHAR:
                        break
                    if char == ' ':
                        space = True
                        continue
                    if char != COMMENT_CHAR and space == True and char != ' ':
                        raise Exception()
                    fact = Fact(self.facts, char, False)
                    if fact in self.facts:
                        self.queries.append(self.facts[self.facts.index(fact)])
                    else:
                        self.facts.append(fact)
                        self.queries.append(fact)
                query = True
            else:
                raise Exception()
        if not query:
            raise Exception()

    def parse_rules(self, term):
        result = None
        tmp = []
        not_op = False
        operator = None
        priority = False
        i = 0
        while i < len(term):
            char = term[i]
            if char.isspace():
                pass
            elif char == '(':
                opened = i
                count = 0
                while i < len(term):
                    if term[i] == '(':
                        count += 1
                    if term[i] ==')':
                        count -= 1
                        if count == 0:
                            tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, self.parse_rules(term[opened + 1:i])) if not_op else self.parse_rules(term[opened + 1:i]))
                            not_op = False
                            break
                    i+= 1
                if count != 0:
                    raise Exception()
            elif char in OPERATORS:
                if char == operator:
                    pass
                elif char == NOT_OPERATOR:
                    not_op = True
                elif operator == None:
                    operator = char
                else:
                    if priority == False:
                        result = OPERATORS_FUNC[operator](self.facts, tmp)
                        tmp = []
                        tmp.append(result)
                        priority = OPERATORS.index(char) < OPERATORS.index(operator) and not_op == False 
                    else:
                        parent = result
                        elem = result.elements[-1]
                        while elem.__class__.__name__ != 'Fact':
                            parent = elem
                            elem = elem.elements[-1]
                        parent.elements[-1] = OPERATORS_FUNC[operator](self.facts, tmp)
                        tmp = []
                    operator = char
            elif char in POSSIBLE_FACTS:
                fact = Fact(self.facts, char, False)
                if fact in self.facts:
                    fact = self.facts[self.facts.index(fact)]
                else:
                    self.facts.append(fact)
                tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, fact) if not_op else fact)
                not_op = False
            else:
                raise Exception()
            i += 1
        if operator is None:
            if len(tmp):
                result = tmp[0]
            else:
                raise Exception()
        else:
            if priority == False:
                result = OPERATORS_FUNC[operator](self.facts, tmp)
            else:
                parent = result
                elem = result.elements[-1]
                while elem.__class__.__name__ != 'Fact':
                    parent = elem
                    elem = elem.elements[-1]
                node = elem
                # node = tmp[0].elements[-1]
                tab = list(tmp)
                tab[0] = node
                parent.elements[-1] = OPERATORS_FUNC[operator](self.facts, tab)
        return result

    def check_incoherences(self):
        for fact in self.facts:
            fact.solve(self.kb)

    def solve(self, fact):
        fact.solve(self.kb)
        if (fact.undetermined):
            print(fact.element + " is Undetermined")
        else:
            print(fact.element + " is " + str(fact.status))
