"""
Using Constraint Processing for solving a simple sum-words brain teaser
"""

import constraint
# pylint: disable=all

# this simple Python script solves the following sum-word brain
# teaser:
#
#                             S E N D
#                           + M O R E
#                          -----------
#                           M O N E Y
#                             a b c d

# sumWordConstraint
#
# verifies that a + b = c but taking into account an overflow coming
# from the previous summation and that an overflow might be generated
# in this one
def sumWordConstraint(a, b, c, post, pre=0):
    return pre + a + b == c + 10 * post


# main
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    # create a new problem
    problem = constraint.Problem()

    # variables
    # -------------------------------------------------------------------------

    # upper-case letters stand for the variables to unveal wheras
    # lower-case letters stand for the overflow
    problem.addVariables("SENDMORY", range(10))
    problem.addVariables("abcd", range(2))

    # constraints
    # -------------------------------------------------------------------------

    # the constraints are numerically described as follows
    problem.addConstraint(sumWordConstraint, ('D', 'E', 'Y', 'd'))
    problem.addConstraint(sumWordConstraint, ('N', 'R', 'E', 'c', 'd'))
    problem.addConstraint(sumWordConstraint, ('E', 'O', 'N', 'b', 'c'))
    problem.addConstraint(sumWordConstraint, ('S', 'M', 'O', 'a', 'b'))
    problem.addConstraint(constraint.AllDifferentConstraint(), "SENDMORY")
    problem.addConstraint(lambda x, y: x == y, ("M", "a"))

    # compute the solutions
    solutions = problem.getSolutions()

    print(" #{0} solutions have been found: ".format(len(solutions)))
    for isolution in solutions:
        print("""   
     {0} {1} {2} {3}
   + {4} {5} {6} {1}
   ----------
   {4} {5} {2} {1} {7}""".format(isolution['S'], isolution['E'], isolution['N'], isolution['D'],
                                 isolution['M'], isolution['O'], isolution['R'], isolution['Y']))

# Local Variables:
# mode:python
# fill-column:80
# End: