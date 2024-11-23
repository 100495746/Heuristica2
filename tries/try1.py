# Importación de la librería
# pylint: disable=all

from constraint import *

# Definición de una variable como nuestro problema
problem = Problem()

# Creación de las variables
problem.addVariable('a', [1, 2])
problem.addVariable('b', [1, 2])

# Creación de las restricciones
problem.addConstraint(lambda a, b: a != b, ('a', 'b'))

# Recuperación de las soluciones
solutions = problem.getSolutions()
