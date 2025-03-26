#!/bin/python3
from itertools import product

def generate_planning_domain(columns, rows, filename, onto):

	print("Ontology \n")
	ontology = """@prefix : <http://www.semanticweb.org/alisa/ontologies/2021/3/robot> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://www.semanticweb.org/alisa/ontologies/2021/3/robot> .\n"""
	ontology += "\n<http://www.semanticweb.org/alisa/ontologies/2021/3/robot> rdf:type owl:Ontology .\n\n ################################################################# \n #    Classes\n ################################################################# \n \n"
	
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Column0\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Column0> rdf:type owl:Class .\n\n\n"
#	                                                          owl:equivalentClass <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf1> .\n\n\n"
	for column in range(1,columns):
		#planning_domain += "\t\t(isA RightOf"+str(column+1)+" RightOf"+str(column)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(column)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(column)+"> rdf:type owl:Class .\n\n\n"
		#                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(column)+"> .\n\n\n"
	# ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(columns)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(columns)+"> rdf:type owl:Class ;\n                                                          owl:equivalentClass <http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf"+str(columns-1)+"> .\n\n\n"
	
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Row0\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Row0> rdf:type owl:Class .\n\n\n"
	#                                                          owl:equivalentClass <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf1> .\n\n\n"
	for row in range(1,rows-1):
		#planning_domain += "\t\t(isA RightOf"+str(column+1)+" RightOf"+str(column)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(row)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(row)+"> rdf:type owl:Class .\n\n\n"
		#                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(row)+"> .\n\n\n"
	# ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(rows)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(rows)+"> rdf:type owl:Class ;\n                                                          owl:equivalentClass <http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf"+str(rows-1)+"> .\n\n\n"
	
	#planning_domain += "\t\t(isA RightOf0 Columns)\n"
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf0 \n <http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf0> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Columns> .\n\n\n"
	for column in range(columns-1):
		#planning_domain += "\t\t(isA RightOf"+str(column+1)+" RightOf"+str(column)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf"+str(column+1)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf"+str(column+1)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf"+str(column)+"> ;\n                                                          owl:disjointWith <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(column+1)+"> .\n\n\n"
	
	#planning_domain += "\t\t(isA LeftOf"+str(columns)+" Columns)\n"
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(columns)+" \n <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(columns)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Columns> .\n\n\n"
	for column in range(columns-1):
		#planning_domain += "\t\t(isA LeftOf"+str(columns-column-1)+" LeftOf"+str(columns-column)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(columns-column-1)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(columns-column-1)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(columns-column)+"> .\n\n\n"
		
	#planning_domain += "\t\t(isA AboveOf0 Rows)\n"
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf0 \n <http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf0> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Rows> .\n\n\n"
	for row in range(rows-1):
		#planning_domain += "\t\t(isA AboveOf"+str(row+1)+" AboveOf"+str(row)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf"+str(row+1)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf"+str(row+1)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf"+str(row)+"> ;\n                                                          owl:disjointWith <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(row+1)+"> .\n\n\n"
	
	#planning_domain += "\t\t(isA BelowOf"+str(rows)+" Rows)\n"
	ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(rows)+" \n <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(rows)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Rows> .\n\n\n"
	for row in range(rows-1):
		#planning_domain += "\t\t(isA BelowOf"+str(rows-row-1)+" BelowOf"+str(rows-row)+")\n"
		ontology+= "###  http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(rows-row-1)+"\n <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(rows-row-1)+"> rdf:type owl:Class ;\n                                                          rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(rows-row)+"> .\n\n\n"
	ontology+= "################################################################# \n#    General axioms\n ################################################################# \n\n"
	
	for column in range(columns):
		ontology+= "[ owl:intersectionOf ( <http://www.semanticweb.org/alisa/ontologies/2021/3/LeftOf"+str(column+1)+"> \n                       <http://www.semanticweb.org/alisa/ontologies/2021/3/RightOf"+str(column)+">\n                     ) ;\n   rdf:type owl:Class ; \n  rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Column"+str(column)+">] . \n\n"
	for row in range(rows):
		ontology+= "[ owl:intersectionOf ( <http://www.semanticweb.org/alisa/ontologies/2021/3/BelowOf"+str(row+1)+"> \n                       <http://www.semanticweb.org/alisa/ontologies/2021/3/AboveOf"+str(row)+">\n                     ) ;\n   rdf:type owl:Class ; \n  rdfs:subClassOf <http://www.semanticweb.org/alisa/ontologies/2021/3/Row"+str(row)+">] . \n\n"
	#for column in range(1,columns):
	#	planning_domain += "\t\t(isA LeftOf"+str(column)+" (not RightOf"+str(column)+"))\n"
	#for row in range(1,rows):
	#	planning_domain += "\t\t(isA AboveOf"+str(row)+" (not BelowOf"+str(row)+"))\n"
	
	#~ Chiudo la parentesi di axioms
	ontology += "###  Generated by the OWL API (version 4.5.9.2019-02-01T07:24:44Z) https://github.com/owlcs/owlapi\n"
	
	output_file = open(onto, "w")
	output_file.write(ontology)
	output_file.close()
	
	print("Inizio la generazione del planning domain.\n")
	
	#~ Inizializzo il dominio di planning
	planning_domain = """(define (domain robot)\n"""
	
	#~ Genero i predicati per ogni colonna e riga
	planning_domain += "\t(:predicates\n"
	planning_domain += "\t\t(Columns ?x)\n"
	planning_domain += "\t\t(Rows ?x)\n"
	
	for column in range(columns):
		planning_domain += "\t\t(Column"+str(column)+" ?x)\n"
	for column in range(columns):
		planning_domain += "\t\t(RightOf"+str(column)+" ?x)\n"
	for column in range(columns):
		planning_domain += "\t\t(LeftOf"+str(column+1)+" ?x)\n"
		
	for row in range(rows):
		planning_domain += "\t\t(Row"+str(row)+" ?x)\n"
	for row in range(rows):
		planning_domain += "\t\t(AboveOf"+str(row)+" ?x)\n"
	for row in range(rows):
		planning_domain += "\t\t(BelowOf"+str(row+1)+" ?x)\n"
	
	#~ Chiudo la parentesi di predicates
	planning_domain += "\t)\n"
	
	#~ Creo il file e gli scrivo dentro planning_domain
	output_file = open(filename, "w")
	output_file.write(planning_domain)
	output_file.close()
	
	planning_domain = ""
	print("Finito la sezione :predicates\n")
	
	#~ Genero le azioni
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
		planning_domain += "\t\t\t\t(and (LeftOf"+str(column+1)+" ?x)\n"
		planning_domain += "\t\t\t\t(not (LeftOf"+str(column)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"
	
	# for column in range(columns-1):
	# 	#planning_domain += "\t\t\n"
	# 	planning_domain += "\t\t\t(when (mko (Column"+str(column)+" ?x))\n"
	# 	planning_domain += "\t\t\t\t(and (Column"+str(column+1)+" ?x)\n"
	# 	planning_domain += "\t\t\t\t(not (Column"+str(column)+" ?x)))\n"
	# 	planning_domain += "\t\t\t\t)\n"
	
	#for column in range(columns-1):
		#planning_domain += "\t\t\t(when (mko (and (RightOf"+str(column)+" ?x) (LeftOf"+str(column+1)+" ?x)))\n"
		#planning_domain += "\t\t\t\t(and (Column"+str(column+1)+" ?x))\n"
		#planning_domain += "\t\t\t\t)\n"
	
	#~ Chiudo la parentesi di moveRight
	planning_domain += "\t\t))\n"
	
	#~ Genero moveLeft
	planning_domain += "\t(:action moveLeft\n"
	planning_domain += "\t\t:parameters (?x)\n"
	planning_domain += "\t\t:precondition (and (mko (Columns ?x)))\n"
	planning_domain += "\t\t:effect "
	
	planning_domain += "(and \n"
	for column in range(2,columns+1):
		#planning_domain += "\t\t\n"
		planning_domain += "\t\t\t(when (mko (LeftOf"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (LeftOf"+str(column-1)+" ?x))\n"
		#~ planning_domain += "\t\t:delete ()\n"
		planning_domain += "\t\t\t\t)\n"
	
	for column in range(1,columns):
		#planning_domain += "\t\t\n"
		planning_domain += "\t\t\t(when (mko (RightOf"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (RightOf"+str(column-1)+" ?x)\n"
		planning_domain += "\t\t\t\t(RightOf"+str(column)+" ?x))\n"
		planning_domain += "\t\t\t\t)\n"
	
	# for column in range(1,columns):
	# 	#planning_domain += "\t\t(\n"
	# 	planning_domain += "\t\t\t(when (mko (Column"+str(column)+" ?x))\n"
	# 	planning_domain += "\t\t\t\t(and (Column"+str(column-1)+" ?x)\n"
	# 	planning_domain += "\t\t\t\t(not (Column"+str(column)+" ?x)))\n"
	# 	planning_domain += "\t\t\t\t)\n"
	
	#for column in range(1,columns):
		#planning_domain += "\t\t\t(when (mko (and (RightOf"+str(column)+" ?x) (LeftOf"+str(column+1)+" ?x)))\n"
		#planning_domain += "\t\t\t\t(and (Column"+str(column-1)+" ?x))\n"
		#planning_domain += "\t\t\t\t)\n"
	
	#~ Chiudo la parentesi di moveLeft
	planning_domain += "\t\t))\n"
	
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
		planning_domain += "\t\t\t\t(and (BelowOf"+str(row+1)+" ?x)\n"
		planning_domain += "\t\t\t\t(not (BelowOf"+str(row)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"
	
	# for row in range(rows-1):
	# 	#planning_domain += "\t\t(\n"
	# 	planning_domain += "\t\t\t(when (mko (Row"+str(row)+" ?x))\n"
	# 	planning_domain += "\t\t\t\t(and (Row"+str(row+1)+" ?x)\n"
	# 	planning_domain += "\t\t\t\t(not (Row"+str(row)+" ?x)))\n"
	# 	planning_domain += "\t\t\t\t)\n"
	
	#for row in range(rows-1):
		#planning_domain += "\t\t\t(when (mko (and (AboveOf"+str(row)+" ?x) (BelowOf"+str(row+1)+" ?x)))\n"
		#planning_domain += "\t\t\t\t(and (Row"+str(row+1)+" ?x))\n"
		#planning_domain += "\t\t\t\t)\n"
	
	#~ Chiudo la parentesi di moveUp
	planning_domain += "\t\t))\n"
	
	#~ Genero moveDown
	planning_domain += "\t(:action moveDown\n"
	planning_domain += "\t\t:parameters (?x)\n"
	planning_domain += "\t\t:precondition (and (mko (Rows ?x)))\n"
	planning_domain += "\t\t:effect "
	
	planning_domain += "(and \n"
	for row in range(2,rows+1):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (BelowOf"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (BelowOf"+str(row-1)+" ?x))\n"
		#~ planning_domain += "\t\t:delete ()\n"
		planning_domain += "\t\t\t\t)\n"
	
	for row in range(1,rows):
		#planning_domain += "\t\t(\n"
		planning_domain += "\t\t\t(when (mko (AboveOf"+str(row)+" ?x))\n"
		planning_domain += "\t\t\t\t(and (AboveOf"+str(row-1)+" ?x)\n"
		planning_domain += "\t\t\t\t(not (AboveOf"+str(row)+" ?x)))\n"
		planning_domain += "\t\t\t\t)\n"
	
	# for row in range(1,rows):
	# 	#planning_domain += "\t\t(\n"
	# 	planning_domain += "\t\t\t(when (mko (Row"+str(row)+" ?x))\n"
	# 	planning_domain += "\t\t\t\t(and (Row"+str(row-1)+" ?x)\n"
	# 	planning_domain += "\t\t\t\t(not (Row"+str(row)+" ?x)))\n"
	# 	planning_domain += "\t\t\t\t)\n"
	
	#for row in range(1,rows):
		#planning_domain += "\t\t\t(when (mko (and (AboveOf"+str(row)+" ?x) (BelowOf"+str(row+1)+" ?x)))\n"
		#planning_domain += "\t\t\t\t(and (Row"+str(row-1)+" ?x))\n"
		#planning_domain += "\t\t\t\t)\n"
	
	#~ Chiudo la parentesi di moveDown
	planning_domain += "\t\t))\n"
	
	#~ Creo il file e gli scrivo dentro planning_domain
	output_file = open(filename, "a")
	output_file.write(planning_domain)
	output_file.close()
	
	planning_domain = ""
	print("Finito la sezione :action\n")
	
	#~ Chiudo la parentesi di domain
	planning_domain += "\n)"
	
	#~ Creo il file e gli scrivo dentro planning_domain
	output_file = open(filename, "a")
	output_file.write(planning_domain)
	output_file.close()
	
	print("Finito di scrivere il dominio!\n")

def generate_planning_problem(rightOf, leftOf, aboveOf, belowOf, column, row, filename):
	
	#~ Inizializzo il problema di planning
	planning_domain = """(define (problem robotProblem)
	(:domain robot)\n"""
	
	#~ Genero gli individui in :objects
	planning_domain += "\t(:objects robot)\n"
	
	#~ Definisco :init
	planning_domain += "\t(:init\n"
	planning_domain += "\t\t(RightOf" + str(rightOf) + " robot)\n"
	planning_domain += "\t\t(LeftOf" + str(leftOf) + " robot)\n"
	planning_domain += "\t\t(AboveOf" + str(aboveOf) + " robot)\n"
	planning_domain += "\t\t(BelowOf" + str(belowOf) + " robot)\n"
	
	#~ Chiudo la parentesi di init
	planning_domain += "\t)\n"
	
	#~ Definisco il goal
	planning_domain += "\t(:goal (and (mko (Column" + str(column) + " robot)) (mko (Row" + str(row) + " robot))))\n"
	
	#~ Chiudo la parentesi di domain
	planning_domain += "\n)"
	
	#~ Creo il file e gli scrivo dentro planning_domain
	output_file = open(filename, "w")
	output_file.write(planning_domain)
	output_file.close()

if __name__ == '__main__':
	for t in range(50,201,10):
		columns = t
		rows = t
		generate_planning_domain(columns = columns, rows = rows, filename = "generated/robotDomain"+ str(t) +".pddl",onto = "generated/TTL"+ str(t) +".owl")
		generate_planning_problem(rightOf = 1, leftOf = columns-1, aboveOf = 0, belowOf = rows-1, column = 2, row = 1, filename = "generated/robotProblem" + str(t) +".pddl")
