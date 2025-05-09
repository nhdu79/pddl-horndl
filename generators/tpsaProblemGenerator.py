#!/bin/python3
import math
import random
from itertools import product


def generate_planning_problem(obj, services, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem Wsmo2TPSA_problem)
	(:domain Wsmo2TPSA)\n"""

    # ~ Genero gli individui in :objects
    object_arr = ["voipRequest", "voip"]
    j = 0
    dig = math.floor(math.log(obj * 2, 26))
    while j < obj:
        s = ""
        i = dig
        tr = j
        while i >= 0:
            num = math.trunc(tr / (26**i))
            s += chr(ord("a") + num)
            tr -= num * (26**i)
            i -= 1
        if s != "x":
            object_arr.append(s)
        j += 1
    #
    i = 0
    var_arr = ["x"]
    # while i < trips:
    #    s = random.choice(object_arr)
    #    object_arr.remove(s)
    #    var_arr.append(s)
    #    i += 1
    #
    planning_domain += "\t(:objects "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    # i = 0
    # trips_arr = []
    # while i < trips:
    #    s = random.choice(object_arr)
    #    object_arr.remove(s)
    #    trips_arr.append(s)
    #    i += 1
    #
    # for x in trips_arr:
    #    planning_domain += "\t\t(trip " + x + ")\n"
    # ~ Chiudo la parentesi di init
    # planning_domain += "\t)\n"
    planning_domain += "\t\t(requestedService voipRequest voip) \n \t\t (service voip)\n \t\t (order voipRequest) \n \t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (exists ("
    for x in var_arr:
        planning_domain += "?" + x
    # ~ Chiudo la parentesi di init
    planning_domain += ")\n \t\t (mko "  # " (and \n"
    for x in var_arr:
        planning_domain += "(invoice ?" + x + ")\n"
    # ~ Chiudo la parentesi di init
    planning_domain += "\t\t ) \n\t\t) \n \t)\n"  # )

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    services = 1
    for t in [
        4,
        5,
        6,
        7,
        10,
        15,
        20,
        25,
        30,
        35,
        40,
        45,
        50,
        55,
        60,
    ]:  # ,70,80,90,100]:
        generate_planning_problem(
            t + 3, services, filename="problems/orderProblem" + str(t) + ".pddl"
        )
