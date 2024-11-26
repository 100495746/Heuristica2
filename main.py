# pylint: disable=all
import sys
import constraint


class Avion:
    def __init__(self, codigo):
        self.id = int(codigo[0])
        self.tipo = codigo[2:5]
        self.restr = bool(codigo[6] == "T")
        self.t1 = int(codigo[8:codigo.find("-", 8)])
        self.t2 = int(codigo[codigo.find("-", 8) + 1:])



    def __str__(self):
        return str(self.id) + "-" + str(self.tipo) + "-" + str(self.restr) + "-" + str(self.t1) + "-" + str(self.t2)


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


def tareas_completadas(avion, talleres, vals):
    """
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    """
    counter_2 = avion.t2
    counter_1 = avion.t1
    for each in vals:
        if each in talleres["STD"]:
            counter_1 -= 1
        elif each in talleres["SPC"]:
            if counter_2 > 0:
                counter_2 -= 1
            elif counter_1 > 0:
                counter_1 -= 1
    return counter_1 + counter_2 == 0

# Main function
def main():
    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        return 1

    fichero = sys.argv[1]
    lineas = lector(fichero)
    problem = constraint.Problem()
    franjas = int(lineas[0].split(":")[1].strip())
    x, y = lineas[1].split("x")
    dimensiones = (int(x), int(y))
    talleres = process_strings_to_dict(lineas[2:5])
    aviones = creador_aviones(lineas[5:])
    dicc_var = {franja: [] for franja in range(franjas)}
    variables_jmb = {franja: [] for franja in range(franjas)}
    dicc_por_avion = {avion: [] for avion in aviones}

    for avion in aviones:
        for franja in range(franjas):
            nueva_var = f"{avion}_{franja}"
            problem.addVariable(nueva_var, talleres["STD"] + talleres["SPC"] + talleres["PRK"])
            dicc_var[franja].append(nueva_var)
            dicc_por_avion[avion].append(nueva_var)
            if avion.tipo == "JMB":
                variables_jmb[franja].append(nueva_var)

    for franja, variables in variables_jmb.items():
        if variables:
            problem.addConstraint(constraint.AllDifferentConstraint(), variables)
            problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, True), variables)

    for franja in range(franjas):
        problem.addConstraint(no_mas_de_2, dicc_var[franja])
        problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, False), dicc_var[franja])

    for avion in aviones:
        problem.addConstraint(
            lambda *vals, av=avion: tareas_completadas(av, talleres, vals),
            dicc_por_avion[avion]
        )


    formated_dictionary = {}
    solution = problem.getSolution()

    for each in solution.keys():
        key_prefix = each.split("-")[0]
        if solution[each] in talleres["STD"]:
            tipo = "STD"
        elif solution[each] in talleres["SPC"]:
            tipo = "SPC"
        else:
            tipo = "PRK"

        if key_prefix in formated_dictionary:
            formated_dictionary[key_prefix].append(tipo + str(solution[each]))
        else:
            formated_dictionary[key_prefix] = [tipo + str(solution[each])]

    print(formated_dictionary)

if __name__ == "__main__":
    main()