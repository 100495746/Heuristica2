# pylint: disable=all
from constraint import *

# Definición de una variable como nuestro problema
problem = Problem()

# Crea la variable 'a' que tiene como dominio [1, 2]
problem.addVariable('a', [1, 2])

# Crea las variables 'a' y 'b', ambas con el dominio [1, 2, 3]
problem.addVariables('ab', [1, 2, 3])

# Crea las variables 'a' y 'b', ambas con el dominio [0, 1, 2]
problem.addVariables(['a', 'b'], range(3))
