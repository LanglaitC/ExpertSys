class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

    def check_for_exception(self, tab, element):
        if True in tab and False in tab:
            raise Exception("Incoherence au niveau de l'élément " + element + " merci de verifier les regles indiquées")

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

    def set_status(self, result, element):
        conclusions = []
        if result == False:
            return [None]
        if element == self:
            return [True]
        else:
            for sub_elmt in self.elements:
                if not element in sub_elmt.get_facts():
                    continue
                conclusions += sub_elmt.set_status(result, element)
        self.check_for_exception(conclusions, element.element)
        for index, each in enumerate(conclusions):
            conclusions[index] = None if each == False else True
        return conclusions

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

    def set_status(self, result, element):
        conclusions = []
        if result == True:
            return [None]
        if element == self:
            return [False]
        else:
            for sub_elmt in self.elements:
                if not self in sub_elmt.get_facts():
                    continue
                conclusions += sub_elmt.set_status(result, element)
        self.check_for_exception(conclusions, element.element)
        for index, each in enumerate(conclusions):
            conclusions[index] = False if each == False else None
        return conclusions


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

    def set_status(self, result, element):
        return [None]

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

    def set_status(self, result, element):
        return self.element.set_status(not result, element)

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

    def solve(self, to_print=False):
        explanation = ""
        explanation += Colors.OKBLUE + "On tente de resoudre l'élément " + self.element
        if self.checked:
            explanation += ", il est present dans les faits initiaux" +  Colors.ENDC + "\n"
        else:
            explanation += Colors.ENDC + "\n\n"
            self.checked = True
            results = []                
            if self in self.facts and self.status:
                explanation  += "\tIl est present dans les faits initiaux, il est donc evalue a True\n"
                results.append(True)
            for key, value in self.kb.items():
                if key == self:
                    for rule in value:
                        status = rule.solve()
                        explanation += "\t" + str(rule) + " est evaluée à " + str(status) + " donc l'element peut etre evalué à True\n"
                        if status != False:
                            results.append(status)
                elif (type(key) != type(self) and self in key.get_facts()):
                    for rule in value:
                        status = rule.solve()
                        explanation += "\tIl est present dans la règle " + str(key) + " qui est evalué à " + str(status)
                        conclusion = key.set_status(status, self)
                        results += conclusion
                        if True in conclusion and False in conclusion:
                            raise Exception("Incoherence au niveau de l'élément " + self.element + " merci de verifier les regles indiquées")
                        elif True in conclusion:
                            explanation += ", on peut en deduire que l'element s'evalue a True\n"
                        elif False in conclusion:
                            explanation += ", on peut en deduire que l'element s'evalue a False\n"
                        else:
                            explanation += ", on ne peut rien en deduire\n"
            if (len(results)):
                if True in results and False in results:
                    raise Exception("Incoherence au niveau de l'élément " + self.element + " merci de verifier les regles indiquées")
                elif not True in results and not False in results:
                    self.status = False
                    self.undetermined = True
                else:
                    self.status = True in results
        if (self.undetermined):
            explanation += "\nDonc l'element " + self.element + " ne peut pas etre determiné"
        else:
            explanation += "\n" + (Colors.OKGREEN if self.status == True else Colors.FAIL) + self.element + " est " + ("vrai" if self.status else "faux") + Colors.ENDC
        if (self.verbose and to_print):
            print(explanation + "\n")
        return self.status

    def get_facts(self):
        val = []
        val.append(self)
        return val

    def set_status(self, result, element):
        return [result]

    def __str__(self):
        return self.element
