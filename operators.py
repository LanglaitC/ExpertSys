class Node:
    def __init__(self, facts, verbose, kb):
        self.facts = facts
        self.verbose = verbose
        self.kb = kb
    
    def get_facts(self):
        facts = []
        for element in self.elements:
            facts += element.get_facts()
        return facts

class And(Node):
    def __init__(self, facts, elements, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.elements = elements
        self.operator = "+"

    def solve(self):
        for element in self.elements:
            if not element.solve():
                return False
        return True

    def set_status(self, result):
        return True if result == True else None

    def __str__(self):
        result = "("
        elements = self.get_facts()
        for index, element in enumerate(self.elements):
            result += element.__str__() + (" + " if index != len(self.elements) - 1 else "")
        return result + ")"

class Or(Node):
    def __init__(self, facts, elements, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.elements = elements
        self.operator = "|"

    def solve(self):
        for element in self.elements:
            if element.solve():
                return True
        return False

    def set_status(self, result):
        return False if result == False else None

    def __str__(self):
        result = "("
        elements = self.get_facts()
        for index, element in enumerate(self.elements):
            result += element.__str__() + (" | " if (index != len(self.elements) - 1) else "")
        return result + ")"

class Xor(Node):
    def __init__(self, facts, elements, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.elements = elements
        self.operator = "^"

    def solve(self):
        result = False
        for element in self.elements:
            if element.solve():
                if not result:
                    result = True
                else:
                    return False
        return result

    def __str__(self):
        result = "("
        for index, element in enumerate(self.elements):
            result += element.__str__() + (" ^ " if index != (len(self.elements) - 1) else "")
        return result + ")"

    def set_status(self, result):
        return None

class Not(Node):
    def __init__(self, facts, element, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.element = element
        self.operator = "!"

    def solve(self):
        return not self.element.solve()

    def get_facts(self):
        return self.element.get_facts()

    def get_type(self):
        return self.element.get_type()

    def set_status(self, result):
        return self.element.set_status(not result)

    def __str__(self):
        return "!" + self.element.__str__()

class Fact(Node):
    def __init__(self, facts, element, status, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.element = element
        self.status = status
        self.checked = False
        self.undetermined = False

    def __hash__(self):
        return hash(self.element)

    def __eq__(self, other):
        if isinstance(other, Fact):
            return self.element == other.element
        return False

    def solve(self):
        if self.checked:
            return self.status
        else:
            self.checked = True
            results = []
            for key, value in self.kb.items():
                if key == self:
                    for rule in value:
                        status = rule.solve()
                        if (self.verbose):
                            print(rule)
                        if status != False:
                            results.append(status)
                elif (type(key) != type(self) and self in key.get_facts()):
                    for rule in value:
                        status = rule.solve()
                        if status != False:
                            results.append(key.set_status(status))
        if (len(results)):
            if True in results and False in results:
                raise Exception("Incoherence")
            elif not True in results and not False in results:
                self.status = False
                self.undetermined = True
            else:
                self.status = True in results
        return self.status

    def get_facts(self):
        val = []
        val.append(self)
        return val

    def set_status(self, result):
        return result

    def __str__(self):
        return self.element
