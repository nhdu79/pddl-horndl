#!/bin/python3
import math


def generate_planning_problem(obj, trips, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem Wsmo2VTAT_problem)
	(:domain Wsmo2VTAT)\n"""

    # ~ Genero gli individui in :objects
    object_arr = []
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
        object_arr.append(s)
        j += 1
    #
    # i = 0
    trips_arr = ["iswc_2007"]
    var_arr = ["receipt", "fullTrip"]
    # while i < trips:
    #    s = random.choice(object_arr)
    #    object_arr.remove(s)
    #    var_arr.append(s)
    #    i += 1
    #
    planning_domain += "\t(:objects "
    for x in trips_arr:
        planning_domain += x + " "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    # i = 0
    # while i < trips:
    #    s = random.choice(object_arr)
    #    object_arr.remove(s)
    #    trips_arr.append(s)
    #    i += 1
    #
    for x in trips_arr:
        planning_domain += "\t\t(trip " + x + ")\n\t\t(notFree " + x + ")\n"
    planning_domain += (
        "\t\t(directlyAfterObj " + trips_arr[0] + " " + object_arr[0] + ")\n"
    )
    i = 0
    while i < obj - 1:
        planning_domain += (
            "\t\t(directlyAfterObj " + object_arr[i] + " " + object_arr[i + 1] + ")\n"
        )
        i += 1
    # ~ Chiudo la parentesi di init
    # planning_domain += "\t\t(directlyAfterObj " + trips_arr[0] + " " + object_arr[0] + ")\n"
    # i = 0
    # while i < obj - 1:
    #    planning_domain += "\t\t(directlyAfterObj " + object_arr[i] + " " + object_arr[i+1] + ")\n"
    #    i += 1
    planning_domain += "\t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (exists ("
    for x in var_arr:
        planning_domain += " ?" + x
    # ~ Chiudo la parentesi di init
    planning_domain += ")\n \t\t (mko (and \n"
    i = 0
    while i < len(var_arr) - 1:
        planning_domain += (
            "\t\t\t (invoice "
            + trips_arr[0]
            + " ?"
            + var_arr[i]
            + ")\n \t\t\t (itinerary "
            + trips_arr[0]
            + " ?"
            + var_arr[i + 1]
            + ")\n"
        )
        i += 1
    # ~ Chiudo la parentesi di init
    planning_domain += "\t\t\t ) \n \t\t )) \n \t)\n"

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    trips = 1
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
            t + 10, trips, filename="problems/tripProblem" + str(t) + ".pddl"
        )
