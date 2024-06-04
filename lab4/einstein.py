#!/usr/bin/env python
#########
from ortools.sat.python import cp_model


# this function needs to create the csp model and return the model and a list of variables in the model
def setup_csp():
    model = cp_model.CpModel()
    variables = {}
    colors = ["Red", "Green", "Ivory", "Yellow", "Blue"]
    nations = ["Englishman", "Spaniard", "Norwegian", "Ukrainian", "Japanese"]
    cigarettes = ["Old Gold", "Kools", "Chesterfields", "Lucky Strike", "Parliaments"]
    drinks = ["Water", "Orange juice", "Tea", "Coffee", "Milk"]
    pets = ["Zebra", "Dog", "Fox", "Snails", "Horse"]

    # TODO: 1. Create all variables and add them to vars!
 	# e.g.,
    # v1 =  model.NewIntVar(1, 5, "variable1")
    # variables.append(v1)
    # v2 =  model.NewIntVar(1, 5, "variable2")
    # variables.append(v2)

    for var in colors + nations + cigarettes + drinks + pets:
        variables[var] = model.NewIntVar(1, 5, var)

    # TODO: 2. Add the constraints to the model!
    # You might need model.Add(), model.addAbsEquality() and model.AddAllDifferent()
    # see https://developers.google.com/optimization/reference/python/sat/python/cp_model
    # e.g.,
    # model.Add(v1 == v2)
    # model.Add(v1 != v2)
    # model.Add(v1 == v2 + 2)
    # model.addAbsEquality(2, v1 - v2) # meaning that abs(v1-v2) == 2
    # etc.
        
    # The Englishman lives in the red house.
    model.Add(variables["Englishman"] == variables["Red"])
    # The Spaniard owns the dog.
    model.Add(variables["Spaniard"] == variables["Dog"])
    # Coffee is drunk in the green house.
    model.Add(variables["Coffee"] == variables["Green"])
    # The Ukrainian drinks tea.
    model.Add(variables["Ukrainian"] == variables["Tea"])
    # The green house is immediately to the right of the ivory house.
    model.Add(variables["Green"] == variables["Ivory"]+1)
    # The Old Gold smoker owns snails.
    model.Add(variables["Old Gold"] == variables["Snails"])
    # Kools are smoked in the yellow house.
    model.Add(variables["Kools"] == variables["Yellow"])
    # Milk is drunk in the middle house.
    model.Add(variables["Milk"] == 3)
    # The Norwegian lives in the first house.
    model.Add(variables["Norwegian"] == 1)
    # The man who smokes Chesterfields lives in the house next to the man with the fox.
    model.AddAbsEquality(1, variables["Chesterfields"] - variables["Fox"])
    # Kools are smoked in the house next to the house where the horse is kept.
    model.AddAbsEquality(1, variables["Kools"] - variables["Horse"])
    # The Lucky Strike smoker drinks orange juice.
    model.Add(variables["Lucky Strike"] == variables["Orange juice"])
    # The Japanese smokes Parliaments.
    model.Add(variables["Japanese"] == variables["Parliaments"])
    # The Norwegian lives next to the blue house.
    model.Add(variables["Blue"] == variables["Norwegian"] + 1)
    # Each of the five houses has a different color, each of the five inhabitants has a different nationality, prefers a different brand of cigarettes, a different drink, and owns a different pet.

    model.AddAllDifferent([variables["Red"], variables["Green"], variables["Yellow"], variables["Blue"], variables["Ivory"]])
    model.AddAllDifferent([variables["Englishman"], variables["Spaniard"], variables["Norwegian"], variables["Ukrainian"], variables["Japanese"]])
    model.AddAllDifferent([variables["Old Gold"], variables["Kools"], variables["Chesterfields"], variables["Lucky Strike"], variables["Parliaments"]])
    model.AddAllDifferent([variables["Water"], variables["Orange juice"], variables["Tea"], variables["Coffee"], variables["Milk"]])
    model.AddAllDifferent([variables["Zebra"], variables["Dog"], variables["Fox"], variables["Snails"], variables["Horse"]])    

    return model, variables.values()


##############

def solve_csp():
    # create the model
    model, variables = setup_csp()
    # create the solver
    solver = cp_model.CpSolver()
    solution_printer = cp_model.VarArraySolutionPrinter(variables)
    # find all solutions and print them out
    status = solver.SearchForAllSolutions(model, solution_printer)
    if status == cp_model.INFEASIBLE:
        print("ERROR: Model does not have a solution!")
    elif status == cp_model.MODEL_INVALID:
        print("ERROR: Model is invalid!")
        model.Validate()
    elif status == cp_model.UNKNOWN:
        print("ERROR: No solution was found!")
    else:
        n = solution_printer.solution_count()
        print("%d solution(s) found." % n)
        print(solver.ResponseStats())
        if n > 1:
            print("ERROR: There should just be one solution!")


##############

def main():
    solve_csp()


if __name__ == "__main__":
    main()
