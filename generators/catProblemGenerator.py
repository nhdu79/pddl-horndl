#!/bin/python3
import math
import random


def generate_planning_problem(obj, bomb_perc, cat_perc, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem BTcat_problem)
	(:domain BTcat)\n"""

    # ~ Genero gli individui in :objects
    object_arr = []
    j = 0
    dig = math.floor(math.log(obj * 2, 26))
    while j < obj * 2:
        s = ""
        i = dig
        tr = j
        while i >= 0:
            num = math.trunc(tr / (26**i))
            s += chr(ord("a") + num)
            tr -= num * (26**i)
            i -= 1
        object_arr.append(s)
        j += 1
    planning_domain += "\t(:objects "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    j = math.floor(obj * bomb_perc)  # cats + #bombs = #packages
    i = 0
    package_arr = []
    bomb_arr = []
    contains_arr = []
    while i < j:
        s = random.choice(object_arr)
        object_arr.remove(s)
        package_arr.append(s)
        sb = random.choice(object_arr)
        object_arr.remove(sb)
        bomb_arr.append(sb)
        contains_arr.append("contains " + str(s) + " " + str(sb))
        i += 1
    #
    j = math.floor(obj * cat_perc)
    i = 0
    cat_arr = []
    while i < j:
        s = random.choice(object_arr)
        object_arr.remove(s)
        package_arr.append(s)
        sb = random.choice(object_arr)
        object_arr.remove(sb)
        cat_arr.append(sb)
        contains_arr.append("contains " + str(s) + " " + str(sb))
        i += 1
    #
    object_arr = []
    object_arr.extend(package_arr)
    object_arr.extend(cat_arr)
    object_arr.extend(bomb_arr)
    object_arr.sort()
    for x in object_arr:
        try:
            i = cat_arr.index(x)
            planning_domain += "\t\t(cat " + x + ")\n"
        except ValueError:
            try:
                i = bomb_arr.index(x)
                planning_domain += "\t\t(bomb " + x + ")\n"
            except ValueError:
                {}

    for x in contains_arr:
        planning_domain += "\t\t(" + x + ")\n"
    # ~ Chiudo la parentesi di init
    planning_domain += "\t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (not (exists (?x) \n \t\t (and \n \t\t\t (mko (package ?x)) \n \t\t\t (not (mko (disarmed ?x))) \n \t\t ) \n \t )) \n \t)\n"

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    bomb_perc = 0.3
    cat_perc = 1 - 0.1 - bomb_perc
    for t in [
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
    ]:
        generate_planning_problem(
            t, bomb_perc, cat_perc, filename="problems/catProblem" + str(t) + ".pddl"
        )
