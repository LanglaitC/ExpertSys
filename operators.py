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

    def set_status(self, element, result):
        conclusions = []
        if result == False or result == None:
            return [None]
        else:
            for sub_elmt in self.elements:
                if not element in sub_elmt.get_facts():
                    continue
                conclusions += sub_elmt.set_status(element, result)
        self.check_for_exception(conclusions, element.element)
        if result == True and False in conclusions:
            return [False]
        if result == False and True in conclusions:
            return [True]
        if result == True and None in conclusions:
            return [True]
        return [None]

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

    def set_status(self, element, result):
        conclusions = []
        if result == True or result == None:
            return [None]
        if element == self:
            return [False]
        else:
            for sub_elmt in self.elements:
                if not self in sub_elmt.get_facts():
                    continue
                conclusions += sub_elmt.set_status(element, result)
        self.check_for_exception(conclusions, element.element)
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

    def set_status(self, element, result):
        results = []
        our_results = []
        for index, sub_element in enumerate(self.elements):
            if element in sub_element.get_facts():
                our_results += sub_element.set_status(element, result)
            results += sub_element.set_status(element, result)
        self.check_for_exception(our_results, element)
        if True in results or False in results:
            if result == True and True not in our_results:
                return [False]
            elif result == True and True not in results:
                return [True]
        return [None]

class Not(Node):
    def __init__(self, facts, element, verbose, kb):
        Node.__init__(self, facts, verbose, kb)
        self.element = element
        self.operator = "!"

    def solve(self):
        result = self.element.solve()
        if result is None:
            return True
        return not result

    def get_facts(self):
        return self.element.get_facts()

    def get_type(self):
        return self.element.get_type()

    def set_status(self, element, result):
        result = self.element.set_status(element, not result)
        is_simple = self.element.__class__.__name__ == 'Not' or self.element.__class__.__name__ == 'Fact'
        for index, each in enumerate(result):
            result[index] = not result if each == None and is_simple else None if each == None else not each
        return result

    def __str__(self):
        return "!" + self.element.__str__()

class Fact(Node):
    def __init__(self, facts, element, status, verbose, kb, queries):
        Node.__init__(self, facts, verbose, kb)
        self.element = element
        self.status = status
        self.queries = queries
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

    def solve(self):
        to_print = not self.checked
        explanation = ""
        explanation += Colors.OKBLUE + "On tente de resoudre l'élément " + self.element
        to_check = []
        self.check_again = False
        results = []
        if self.checking:
            self.status = None
        if self.initial:
            self.status = True
            results.append(True)
            explanation += ", il est present dans les faits initiaux" +  Colors.ENDC
        if self.checked:
            pass
        elif not self.checking:
            self.checking = True
            self.checked = True
            explanation += Colors.ENDC + "\n\n"
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
                            to_check.append(rule)
                elif (type(key) != type(self) and self in key.get_facts()):
                    for rule in value:
                        status = rule.solve()
                        explanation += "\tIl est present dans la règle " + str(key) + " qui "
                        if status is None:
                            explanation += "ne peut pas être evalué"
                        else:
                            explanation += "est évalué à " + str(status)
                        if status:
                            conclusion = key.set_status(self, status)
                            results += conclusion
                            if True in conclusion and False in conclusion:
                                raise Exception("Incoherence au niveau de l'élément " + self.element + " merci de verifier les regles indiquées")
                            elif True in conclusion:
                                explanation += ", on peut en deduire que l'element s'evalue a True\n"
                            elif False in conclusion:
                                explanation += ", on peut en deduire que l'element s'evalue a False\n"
                            else:
                                if status == None:
                                    self.check_again = True
                                self.undetermined = True
                                explanation += ", on ne peut rien en deduire\n"
                        else:
                            explanation += ", on ne peut rien en deduire\n"
            if (len(results)):
                if True in results and False in results:
                    raise Exception("Incoherence au niveau de l'élément " + self.element + " merci de verifier les regles indiquées")
                elif not True in results and not False in results:
                    self.status = None
                    self.checked = not self.check_again
                else:
                    self.undetermined = False
                    self.status = True if True in results else False if False in results else None
            else:
                self.status = False
        self.checking = False
        if (self.undetermined):
            explanation += "\nL'element " + self.element + " ne peut pas etre determiné"
        elif (self.status == True or self.status == False):
            explanation += "\n" + (Colors.OKGREEN if self.status == True else Colors.FAIL) + self.element + " est " + ("vrai" if self.status else "faux") + Colors.ENDC
        if (self.verbose and self in self.queries and to_print):
            print(explanation + "\n")
        return self.status

    def get_facts(self):
        val = []
        val.append(self)
        return val

    def set_status(self, element, result):
        return [self.solve()]

    def __str__(self):
        return self.element
