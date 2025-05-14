#!/bin/python3
import math
import random


def generate_planning_problem(obj, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem elevators_problem)
	(:domain elevators)\n"""

    # ~ Genero gli individui in :objects
    object_arr = []
    j = 0
    dig = math.floor(math.log(obj, 26))
    while j < obj:
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
    passNum = math.floor(obj * 0.4)  # only 40% are passenders
    j = 0
    pass_arr = []
    while j < passNum:
        s = random.choice(object_arr)
        object_arr.remove(s)
        pass_arr.append("pass_" + s)
        j += 1
    #
    planning_domain += "\t(:objects "
    for x in pass_arr:
        planning_domain += x + " "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    for x in pass_arr:
        s = random.choice(object_arr)
        planning_domain += "\t\t(origin " + x + " " + s + ")\n"
        s = random.choice(object_arr)
        planning_domain += "\t\t(destin " + x + " " + s + ")\n"
    x = 0
    while x < len(object_arr) - 1:
        planning_domain += (
            "\t\t(next " + object_arr[x] + " " + object_arr[x + 1] + ")\n"
        )
        x += 1
    s = random.choice(object_arr)
    planning_domain += "\t\t(lift_at " + s + ")\n"

    # ~ Chiudo la parentesi di init
    planning_domain += "\t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (not (exists (?x) \n \t\t (and \n \t\t\t (mko (passenger ?x)) \n \t\t\t (not (mko (served ?x))) \n \t\t )) \n \t ))"

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    for t in range(15, 35):
        generate_planning_problem(
            t, filename="problems/elevatorProblem" + str(t) + ".pddl"
        )
