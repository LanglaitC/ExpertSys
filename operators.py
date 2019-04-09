class Node:
    def __init__(self, facts):
        self.facts = facts
    
    def get_facts(self):
        facts = []
        for element in self.elements:
            facts += element.get_facts()
        return facts

class And(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self, kb):
        for element in self.elements:
            if not element.solve(kb):
                return False
        return True

    def set_status(self, result):
        return True if result == True else None

class Or(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self, kb):
        for element in self.elements:
            if element.solve(kb):
                return True
        return False

    def set_status(self, result):
        return False if result == False else None

class Xor(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self, kb):
        result = False
        for element in self.elements:
            if element.solve(kb):
                if not result:
                    result = True
                else:
                    return False
        return result

    def set_status(self, result):
        return None

class Not(Node):
    def __init__(self, facts, element):
        Node.__init__(self, facts)
        self.element = element

    def solve(self, kb):
        return not self.element.solve(kb)

    def get_facts(self):
        return self.element.get_facts()

    def get_type(self):
        return self.element.get_type()

    def set_status(self, result):
        return self.element.set_status(not result)

class Fact(Node):
    def __init__(self, facts, element, status):
        Node.__init__(self, facts)
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

    def solve(self, kb):
        if self.checked:
            return self.status
        else:
            results = []
            for key, value in kb.items():
                if key == self:
                    for rule in value:
                        status = rule.solve(kb)
                        if status != False:
                            results.append(status)
                elif (type(key) != type(self) and self in key.get_facts()):
                    for rule in value:
                        status = rule.solve(kb)
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
        self.checked = True
        return self.status

    def get_facts(self):
        val = []
        val.append(self)
        return val

    def set_status(self, result):
        return result
