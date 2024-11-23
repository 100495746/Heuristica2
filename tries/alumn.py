from constraint import *
# pylint: disable=all
problem = Problem()

# Se anyaden las variables al problema. Existen diferentes formas de hacerlo mediante las funciones addVariable
# y addVariables
#
# Ejemplos:
# problem.addVariable('a', [1, 2])		Crea la variable 'a' que tiene como dominio [1, 2]
# problem.addVariables("ab", [1, 2, 3])		Crea las variables 'a' y 'b', ambas con el dominio [1, 2, 3]
# problem.addVariables(['a', 'b'], range(3))	Crea las variables 'a' y 'b', ambas con el dominio [0, 1, 2]
#
# Para el problema del grupo de alumnos que tienen que hacer un documento de Ingenieria del Software tenemos 6 variables
# (J, M, A, Y, R, F), todas tienen como dominio [1, 2, 3] salvo Juan puesto que el enunciado dice que no tiene
# conocimientos
# para hacer la primera parte,
# luego su dominio sera [2, 3], y Maria que solo quiere trabajar en la tercera parte, luego su
# dominio sera [3]
#

problem.addVariables(['A', 'Y', 'R', 'F'], [1, 2, 3])
problem.addVariable('J', [2, 3])
problem.addVariable('M', [3])

# A continuacion se anyaden las restricciones del problema mediante la funcion addConstraint proporcionada por la libreria
#
# Ejemplos:
# problem.addConstraint(lambda a, b: a > b, ('a', 'b'))		Crea una funcion lambda que recibe dos parametros que se corresponden
# con los valores de las variables 'a' y 'b', y comprueba que 'a' es mayor que 'b'. Tambien se podria haber creado una funcion para
# comprobar este hecho:
#
# def greater(a, b):
#    if a > b:
#	return True
#
# problem.addConstraint(greater, ('a', 'b'))
#
# En este caso vamos a modelar en primer lugar la restriccion de que Alfredo y Ruben no quieren trabajar juntos, es decir,
# RA,R = [(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)]. Se puede hacer de varias formas. Una de ellas es definir una funcion, por ejemplo,
# notEqual, que compruebe que el valor de una variable es diferente de la de la otra:

def notEqual(a, b):
	if a != b:
		return True

problem.addConstraint(notEqual, ('A', 'R'))

# Tambien se puede crear una funcion lambda para hacer esta comprobacion:

problem.addConstraint(lambda a, b: a != b, ('A', 'R'))


# Por ultimo, la libreria ofrece la funcion AllDifferentConstraint que precisamente comprueba que el valor de una variable es diferente a las de las otras:

problem.addConstraint(AllDifferentConstraint(), ['A', 'R'])

# Lo anterior, son tres formas diferentes de modelar la misma restriccion RA,R = [(1,2),(1,3),(2,1),(2,3),(3,1),(3,2)]
# Ahora modelamos la restriccion de que Ruben y Felisa quieren trabajar en la misma parte RR,F={(1,1),(2,2),(3,3)}

problem.addConstraint(lambda a, b: a == b, ('R', 'F'))


# Por ultimo, modelamos la restriccion de que Yara hace una parte posterior a la que haga Ruben, RR,Y={(1,2),(1,3),(2,3)}

def consecutive(a, b):
	if b > a:
		return True

problem.addConstraint(consecutive, ('R', 'Y'))

# Una vez modelado el problema, podemos recuperar una de las soluciones:

print(problem.getSolution())

# o todas las soluciones:

print(problem.getSolutions())

