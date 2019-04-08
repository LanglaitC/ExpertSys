import re

COMMENT_CHAR = '#'
FACT_CHAR = '='
QUERY_CHAR = '?'
OPERATORS = ['(', '']

class Algo:
    def __init__(self, input_file, forward, verbose):
        self.forward = forward
        self.verbose = verbose
        self.parse(input_file)
        self.facts = {}
        self.queries = []
        return

    def parse(self, input_file):
        self.kb ={}
        with open(input_file, 'r') as fd:
            content = fd.read.split('\n')
        try:
            self.parse_clauses(content)
        except Exception as e:
            sys.stderr.write('Parsing error \n')
            exit

            
    def parse_clauses(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or line[0] == COMMENT_CHAR:
                continue
            if (line == '' and jump = True)
                return self.parse_facts(content)
            elif line[0] == FACT_CHAR:
                return parse_facts(content[index:])
            else:
                #TODO Deal with equivalence <=>
                jump = True
                splited = re.compile('<?=>').match(line)
                if (splited.length !== 2):
                    Exception()
                self.parse_rules(splited[1].split(COMMENT_CHAR)[0])
        Exception()

    def parse_facts(self, content):
        jump = None
        for index, line in enumerate(content):
            line = line.strip()
            if (line == '' and jump == None) or line[0] == COMMENT_CHAR:
                continue
            elif line[0] == FACT_CHAR:
                for char in line[1:]:
                    if char == COMMENT_CHAR:
                        break
                    self.facts[char] = True
                return parse_queries(content[index + 1:])
            else
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
                    if char == COMMENT_CHAR:
                        break
                    self.queries.append(char)
                query = True
            else
                Exception()
        if not query
            Exception()

    def parse_rules(self, line):
        return ""