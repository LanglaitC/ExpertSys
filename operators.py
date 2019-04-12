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
            result = element.solve()
            if not result or result == None:
                return result
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
        results = []
        for element in self.elements:
            result = element.solve()
            if result == True:
                return True
            results.append(result)
        if not False in results:
            return None
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
            sub_result = element.solve()
            if sub_result == True:
                if not result:
                    result = True
                else:
                    return False
            if sub_result == None:
                return None
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
        result = self.element.solve()
        if result is None:
            return None
        return not result

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
        self.checking = False
        self.initial = False

    def __hash__(self):
        return hash(self.element)

    def __eq__(self, other):
        if isinstance(other, Fact):
            return self.element == other.element
        return False

    def solve(self, to_print=False):
        explanation = ""
        explanation += Colors.OKBLUE + "On tente de resoudre l'élément " + self.element
        to_check = []
        self.check_again = False
        if self.checking:
            explanation += " mais il est deja en train d'etre verifié\n"
            self.status = None
        elif self.initial:
            explanation += ", il est present dans les faits initiaux" +  Colors.ENDC + "\n"
        if self.checked:
            pass
        else:
            self.checking = True
            explanation += Colors.ENDC + "\n\n"
            self.checked = True
            results = []                
            if self in self.facts and self.status:
                results.append(True)
            for key, value in self.kb.items():
                if key == self:
                    for rule in value:
                        status = rule.solve()
                        if status == False:
                            explanation += "\t" + str(rule) + " est evaluée à " + str(status) + ", on ne peut rien en déduire\n"
                        elif status == True:
                            results.append(status)
                            explanation += "\t" + str(rule) + " est evaluée à " + str(status) + " donc l'element peut etre evalué à True\n"
                        else:
                            results.append(status)
                            self.check_again = True
                            explanation += "\t" + str(rule) + " contient une dependance circulaire a l'element, il ne peut pas etre evalué pour le moment\n"
                            to_check.append(rule)
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
                            self.undetermined = True
                            explanation += ", on ne peut rien en deduire\n"
            if (len(results)):
                if True in results and False in results:
                    raise Exception("Incoherence au niveau de l'élément " + self.element + " merci de verifier les regles indiquées")
                elif not True in results and not False in results:
                    self.status = self.check_again
                    self.checked = not self.check_again
                else:
                    self.undetermined = False
                    self.status = True in results
            else:
                self.status = False
        self.checking = False
        if (self.undetermined):
            explanation += "\nDonc l'element " + self.element + " ne peut pas etre determiné"
        elif (self.status == True or self.status == False):
            explanation += "\n" + (Colors.OKGREEN if self.status == True else Colors.FAIL) + self.element + " est " + ("vrai" if self.status else "faux") + Colors.ENDC
        if (self.verbose and to_print):
            print(explanation + "\n")
        for rule in to_check:
            rule.solve()
        # print(self.element, self.status)
        return self.status

    def get_facts(self):
        val = []
        val.append(self)
        return val

    def set_status(self, result, element):
        return [result]

    def __str__(self):
        return self.element
