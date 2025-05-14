#!/bin/python3
import math
import random


def generate_planning_problem(obj, prof, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem taskAssigment_problem)
	(:domain taskAssigment)\n"""

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
    planning_domain += "\t(:objects "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    j = math.floor((obj - 2) * 0.6)  # only 60% got assigned
    i = 0
    assig_arr = []
    while i <= j:
        s = random.choice(object_arr)
        object_arr.remove(s)
        assig_arr.append(s)
        i += 1
    #
    assig_arr.sort()
    for x in assig_arr:
        s = random.choice(prof)
        planning_domain += "\t\t(" + s + " " + x + ")\n"

    # ~ Chiudo la parentesi di init
    planning_domain += "\t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (exists (?x ?y) \n \t\t (and \n \t\t\t (mko (and (ElectronicEngineer ?x) (ElectronicEngineer ?y))) \n \t\t\t (not (mko-eq ?x ?y)) \n \t\t ) \n \t ) \n \t)"

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    professions = ["Engineer", "Designer", "Developer"]
    # , "InformaticEngineer", "MaterialsEngineer"] #ElectronicEngineer
    for t in range(3, 23):
        generate_planning_problem(
            t, professions, filename="problems/taskProblem" + str(t) + ".pddl"
        )
