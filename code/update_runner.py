import os
import re
import time
import subprocess
from datalog import Negated, Equality
from planning.logic import Forall, Or, And, Comparison, Fact, SimpleFExpression, DerivedPredicate, Predicate
from utils.functions import read_predicates, read_unary_predicate
from coherence_update.classes.tbox import TBox
from coherence_update.classes.inclusion import INCLUSION_TYPES_ORDER
from coherence_update.update import CohrenceUpdate
from utils.functions import get_repr
from coherence_update.rules.atomic import build_del_concept_and_incompatible_rules_for_atomic_concepts, build_del_role_and_incompatible_rules_for_roles
from coherence_update.rules.negative import atomicA_closure, roleP_closure
from coherence_update.rules.symbols import COMPATIBLE_UPDATE, INCOMPATIBLE_UPDATE

TMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tmp')
RULES_FILE_NAME = '_update_rules.txt'


class Timer:
    def __init__(self, message = None, end = ",", file = "result.csv", block = False):
        self.message = message
        self.block = block
        self._t = None
        self.end = end
        self.file = file
    def __enter__(self):
        self._t = time.time()
    def __exit__(self, *args, **kwargs):
        elapsed = time.time() - self._t
        with open(self.file, 'a') as f:
            f.write("%.6f" % elapsed + self.end)


class UpdateRunner:
    def __init__(self, nmo_path = "", rls_file_path = "", ontology_file_path="", write_to_file=False, timer_output="result.csv"):
        self.nmo_path = nmo_path
        self.rls_file_path = rls_file_path
        self.write_to_file = write_to_file
        self.ontology_file_path = ontology_file_path
        self.inclusions = None
        self.roles = None
        self.a_atomics = None
        self.functs = None
        self.invFunct = None
        self.timer_output = timer_output
        self.compute_t_closure()

    def run(self):
        tbox = TBox(self.inclusions, roles=self.roles, a_concepts=self.a_atomics, functs=self.functs, functs_inv=self.invFunct)
        rules = CohrenceUpdate.run(tbox)
        if self.write_to_file:
            with open(os.path.join(TMP_DIR, RULES_FILE_NAME), 'w') as f:
                for rule in rules:
                    f.write(rule + '\n')
        return rules

    def run_for_missing_predicates(self, missing_concepts, missing_roles):
        rules = []
        rules.extend(build_del_concept_and_incompatible_rules_for_atomic_concepts(missing_concepts))
        rules.extend(build_del_role_and_incompatible_rules_for_roles(missing_roles))
        for concept in missing_concepts:
            rules.extend(atomicA_closure(concept, [], [], []))
        for role in missing_roles:
            rules.extend(roleP_closure(role, [], [], []))
        return rules

    def compute_t_closure(self):
        if os.path.exists(TMP_DIR):
            subprocess.call(['rm', '-rf', TMP_DIR])

        os.makedirs(TMP_DIR)
        with open(self.rls_file_path, 'r') as f:
            rls = f.read()
            rls = re.sub(r'::DATA_IMPORT_PATH', self.ontology_file_path, rls)
        with open(self.rls_file_path, 'w') as f:
            f.write(rls)

        with Timer("tbox_closure", block=True, file=self.timer_output):
            subprocess.call([self.nmo_path, self.rls_file_path, '--export', 'all', '--export-dir', TMP_DIR], stderr=subprocess.PIPE)
            try:
                self.inclusions = read_predicates(TMP_DIR, INCLUSION_TYPES_ORDER)
                self.roles = read_unary_predicate(TMP_DIR, 'atomicRole')
                self.a_atomics = read_unary_predicate(TMP_DIR, 'atomicConcept')
                self.functs = read_unary_predicate(TMP_DIR, 'funct')
                self.invFunct = read_unary_predicate(TMP_DIR, 'invFunct')
            except FileNotFoundError as e:
                print(e)

        with open(self.rls_file_path, 'r') as f:
            rls = f.read()
            rls = re.sub(self.ontology_file_path, '::DATA_IMPORT_PATH', rls)
        with open(self.rls_file_path, 'w') as f:
            f.write(rls)
        subprocess.call(['rm', '-rf', TMP_DIR])

    def atomic_predicates(self):
        atomic = self.a_atomics + self.roles + self.functs + self.invFunct
        return set([get_repr(uri) for uri in atomic])


def transform_incompatible_update(rules):
    """
        rules: list of Datalog rules
        return: list of filtered Datalog rules, compatible_update
    """
    new_rules = []
    cond = []
    params = set()
    for rule in rules:
        if rule.head.name == INCOMPATIBLE_UPDATE:
            disjuctions = []
            for literal in rule.tail:
                if isinstance(literal, Negated):
                    if isinstance(literal.element, Equality):
                        left_exp = SimpleFExpression(ensure_pddl_parameter(literal.element.left))
                        right_exp = SimpleFExpression(ensure_pddl_parameter(literal.element.right))
                        f = Comparison("=", left_exp, right_exp)
                        neg = f.negate()
                        params.update([f.left.__str__(), f.right.__str__()])
                    else:
                        raise ValueError("Unknown literal type: %r" % literal)
                elif isinstance(literal, Equality):
                    left_exp = SimpleFExpression(ensure_pddl_parameter(literal.left))
                    right_exp = SimpleFExpression(ensure_pddl_parameter(literal.right))
                    f = Comparison("=", left_exp, right_exp)
                    neg = f.negate()
                    params.update([f.left.__str__(), f.right.__str__()])
                else:
                    f = Fact(literal.name, [ensure_pddl_parameter(x) for x in [*literal.parameters]])
                    neg = f.negate()
                    params.update(f.parameters)
                disjuctions.append(neg)
            cond.append(Or(disjuctions))
        else:
            new_rules.append(rule)

    cond = And(cond)
    cond = Forall(params, cond)
    predicate = Predicate(COMPATIBLE_UPDATE, [])
    compatible_update = DerivedPredicate(predicate, cond)

    return new_rules, compatible_update


def ensure_pddl_parameter(parameter):
    if not parameter.startswith("?"):
        return "?" + parameter
    return parameter


if __name__ == '__main__':
    runner = UpdateRunner()
    rules = runner()
