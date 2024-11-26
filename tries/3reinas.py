"""Using Constraint Processing for solving the classical N-queens problem """
# pylint: disable=all
import constraint

# globals
# -----------------------------------------------------------------------------
N = 4


# this simple Python script solves the N-queens problem, where N queens have to
# be located on a NxN chessboard such that there are not two queens threatening
# each other. The following is a feasible solution of the 4-Queens problem:
#
# +---+---+---+---+
# |   |   | x |   |
# +---+---+---+---+
# | x |   |   |   |
# +---+---+---+---+
# |   |   |   | x |
# +---+---+---+---+
# |   | x |   |   |
# +---+---+---+---+
#

# showSolution
#
# Given a solution as a dictionary of variables and their values, show a
# graphical view of it

def showSolution(solution):
    """Given a solution as a dictionary of variables and their values, show a
       graphical view of it

    """

    print("+---" * N + "+")
    for irow in range(N):
        print("|", end='')
        for icol in range(N):
            if solution[icol] == irow:
                print(" x |", end='')
            else:
                print("   |", end='')
        print()
        print("+---" * N + "+")


# main
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # create a new problem
    problem = constraint.Problem()

    # variables
    # -------------------------------------------------------------------------
    # there is a variable for each column so that the i-th variable records the
    # row in which the i-th queen is located, and thus each variable has a
    # domain which is the number of rows
    x = range(N)
    domain = range(N)
    problem.addVariables(x, domain)

    # constraints
    # -------------------------------------------------------------------------

    # to ensure that all queens are located in different rows it just suffices
    # to ensure that they all take different values
    problem.addConstraint(constraint.AllDifferentConstraint())

    # next, to ensure that two queens are not located in the same diagonal it is
    # necessary to verify that the absolute value of the difference of the rows
    # is different to the absolute value of the columns
    for icol in x:
        for jcol in x:
            if icol < jcol:
                # note the usage of the default parameters which easily record
                # the columns, i.e., the variables used in this iteration
                problem.addConstraint(lambda irow, jrow, icol=icol, jcol=jcol:
                                      abs(irow - jrow) != abs(icol - jcol),
                                      (icol, jcol))
    # compute the solutions
    solutions = problem.getSolutions()

    # and show them on the standard output
    print(" #{0} solutions have been found: ".format(len(solutions)))
    for isolution in solutions:
        showSolution(isolution)
        print()
