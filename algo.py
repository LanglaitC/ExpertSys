import re
import sys
import math
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
    def __init__(self, input_file, verbose, fast, facts, query):
        try:
            self.verbose = verbose
            self.fast = fast
            self.fact_asked = facts
            self.query_asked = query
            self.facts = []
            self.queries = []
            self.parse(input_file)
            if self.fact_asked != None:
                self.check_line_validity(self.fact_asked)
                self.parse_facts_line(self.fact_asked)
            if self.query_asked != None:
                self.check_line_validity(self.query_asked)
                self.parse_queries_line(self.query_asked)
            if not fast:
                self.check_incoherences()
            for query in self.queries:
                self.solve(query)
        except Exception as e:
            length = len(e.__str__())
            sys.stderr.write(Colors.FAIL + "\n")
            for i in range(math.ceil(length / 2) - 18):
                sys.stderr.write('-')
            sys.stderr.write(" /!\\ WARNING: MISTAKES HAVE BEEN MADE /!\\ ")
            sys.stderr.write(Colors.FAIL)
            for i in range(math.ceil(length / 2) - 17):
                sys.stderr.write('-')
            sys.stderr.write('\n')
            sys.stderr.write("\n  " + Colors.ENDC + e.__str__() + Colors.FAIL + "\n\n")
            for i in range(length + 8):
                sys.stderr.write('-')
            sys.stderr.write("\n" + Colors.ENDC)

    def parse(self, input_file):
        self.kb ={}
        with open(input_file, 'r') as fd:
            content = fd.read().split('\n')
        try:
            self.parse_clauses(content)
        except Exception as e:
            raise(e)
            sys.stderr.write('Parsing error\n')
            exit
            
    def parse_clauses(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or (line != '' and line[0] == COMMENT_CHAR):
                continue
            if (line == '' and jump == True):
                return self.parse_facts(content[index:])
            elif line[0] == FACT_CHAR:
                if not len(self.kb):
                    raise Exception("Aucune regle defini")
                return self.parse_facts(content[index:])
            else:
                jump = True
                splited = re.compile('(<?=>)').split(line)
                if (len(splited) != 3):
                    raise Exception("Regle invalide: " + line)
                key = self.parse_rules(splited[2].split(COMMENT_CHAR)[0])
                val = self.parse_rules(splited[0].split(COMMENT_CHAR)[0])
                self.add_to_kb(key, val)
                if (splited[1] == "<=>"):
                    self.add_to_kb(val, key)
        raise Exception()

    def add_to_kb(self, key, val):
        if key in self.kb:
            self.kb[key].append(val)
        else:
            values = []
            values.append(val)
            self.kb[key] = values

    def parse_facts(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or (line != '' and line[0] == COMMENT_CHAR):
                continue
            elif line[0] == FACT_CHAR:
                self.check_line_validity(line[1:])
                if self.fact_asked == None:
                    self.parse_facts_line(line[1:])
                return self.parse_queries(content[index + 1:])
            else:
                if self.fact_asked == None:
                    raise Exception("Le caractere introduisant les faits n'a pas ete rencontré et aucun fait n'a été indique en parametres")
                return self.parse_queries(content[index:])

    def check_line_validity(self, line, fact=True):
        space = False
        for char in line:
            if char == COMMENT_CHAR:
                break
            if char == ' ':
                space = True
                continue
            if char != COMMENT_CHAR and space == True and char != ' ':
                raise Exception("Charactere invalide" + char)
            if fact and char not in POSSIBLE_FACTS:
                raise Exception(char + " n'est pas un charactere valide, les faits devraient etre des lettres de l'alphabet majuscules")

    def parse_facts_line(self, line):
        for char in line:
            if char not in POSSIBLE_FACTS:
                break
            fact = Fact(self.facts, char, True, self.verbose, self.kb, self.queries)
            if fact in self.facts:
                sub_index = self.facts.index(fact)
                self.facts[sub_index].checked = self.fast
                self.facts[sub_index].status = True
                self.facts[sub_index].initial = True
            else:
                fact.initial = True
                fact.checked = self.fast
                self.facts.append(fact)

    def parse_queries_line(self, line):
        for char in line:
            if char not in POSSIBLE_FACTS:
                break
            fact = Fact(self.facts, char, False, self.verbose, self.kb, self.queries)
            if fact in self.facts:
                self.queries.append(self.facts[self.facts.index(fact)])
            else:
                self.facts.append(fact)
                self.queries.append(fact)

    def parse_queries(self, content):
        jump = None
        query = False
        for line in content:
            line = line.strip()
            if line == '' or line[0] == COMMENT_CHAR:
                continue
            elif line[0] == QUERY_CHAR and not query:
                self.check_line_validity(line[1:])
                if self.query_asked == None:
                    self.parse_queries_line(line[1:])
                    query = True
            else:
                raise Exception("Charactère(s) invalide au niveau des queries: " + line)
        if not query and self.query_asked == False:
            raise Exception("Aucune querie valide n'a été saisie")

    def parse_rules(self, term):
        result = None
        tmp = []
        not_op = 0
        operator = None
        priority = False
        last_op = 0
        last_fact = 0
        i = 0
        while i < len(term):
            char = term[i]
            if char.isspace():
                pass
            elif char == '(':
                last_fact = i
                opened = i
                count = 0
                while i < len(term):
                    if term[i] == '(':
                        count += 1
                    if term[i] ==')':
                        count -= 1
                        if count == 0:
                            tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, self.parse_rules(term[opened + 1:i]), self.verbose, self.kb) if not_op % 2 else self.parse_rules(term[opened + 1:i]))
                            not_op = 0
                            break
                    i+= 1
                if count != 0:
                    raise Exception("Incoherence au niveau des parentheses d'une regle: " + term)
            elif char in OPERATORS:
                last_op = i
                j = i + 1
                parentheses = 0
                while (j < len(term) and term[j] not in OPERATORS) or (j < len(term) and parentheses != 0):
                    if (term[j] in "()"):
                        parentheses += 1 if term[j] == "(" else -1
                    j += 1
                priority = j < len(term) and term[j] in OPERATORS and OPERATORS.index(term[j]) < OPERATORS.index(char)
                if char == operator:
                    pass
                elif char == NOT_OPERATOR:                  
                    not_op += 1
                elif operator == None:
                    operator = char
                else:
                    result = OPERATORS_FUNC[operator](self.facts, tmp, self.verbose, self.kb)
                    tmp = []
                    tmp.append(result)
                    operator = char
            elif char in POSSIBLE_FACTS:
                last_fact = i
                if priority == True:
                    start = i
                    parentheses = 0
                    while i < len(term):
                        if (term[i] in "()"):
                            parentheses += 1 if term[i] == "(" else -1
                        if term[i] in OPERATORS and OPERATORS.index(term[i]) >= OPERATORS.index(operator) and parentheses == 0:
                            break
                        i += 1
                    tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, self.parse_rules(term[start:i]), self.verbose, self.kb) if not_op % 2 else self.parse_rules(term[start:i]))
                    not_op = 0
                    i -= 1
                    priority = False
                else:
                    fact = Fact(self.facts, char, False, self.verbose, self.kb, self.queries)
                    if fact in self.facts:
                        fact = self.facts[self.facts.index(fact)]
                    else:
                        self.facts.append(fact)
                    tmp.append(OPERATORS_FUNC[NOT_OPERATOR](self.facts, fact, self.verbose, self.kb) if not_op % 2 else fact)
                    not_op = 0
            else:
                raise Exception("Charactère invalide au sein de l'une des regles: " + char + ", " + term)
            i += 1
        if last_op > last_fact:
            raise Exception("Un opérateur doit etre suivi d'un fait valide ou de parentheses contenant un autre operateur valide")
        if operator is None:
            if len(tmp):
                result = tmp[0]
            else:
                raise Exception("Erreur de syntaxe")
        else:
            if result and OPERATORS.index(operator) < OPERATORS.index(result.operator):
                result.elements[-1] = (OPERATORS_FUNC[operator](self.facts, [result.elements[-1]] + tmp[1:], self.verbose, self.kb))
            else:
                result = OPERATORS_FUNC[operator](self.facts, tmp, self.verbose, self.kb)
        return result

    def check_incoherences(self):
        for fact in self.facts:
            fact.solve()

    def solve(self, fact):
        fact.solve()
        if (not self.verbose):
            if (fact.undetermined or fact.status == None):
                print(fact.element + " is Undetermined")
            else:
                print((Colors.OKGREEN if fact.status == True else Colors.FAIL) + fact.element + " is " + str(fact.status) + Colors.ENDC)

    def find_end_of_term(self, term, start, operator):
        i = start
        while i < len(term):
            if term[i] in OPERATORS and OPERATORS.index(term[i]) >= OPERATORS.index(operator):
                break
            i += 1
        return i
