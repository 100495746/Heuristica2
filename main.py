# pylint: disable=all
import sys
import constraint
import time


class Avion:
    def __init__(self, codigo):
        partes = codigo.split("-")
        self.id = int(partes[0])
        self.tipo = partes[1]
        self.restr = partes[2] == 'T'
        self.t1 = int(partes[3])
        self.t2 = int(partes[4])

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


def adyacentes(proposed, dimensiones, jmb):
    occupied = 0
    for each in proposed:
        if (each[0], each[1] + 1) in proposed:
            occupied += 1
        if (each[0] + 1, each[1]) in proposed:
            occupied += 1
        if (each[0], each[1] - 1) in proposed:
            occupied += 1
        if (each[0] - 1, each[1]) in proposed:
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


"""def tareas2_completadas(avion, talleres, vals):
    
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    
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
    print(counter_1+counter_2)
    return counter_1 + counter_2 == 0
"""


def tareas2_completadas(avion, talleres, di, vals):
    """
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    """
    print(vals)
    counter_2 = avion.t2
    counter_1 = avion.t1
    prk_count = 0
    for each in vals:
        if each in talleres["PRK"]:
            prk_count += 1
    if di - prk_count < counter_1 + counter_2:
        return False

    for each in vals:
        if each in talleres["STD"]:
            counter_1 -= 1
        elif each in talleres["SPC"]:
            counter_2 -= 1
    if counter_2 > 0:
        return False
    if counter_1 > 0:
        if counter_1-(counter_2-avion.t2) > 0:
            return False

    return counter_1 + counter_2 <= 0


"""
def tareas2_completadas(avion, talleres, vals):
    
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    
    counter_2 = avion.t2

    for each in vals:
        if each in talleres["SPC"]:
                counter_2 -= 1

    return counter_2 <= 0
"""


def tareas1_completadas(avion, talleres, vals):
    """
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    """
    counter = 0
    counter_2 = avion.t2
    counter_1 = avion.t1
    for each in vals:
        if each not in talleres["PRK"]:
            counter += 1

    return counter - avion.t2 >= avion.t1


# Main function

def main():
    start_time = time.time()

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        return 1

    fichero = sys.argv[1]
    lineas = lector(fichero)
    problem = constraint.Problem()
    franjas = int(lineas[0].split(":")[1].strip())
    dimensiones = (lineas[1].split("x")[0], lineas[1].split("x")[1])
    talleres = process_strings_to_dict(lineas[2:5])

    aviones = creador_aviones(lineas[5:])
    dicc_var = {franja: [] for franja in range(franjas)}

    variables_jmb = {franja: [] for franja in range(franjas)}
    dicc_por_avion = {avion: [] for avion in aviones}

    for avion in aviones:
        for franja in range(franjas):
            nueva_var = f"{avion}_{franja}"
            # no sé por qué pero este orden es importante... (std,prk, spc), (prk, std,spc) funcionan,
            # pero  si es (std, spc, prk no funciona
            problem.addVariable(nueva_var,  talleres["PRK"] + talleres["STD"]  + talleres["SPC"])
            dicc_var[franja].append(nueva_var)
            dicc_por_avion[avion].append(nueva_var)
            if avion.tipo == "JMB":
                variables_jmb[franja].append(nueva_var)

    for franja, variables in variables_jmb.items():
        if variables:
            problem.addConstraint(constraint.AllDifferentConstraint(), variables)
            problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, True), variables)

    for franja in range(franjas):
        problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, False), dicc_var[franja])
        problem.addConstraint(no_mas_de_2, dicc_var[franja])
    for avion in aviones:
        problem.addConstraint(
            lambda *vals, av=avion, fr=franjas: tareas2_completadas(av, talleres, fr, vals),
            dicc_por_avion[avion]
        )

    solution = problem.getSolution()
    """ problem.addConstraint(
              lambda *vals, av=avion: tareas1_completadas(av, talleres, vals),
              dicc_por_avion[avion]
          )
  """
    """problem.addConstraint(
            lambda *vals, av=avion: tareas2_completadas(av, talleres, vals),
            dicc_por_avion[avion]
        )"""

    def format_solution(solution, talleres):
        formated_dictionary = {}
        for key, value in solution.items():
            avion_id = key.split("_")[0]  # Extrae el ID del avión desde la clave
            # Determina el tipo de taller basado en la solución encontrada
            if value in talleres["STD"]:
                tipo = "STD"
            elif value in talleres["SPC"]:
                tipo = "SPC"
            else:
                tipo = "PRK"
            # Añade la solución formateada al diccionario agrupado por ID de avión
            if avion_id not in formated_dictionary:
                formated_dictionary[avion_id] = []
            formated_dictionary[avion_id].append(f"{tipo}{value}")
        formated_dictionary = {k: formated_dictionary[k] for k in sorted(formated_dictionary)}
        # Construye la salida final de texto
        formatted_output = "N sol: 1 \nSolucion 1: \n" + "\n".join(
            f"{avion_id}: {' '.join(locations)}" for avion_id, locations in formated_dictionary.items()
        )
        print(formatted_output)
        print("\n\n \n")

    format_solution(solution, talleres)
    end_time = time.time()
    total_time = end_time-start_time
    print(f"\n\n TOTAL TIME: {total_time}")

# Problema, siempre escoge un parking primero, además siempre es el 4,4 por lo que he observado en el
# input maintenance01

if __name__ == "__main__":
    main()

# maint01: 0.007613 (4fr, 5x5, 5 av
# prueba1: 0.00171 (3 fr, 4x4, 6 av)
# prueba: 0.000525236 (2fr, 3x3, 2 av)
