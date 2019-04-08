class Node:
    def __init__(self, facts):
        self.facts = facts
    
    def get_facts(self):
        facts = []
        for element in self.elements:
            facts.append(element.get_facts())
        return facts

class And(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self):
        for element in self.elements:
            if not element.solve():
                return False
        return True

class Or(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self):
        for element in self.elements:
            if element.solve():
                return True
        return False

class Xor(Node):
    def __init__(self, facts, elements):
        Node.__init__(self, facts)
        self.elements = elements

    def solve(self):
        result = False
        for element in self.elements:
            if element.solve():
                if not result:
                    result = True
                else:
                    return False
        return result

class Not(Node):
    def __init__(self, facts, element):
        Node.__init__(self, facts)
        self.element = element

    def solve(self):
        return not element.solve()

class Fact(Node):
    def __init__(self, facts, element):
        Node.__init__(self, facts)
        self.element = element

    def solve(self):
        return self.facts[element]

    def get_facts(self):
        return self.element