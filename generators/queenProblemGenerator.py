#!/bin/python3
import random


def inline(t, queen_arr):
    for x in queen_arr:
        if x[0] == t[0] or x[1] == t[1]:
            if (abs(ord(x[0]) - ord(t[0])) < 2) and (abs(ord(x[1]) - ord(t[1])) < 2):
                return True
    return False


def generate_planning_problem(board_size, queen_number, filename):

    # ~ Inizializzo il problema di planning
    planning_domain = """(define (problem queen_problem)
	(:domain queens)\n"""

    # ~ Genero gli individui in :objects
    object_arr = []
    j = 0
    i = 0
    # dig = math.floor(math.log(pow(board_size,2),26))
    # while j < pow(board_size,2):
    # s = ""
    # i = dig
    # tr = j
    # while i >= 0:
    # num = math.trunc(tr/(26**i))
    # s += chr(ord('a') + num)
    # tr -= num*(26**i)
    # i -= 1
    # object_arr.append(s)
    # j += 1
    while i < board_size:
        while j < board_size:
            s = chr(ord("a") + i) + chr(ord("a") + j)
            object_arr.append(s)
            j += 1
        i += 1
        j = 0
    planning_domain += "\t(:objects "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += ")\n"
    #
    # ~ Definisco :init
    planning_domain += "\t(:init\n"

    board_arr = list(object_arr)
    pic = ["-"] * pow(board_size, 2)
    queen_arr = []
    i = 0
    while i < queen_number:
        s = random.choice(object_arr)
        object_arr.remove(s)
        queen_arr.append(s)
        i += 1
    #
    for s in queen_arr:
        planning_domain += "\t\t(Queen " + s + ")\n"
        ind = board_arr.index(s)
        pic[ind] = "q"
    #
    for i in range(board_size):
        print(pic[i * board_size : (i + 1) * board_size])
    #
    for i in range(board_size):
        for j in range(board_size - 1):
            planning_domain += (
                "\t\t(horinline "
                + board_arr[i * board_size + j]
                + " "
                + board_arr[i * board_size + (j + 1)]
                + ")\n"
            )
            planning_domain += (
                "\t\t(verinline "
                + board_arr[i + j * board_size]
                + " "
                + board_arr[i + (j + 1) * board_size]
                + ")\n"
            )
    for i in range(board_size - 1):
        for j in range(board_size - 1):
            planning_domain += (
                "\t\t(backdiagonal "
                + board_arr[i * board_size + j]
                + " "
                + board_arr[(i + 1) * board_size + (j + 1)]
                + ")\n"
            )
        for j in range(1, board_size):
            planning_domain += (
                "\t\t(rightdiagonal "
                + board_arr[i * board_size + j]
                + " "
                + board_arr[(i + 1) * board_size + (j - 1)]
                + ")\n"
            )
    # ~ Chiudo la parentesi di init
    planning_domain += "\t)\n"

    # ~ Definisco il goal
    planning_domain += "\t(:goal (not (exists (?x ?y) \n \t\t (and \n \t\t\t (not (= ?x ?y)) \n \t\t\t (Queen ?x) \n \t\t\t (Queen ?y) \n \t\t\t (mko (inline ?x ?y)) \n \t\t ) \n \t )) \n \t)\n"

    # ~ Chiudo la parentesi di domain
    planning_domain += "\n)"

    # ~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()


if __name__ == "__main__":
    # for att in ['a','b','c','d','e']: #copy of an instance for averaging
    # for board_size in range(3,27): #On an 8x8 board one can place 16 kings, so that no two pieces attack each other.
    for board_size in range(5, 16):
        # board_size = math.trunc(math.sqrt(queen_number * 16 / 3)) + var
        queen_number = board_size - 4  # math.trunc((pow(board_size,2))/4)
        if board_size < 27:
            print(
                "board_size " + str(board_size) + "\n queen_number " + str(queen_number)
            )
            generate_planning_problem(
                board_size,
                queen_number,
                filename="problems/problem" + str(board_size) + ".pddl",
            )
