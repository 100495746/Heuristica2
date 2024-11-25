# pylint: disable=all
import sys


class Avion:
    def __init__(self, codigo):
        self.id = int(codigo[0])
        self.tipo = codigo[2:5]
        self.restr = bool(codigo[6] == "T")
        self.t1 = int(codigo[8:codigo.find("-", 8)])
        self.t2 = int(codigo[codigo.find("-", 8) + 1:])
    def __str__(self):
        return str(self.id) + str(self.tipo) + str(self.restr) + str(self.t1) + " - " + str(self.t2)


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

    franjas = int(lineas[0].split(":")[1].strip())
    x, y = lineas[1].split("x")
    dimensiones = (int(x), int(y))
    process_strings_to_dict(lineas[2:5])
    aviones = creador_aviones(lineas[5:])













    return 0


if __name__ == "__main__":
    main()
