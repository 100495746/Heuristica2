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


def creador_aviones(l_codigos):
    return [Avion(each) for each in l_codigos]


def adyacentes(proposed, dimensiones, jmb):
    occupied = 0
    for each in set(proposed):
        if (each[0], each[1] + 1) in proposed:
            occupied += 1
        if (each[0] + 1, each[1]) in proposed:
            occupied += 1
        if (each[0], each[1] - 1) in proposed:
            occupied += 1
        if (each[0] - 1, each[1]) in proposed:
            occupied += 1

        if jmb and occupied > 0: return False
        if each[0] in [0, dimensiones] and each[1] in [0, dimensiones] and occupied >= 2:
            return False
        if ((each[0] in [0, dimensiones]) or (each[1] in [0, dimensiones])) and occupied >= 3:
            return False
        if occupied >= 4:
            return False
    return True


def process_strings_to_dict(strings):
    talleres = {}
    for line in strings:
        key, coords = line.split(":")  # Separar la clave y las coordenadas
        key = key.strip()  # Limpiar espacios en la clave
        # Convertir las coordenadas a tuplas y almacenarlas en un set
        coordinates = {tuple(int(x) for x in coord.strip("()").split(",")) for coord in coords.strip().split()}
        talleres[key] = set(coordinates)
    return talleres


def format_solution(solution, talleres, i):
    formated_dictionary = {}
    for key, value in solution.items():
        avion_id = key.split("_")[0]  # Extrae el ID del avión
        tipo = "STD" if value in talleres["STD"] else "SPC" if value in talleres["SPC"] else "PRK"
        formated_dictionary.setdefault(avion_id, []).append(f"{tipo}{value}")

    formatted_output = f"Solucion {i}: \n" + "\n".join(
        f"{avion_id}: {' '.join(locations)}" for avion_id, locations in formated_dictionary.items()
    )
    print(formatted_output)


def tareas1_completadas(avion, talleres, vals):
    """
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    """
    counter = sum(1 for each in vals if each not in talleres["PRK"])
    return counter - avion.t2 >= avion.t1


def tareas2_completadas(avion, talleres, di, vals):
    """
    Asegura que todos los aviones tengan T1 y T2 igual a 0 al final de las franjas.
    """
    counter_2 = avion.t2
    counter_1 = avion.t1
    prk_count = 0
    for each in vals:
        if each in set(talleres["PRK"]):
            prk_count += 1
        elif each in set(talleres["STD"]):
            counter_1 -= 1
        elif each in set(talleres["SPC"]):
            counter_2 -= 1

    if di - prk_count < counter_1 + counter_2:
        return False
    if counter_2 > 0:
        return False
    if counter_1 > 0:
        if counter_1 - (counter_2 - avion.t2) > 0:
            return False
    return counter_1 + counter_2 <= 0


def tareas_2_primero(avion, talleres, vals):
    # Si el avión no tiene restricciones, no se aplica la prioridad
    if not avion.restr:
        return True

    # Si el avión tiene restricciones, verificamos que todas las T2 se hagan antes de las T1
    t2_left = avion.t2
    t2_done = False

    # Convertir talleres["SPC"] y talleres["STD"] en sets para mayor eficiencia
    spc_set = set(talleres["SPC"])
    std_set = set(talleres["STD"])

    for val in vals:
        if val in spc_set:
            t2_left -= 1
            if t2_left == 0:
                t2_done = True  # Encontramos una tarea de tipo 2
        elif val in std_set and not t2_done:
            # Si encontramos una tarea de tipo 1 antes de una tarea de tipo 2, devolvemos False
            return False

    return True


def main():
    start_time = time.time()

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        return

    fichero = sys.argv[1]
    lineas = lector(fichero)
    problem = constraint.Problem()

    franjas = int(lineas[0].split(":")[1].strip())
    dimensiones = tuple(map(int, lineas[1].split("x")))
    talleres = process_strings_to_dict(lineas[2:5])

    aviones = creador_aviones(lineas[5:])
    dicc_var = {franja: [] for franja in range(franjas)}
    variables_jmb = {franja: [] for franja in range(franjas)}
    dicc_por_avion = {avion: [] for avion in aviones}

    # Precompute the combined list of all available locations in talleres
    all_locations = tuple(talleres["STD"] | talleres["SPC"] | talleres["PRK"])

    for avion in aviones:
        for franja in range(franjas):
            nueva_var = f"{avion}_{franja}"
            problem.addVariable(nueva_var, all_locations)  # Use precomputed list
            dicc_var[franja].append(nueva_var)
            dicc_por_avion[avion].append(nueva_var)

            if avion.tipo == "JMB":
                variables_jmb[franja].append(nueva_var)

    for avion in aviones:
        problem.addConstraint(
            lambda *vals, av=avion, fr=franjas: tareas2_completadas(av, talleres, fr, vals),
            dicc_por_avion[avion]
        )
        problem.addConstraint(
            lambda *vals, av=avion: tareas_2_primero(av, talleres, vals),
            dicc_por_avion[avion]
        )

    # Combine and batch application of time slot constraints
    for franja in range(franjas):
        vars_in_franja = dicc_var[franja]
        problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, False), vars_in_franja)

    # Combine constraints for JMB airplanes
    for franja, variables in variables_jmb.items():
        if variables:
            problem.addConstraint(constraint.AllDifferentConstraint(), variables)
            problem.addConstraint(lambda *vals: adyacentes(vals, dimensiones, True), variables)

    for franja in dicc_var.keys():
        # Para cada franja, verifique que ningún taller tenga más de 2 aviones asignados
        # Unificar todos los talleres en un set
        problem.addConstraint(
            lambda *vals: all(vals.count(taller) <= 2 for taller in set(vals)), dicc_var[franja])

    one_solution = problem.getSolution()
    if one_solution is None:
        print("No hay soluciones para este caso")
        return

    format_solution(one_solution, talleres, 1)
    print("Encontrando otras soluciones...")
    solutions = problem.getSolutionIter()

    generated_solutions = set()
    i = 0
    listed = []

    for solution in solutions:
        solution_tuple = tuple(solution.items())
        if solution_tuple not in generated_solutions:
            i += 1
            generated_solutions.add(solution_tuple)
            if i < 9:
                listed.append((solution, talleres, i))

    print(f"N sol: {i} \n")

    for each in listed:
        format_solution(*each)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n\nTOTAL TIME: {total_time}")


if __name__ == "__main__":
    main()
