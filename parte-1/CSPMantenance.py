# pylint: disable=all
import sys
import constraint


class Avion:
    def __init__(self, codigo):
        self.id = int(codigo[0])
        self.tipo = codigo[2:5]
        self.restr = bool(codigo[6] == "T")
        self._t1 = int(codigo[8:codigo.find("-", 8)])
        self._t2 = int(codigo[codigo.find("-", 8) + 1:])
        self.t1 = self._t1
        self.t2 = self._t2

    def __str__(self):
        return str(self.id)  + "-" + str(self.tipo) + "-" + str(self.restr)  + "-" + str(self.t1) + "-" + str(self.t2)


def lector(fichero):
    with open(fichero, "r") as file1:
        lineas = file1.readlines()
    return lineas


def process_strings_to_dict(strings):
    talleres = {}
    for line in strings:
        key, coords = line.split(":")  # Separar la clave y las coordenadas
        key = key.strip()  # Limpiar espacios en la clave
        # Convertir las coordenadas a tuplas
        coordinates = [tuple(int(x) for x in coord.strip("()").split(",")) for coord in coords.strip().split()]
        talleres[key] = coordinates
    return talleres


def creador_aviones(l_codigos):
    l_aviones = []
    for each in l_codigos:
        l_aviones.append(Avion(each))
    return l_aviones


def tareas_restantes(t, avion, talleres):
    """
    Verifica si un taller puede asignarse basado en las tareas restantes del avión.
    Reduce el número de tareas pendientes según corresponda.
    """
    if t in talleres["SPC"]:
        avion.t2 -= 1
        return True

    elif t in talleres["STD"]:
        if avion.restr and avion.t2>0:
            return False
        else:
            if avion.t1 > 0:
                avion.t1 -= 1
            return True
    else:
        return True


def distancia1(t1, t2):
    # Dos talleres son adyacentes si están a una distancia de 1 en ambas dimensiones
    return abs(t1[0] - t2[0]) <= 1 and abs(t1[1] - t2[1]) <= 1


def jmb_no_adyacentes(vars):
    # usar esta en caso de ser necesario dividirlo por partes
    for each in vars:
        if (each[0], each[1] + 1) in vars:
            return False
        if (each[0] + 1, each[1]) in vars:
            return False
        if (each[0], each[1] - 1) in vars:
            return False
        if (each[0] - 1, each[1]) in vars:
            return False
        return True


def adyacentes(vars, dimensiones, jmb):
    occupied = 0
    for each in vars:
        if (each[0], each[1] + 1) in vars:
            occupied += 1
        if (each[0] + 1, each[1]) in vars:
            occupied += 1
        if (each[0], each[1] - 1) in vars:
            occupied += 1
        if (each[0] - 1, each[1]) in vars:
            occupied += 1

        if jmb and occupied > 0:
            return False
        elif (each[0] == 0 or each[0] == dimensiones) and (each[1] == 0 or each[1] == dimensiones) and occupied == 2:
            return False
        elif ((each[0] == 0 or each[0] == dimensiones) or (each[1] == 0 or each[1] == dimensiones)) and occupied == 3:
            return False
        elif occupied == 4:
            return False
        return True


def no_mas_de_2(*variables):
    for each in variables:
        if variables.count(each) > 2:
            return False
    return True


def main():

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        return 1

    fichero = sys.argv[1]
    lineas = lector(fichero)
    # linea0: número de franjas horarias
    # linea1: dimensiones matriz talleres
    # linea2: posiciones talleres STD
    # linea3: posiciones talleres SDC
    # linea4: posiciones parking
    # líneas 5 y en adelante: códigos aviones
    problem = constraint.Problem()
    franjas = int(lineas[0].split(":")[1].strip())
    x, y = lineas[1].split("x")
    dimensiones = (int(x), int(y))
    talleres = process_strings_to_dict(lineas[2:5])
    aviones = creador_aviones(lineas[5:])
    dicc_var = {franja: [] for franja in range(franjas)}
    variables_jmb = {franja: [] for franja in range(franjas)}  # Guardar solo los JMB

    for avion in aviones:
        for franja in range(franjas):
            nueva_var = f"{avion}_{franja}"
            problem.addVariable(nueva_var, talleres["STD"] + talleres["SPC"] + talleres["PRK"])
            # Agregar la restricción para cada variable
            problem.addConstraint(
                    lambda t, av=avion: tareas_restantes(t, av, talleres), [nueva_var]
                )


            dicc_var[franja].append(nueva_var)
            if avion.tipo == "JMB":
                variables_jmb[franja].append(nueva_var)

    for franja in range(franjas):
        problem.addConstraint(no_mas_de_2, dicc_var[franja])
        problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, False), dicc_var[franja])

    for franja, variables in variables_jmb.items():
        if variables:  # Solo aplica si hay variables JMB en esta franja
            problem.addConstraint(constraint.AllDifferentConstraint(), variables)
            problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, True), variables)

    formated_dictionary = {}
    solution = problem.getSolution()
    print(solution)

    for each in solution.keys():
        key_prefix = each.split("-")[0]
        if key_prefix in formated_dictionary:
            formated_dictionary[key_prefix].append(solution[each])
        else:
            formated_dictionary[key_prefix] = [solution[each]]

    print(formated_dictionary)


if __name__ == "__main__":
    main()
