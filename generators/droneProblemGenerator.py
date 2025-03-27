#!/bin/python3
import math
import random
from itertools import product

def inline(t, drone_arr):
    for x in drone_arr:
        if x[0]==t[0] or x[1]==t[1]:
            if (abs(ord(x[0])-ord(t[0])) < 2) and (abs(ord(x[1])-ord(t[1])) < 2):
                return True
    return False

def generate_planning_problem(board_size, drone_number, wetdrone_number, lowvisibility, humantree_number, filename):
	
	#~ Inizializzo il problema di planning
    planning_domain = """(define (problem drone_problem)
	(:domain drone)\n"""
	
	#~ Genero gli individui in :objects
    object_arr = []
    j = 0
    i = 0
    #dig = math.floor(math.log(pow(board_size,2),26))
    #while j < pow(board_size,2):
        #s = ""
        #i = dig
        #tr = j
        #while i >= 0:
            #num = math.trunc(tr/(26**i))
            #s += chr(ord('a') + num)
            #tr -= num*(26**i)
            #i -= 1
        #object_arr.append(s)
        #j += 1
    while i < board_size:
        while j < board_size:
            s = chr(ord('a') + i) + chr(ord('a') + j)
            object_arr.append(s)
            j += 1
        i += 1
        j = 0
    planning_domain += "\t(:objects "
    for x in object_arr:
        planning_domain += x + " "
    planning_domain += "env )\n"
	#
	#~ Definisco :init
    planning_domain += "\t(:init\n"
    
    board_arr = list(object_arr)
    pic = ["-"] * pow(board_size,2)
    drone_arr = []
    humantree_arr = []
    lowvisibility_arr = []
    i = 0
    while i < lowvisibility:
        s = random.choice(object_arr)
        lowvisibility_arr.append(s)
        i += 1
    i = 0
    middle = math.trunc(board_size/2)
    while i < drone_number:
        if i == 0:
            s = object_arr[middle*board_size + middle]
        else:
            s = 0
            while s == 0:
                t = random.choice(object_arr)
                if inline(t,drone_arr):
                    s = t
        object_arr.remove(s)
        drone_arr.append(s)
        i += 1
    i = 0
    while i < humantree_number:
        s = random.choice(object_arr)
        object_arr.remove(s)
        humantree_arr.append(s)
        i += 1
    #
    i = 0
    #wetdrone_arr = []
    while (i < wetdrone_number) and (len(drone_arr) > 0):
        s = random.choice(drone_arr)
        drone_arr.remove(s)
        #wetdrone_arr.append(s)
        ind = board_arr.index(s)
        pic[ind] = "w"
        planning_domain += "\t\t(WetDrone " + s + ")\n"
        i += 1
    for s in drone_arr:
        planning_domain += "\t\t(Drone " + s + ")\n"
        ind = board_arr.index(s)
        pic[ind] = "d"
    #
    i = 0
    #human_arr = []
    while (i < math.floor(humantree_number/2)) and (len(humantree_arr) > 0):
        s = random.choice(humantree_arr)
        humantree_arr.remove(s)
        #human_arr.append(s)
        ind = board_arr.index(s)
        pic[ind] = "h"
        planning_domain += "\t\t(Human " + s + ")\n"
        i += 1
    for s in humantree_arr:
        planning_domain += "\t\t(Tree " + s + ")\n"
        ind = board_arr.index(s)
        pic[ind] = "t"
    #
    for i in range(board_size):
        print pic[i*board_size:(i+1)*board_size]
    #
    planning_domain += "\t\t(LowVisibility env)\n"
    for s in lowvisibility_arr:
        planning_domain += "\t\t(environment " + s + " env)\n"

    for i in range(board_size):
        for j in range(board_size-1):
             planning_domain += "\t\t(veryClose " + board_arr[i*board_size+j] + " " + board_arr[i*board_size+(j+1)] + ")\n"
             planning_domain += "\t\t(veryClose " + board_arr[i+j*board_size] + " " + board_arr[i+(j+1)*board_size] + ")\n"
    for i in range(board_size-1):
        for j in range(board_size-1):
             planning_domain += "\t\t(near " + board_arr[i*board_size+j] + " " + board_arr[(i+1)*board_size+(j+1)] + ")\n"
        for j in range(1,board_size):
             planning_domain += "\t\t(near " + board_arr[i*board_size+j] + " " + board_arr[(i+1)*board_size+(j-1)] + ")\n"
	#~ Chiudo la parentesi di init
    planning_domain += "\t)\n"
	
	#~ Definisco il goal
    planning_domain += "\t(:goal (not (mko (exists (?x ?y) \n \t\t (and \n \t\t\t (RiskOfPhysicalDamage ?x) \n \t\t\t (RiskOfPhysicalDamage ?y) \n \t\t\t (near ?x ?y) \n \t\t )) \n \t )) \n \t)\n"
	
	#~ Chiudo la parentesi di domain
    planning_domain += "\n)"
	
	#~ Creo il file e gli scrivo dentro planning_domain
    output_file = open(filename, "w")
    output_file.write(planning_domain)
    output_file.close()

if __name__ == '__main__':
    for board_size in [3,4,7,8,9,10]:
        humantree_number = math.trunc(pow(board_size,2)/4) #a quater of the board
        for att in ['a','b','c','d','e']: #copy of an instance for averaging
                #for board_size in range(3,27): #On an 8x8 board one can place 16 kings, so that no two pieces attack each other.
            for drone_number in range(2,math.trunc((pow(board_size,2)-humantree_number)*3/4)): #On an 8x8 board one can place 16 kings, so that no two pieces attack each other
                #board_size = math.trunc(math.sqrt(drone_number * 16 / 3)) + var
                #drone_number = math.trunc((pow(board_size,2)-humantree_number)/4) + var
                wetdrone_number = math.trunc(drone_number/4) #a quater of the total drones
                lowvisibility = math.trunc(pow(board_size,2)/5) #a fifth part of the board
                if board_size < 27:
                    print "board_size " + str(board_size) + "\n drone_number " + str(drone_number) + "\n wetdrone_number " + str(wetdrone_number) + "\n lowvisibility " + str(lowvisibility) + "\n humantree_number " + str(humantree_number)
                    generate_planning_problem(board_size, drone_number, wetdrone_number, lowvisibility, humantree_number, filename = "problems" + str(board_size) + "/droneProblem" + str(drone_number) + str(att) + ".pddl")
