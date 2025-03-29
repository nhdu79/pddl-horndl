* 3 Variants
    - For each benchmarks:
        - New Tseitin/ Without Tseitin

* For original:
    - Robot with changed action

* SMALL INSTANCES:
    - Cat
    - Robot
    - Elevator


	#~ Genero moveUp
	planning_domain += "\t(:action moveUp\n"
	planning_domain += "\t\t:parameters (?x)\n"
	planning_domain += "\t\t:precondition (and (mko (Rows ?x)))\n"
	planning_domain += "\t\t:effect "

	planning_domain += "(and \n"
	for row in range(rows-1):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (AboveOf"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (AboveOf"+str(row+1)+" ?x))\n"
		#~ planning_domain += "\t\t:delete ()\n"
		planning_domain += "\t\t\t\t)\n"

	for row in range(1,rows):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (BelowOf"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (BelowOf"+str(row+1)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"
		planning_domain += "\t\t\t(when (and (mko (BelowOf"+str(row)+" ?x)) (not (BelowOf"+str(row+1)+" ?x)))\n"
		planning_domain += "\t\t\t\t(and (not (BelowOf"+str(row)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"

	for row in range(rows-1):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (Row"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (Row"+str(row+1)+" ?x)\n"
		planning_domain += "\t\t\t\t(not (Row"+str(row)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"

	for row in range(rows-1):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (and (AboveOf"+str(row)+" ?x) (BelowOf"+str(row+1)+" ?x)))\n"
		planning_domain += "\t\t\t\t(and (Row"+str(row+1)+" ?x))\n"
		#~ planning_domain += "\t\t:delete ((Row"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"

	#~ Chiudo la parentesi di moveUp
	planning_domain += "\t\t))\n"


    #~ Genero moveRight
	planning_domain += "\t(:action moveRight\n"
	planning_domain += "\t\t:parameters (?x)\n"
	planning_domain += "\t\t:precondition (and (mko (Columns ?x)))\n"
	planning_domain += "\t\t:effect "

	planning_domain += "(and \n"
	for column in range(columns-1):
		planning_domain += "\t\t\t(when (mko (RightOf"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (RightOf"+str(column+1)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"

	for column in range(1,columns):
		#planning_domain += "\t\t\n"
		planning_domain += "\t\t\t(when (mko (LeftOf"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (LeftOf"+str(column+1)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"
		planning_domain += "\t\t\t(when (and (mko (LeftOf"+str(column)+" ?x)) (not (LeftOf"+str(column+1)+" ?x)))\n"
		planning_domain += "\t\t\t\t(and (not (LeftOf"+str(column)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"

	for column in range(columns-1):
		#planning_domain += "\t\t\n"
		planning_domain += "\t\t\t(when (mko (Column"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (Column"+str(column+1)+" ?x)\n"
		planning_domain += "\t\t\t\t(not (Column"+str(column)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"

	for column in range(columns-1):
		#planning_domain += "\t\t\n"
		planning_domain += "\t\t\t(when (mko (and (RightOf"+str(column)+" ?x) (LeftOf"+str(column+1)+" ?x)))\n"
		planning_domain += "\t\t\t\t(and (Column"+str(column+1)+" ?x))\n"
		#~ planning_domain += "\t\t:delete ((Column"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"

	#~ Chiudo la parentesi di moveRight
	planning_domain += "\t\t))\n"
