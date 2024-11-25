# pylint: disable=all
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
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





def main():
    print("running")
    lineas = lector("/Users/raularmasserina/PycharmProjects/p2-495896-495746/parte-1/CSP-tests/maintenance01")
    talleres = process_strings_to_dict(lineas[2:5])
    print(talleres)

if __name__ == "__main__":
    main()
