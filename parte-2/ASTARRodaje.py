import sys
import csv
import math
import time


class Context:
    def __init__(self, map_grid, heuristic, obstaculos):
        self.map_grid = map_grid
        self.reserved = {'cells': set(), 'edges': set(), "reached": set()}
        self.current_cost = 0
        self.closed_set = set()
        self.heuristic = heuristic
        self.h_inicial = 0
        self.obstaculos = obstaculos
        self.expanded = 0

    def is_valid_cell(self, coord, g):
        x, y = coord
        return coord in self.map_grid and coord not in self.obstaculos and \
               (x, y, g + 1) not in self.reserved['cells'] and \
               ((x, y), coord, g + 1) not in self.reserved['edges']


class NODE:
    def __init__(self, coord, g=0, h=0, parent=None):
        self.coord = coord
        self.parent = parent
        self.g = g
        self.h = h
        # tiempo en el que el avión llega a esta celda
        self.f = self.g + self.h

    def __lt__(self, other):
        return self.f < other.f


class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        """Inserta un elemento en el heap y reorganiza para mantener la propiedad del Min-Heap."""
        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def pop(self):
        """Elimina y devuelve el elemento mínimo del heap."""
        if not self.heap:
            raise IndexError("pop from empty heap")
        if len(self.heap) == 1:
            return self.heap.pop()
        # Intercambia el primer elemento con el último y elimina el mínimo
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._heapify_down(0)
        return root

    def _heapify_up(self, index):
        """Reorganiza el heap hacia arriba."""
        parent = (index - 1) // 2
        if index > 0 and self.heap[index] < self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._heapify_up(parent)

    def _heapify_down(self, index):
        """Reorganiza el heap hacia abajo."""
        smallest = index
        left_child = 2 * index + 1
        right_child = 2 * index + 2

        # Encuentra el hijo más pequeño
        if left_child < len(self.heap) and self.heap[left_child] < self.heap[smallest]:
            smallest = left_child
        if right_child < len(self.heap) and self.heap[right_child] < self.heap[smallest]:
            smallest = right_child

        # Si el hijo más pequeño es menor que el nodo actual, intercámbialos
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._heapify_down(smallest)

    def __len__(self):
        return len(self.heap)

    def __bool__(self):
        return bool(self.heap)


def heuristica_manhattan(start, goal, *args):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])


def heuristica_euclides(start, goal, *args):
    return int(math.sqrt((start[0] - goal[0]) ** 2 + (start[1] - goal[1]) ** 2))


def heuristica_propia(start, goal, context, t):
    # Calcular distancia Manhattan
    manhattan = heuristica_manhattan(start, goal)

    # Penalización por obstáculos
    penalizacion = 0

    # Coordenadas del nodo actual
    x, y = start

    # Coordenadas del objetivo
    gx, gy = goal

    # Definir qué significa "bloqueado"
    blocked = lambda coord: coord in context.obstaculos or (coord[0], coord[1], t + 1) in context.reserved["cells"] \
                            or (coord[0], coord[1]) in context.reserved["reached"]

    # Si el objetivo está por debajo del nodo
    if gy > y:
        if blocked((x, y + 1)):  # Bloqueado arriba
            if x > gx:
                if blocked((x - 1, y)):  # Bloqueado también a la izquierda
                    penalizacion += 1
                if blocked((gx + 1, gy)) and blocked((gx, gy - 1)):
                    penalizacion += 1

            elif x < gx:
                if blocked((x + 1, y)):  # Bloqueado también a la derecha
                    penalizacion += 1
                if blocked((gx - 1, gy)) and blocked((gx, gy - 1)):
                    penalizacion += 1
            # Si el objetivo está bloqueado directamente abajo

        # Penalización cuando el objetivo está por encima del nodo (y más a la izquierda)
    elif gy < y:
        if blocked((x, y - 1)):  # Bloqueado arriba
            if x > gx:
                if blocked((x - 1, y)):  # Bloqueado también a la izquierda
                    penalizacion += 1
                if blocked((gx + 1, gy)) and blocked((gx, gy + 1)):
                    penalizacion += 1
            elif x < gx:
                if blocked((x + 1, y)):  # Bloqueado también a la derecha
                    penalizacion += 1
                if blocked((gx - 1, gy)) and blocked((gx, gy + 1)):
                    penalizacion += 1


    # Penalizar la cercanía de obstáculos si están directamente en la misma dirección
    else:
        if gx > x:
            if blocked((gx - 1, gy)):
                penalizacion += 1
        else:
            if blocked((gx + 1, gy)):
                penalizacion += 1

    return manhattan + penalizacion


def camino(node):
    path = []
    while node is not None:
        path.append((node.coord, node.g))
        node = node.parent
    return path[::-1]


def formatter(path):
    if not path:
        return None
    display = ""
    for i in range(1, len(path)):
        x0, y0 = path[i - 1][0]
        x1, y1 = path[i][0]
        if x1 > x0:
            display += f"{(x0, y0)} → "
        elif x1 < x0:
            display += f"{(x0, y0)} ← "
        elif y1 > y0:
            display += f"{(x0, y0)}  ↑ "
        elif y1 < y0:
            display += f"{(x0, y0)}  ↓ "
        else:
            display += f"{(x0, y0)}  w "

    # x1, y1 = path[-1][0]  # Últimas coordenadas del camino
    display += f"{(path[-1][0])}\n"

    return display


def expand(current, context, end):
    neighbors = []
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]

    node_creator(context, current, end, moves, neighbors)

    return neighbors


def wait_posible(context, current, end, neighbors):
    x, y = current.coord
    if context.map_grid[(x, y)] == "B":
        wait_heuristic = context.heuristic((x, y), end, context, current.g + 1)
        neighbors.append(NODE((x, y), current.g + 1, wait_heuristic, current))


def node_creator(context, current, end, moves, neighbors):
    x, y = current.coord
    for dx, dy in moves:
        nx, ny = current.coord[0] + dx, current.coord[1] + dy

        heuristic = context.heuristic((nx, ny), end, context, current.g)
        if (x, y) == (nx, ny):
            wait_posible(context, current, end, neighbors)

        if context.is_valid_cell((nx, ny), current.g):
            neighbors.append(NODE(
                (nx, ny),
                current.g + 1,
                heuristic,
                current
            ))


def astar(start, goal, context):
    context.h_inicial = max(context.h_inicial, context.heuristic(start, goal, context, 0))
    start_node = NODE(start, 0, context.h_inicial, None)
    openlist = MinHeap()
    openlist.push(start_node)
    context.closed_set.clear()  # Limpiar nodos cerrados al inicio de cada búsqueda

    while openlist:
        current = openlist.pop()
        if context.reserved["reached"]:
            if current.g >= context.current_cost:
                context.current_cost += 1
                for x, y in context.reserved["reached"]:
                    context.reserved["cells"].add((x, y, context.current_cost))

        if current.coord == goal:
            return camino(current), context.expanded, current.g

        if (current.coord[0], current.coord[1], current.g) in context.closed_set:
            continue

        context.closed_set.add((current.coord[0], current.coord[1], current.g))
        context.expanded += 1
        if context.reserved["reached"]:
            if current.g >= context.current_cost:
                context.current_cost += 1
                for x, y in context.reserved["reached"]:
                    context.reserved["cells"].add((x, y, context.current_cost + 1))

        neighbors = expand(current, context, goal)
        for n in neighbors:
            openlist.push(n)

    return None, context.expanded, None


def reservar_ruta(path, reserved):
    """ evito colisiones"""
    for i in range(len(path)):
        x, y = path[i][0]
        t = path[i][1]
        reserved['cells'].add((x, y, t))
        if i > 0:
            x_prev, y_prev = path[i - 1][0]
            if (x, y) != (x_prev, y_prev):
                reserved['edges'].add(((x_prev, y_prev), (x, y), t))


def guardar_estadisticas(mapa, num_h, tiempo_total, makespan, h_inicial, nodos_expandidos, context):
    # Crear el nombre del archivo
    nombre_fichero = f"{mapa}-{num_h}.stat"

    # Crear el contenido del archivo
    contenido = (
        f"Tiempo total: {tiempo_total}s\n"
        f"Makespan: {makespan}\n"
        f"max h inicial: {h_inicial.__name__} {context.h_inicial}\n"
        f"Nodos expandidos: {nodos_expandidos}\n"
    )

    # Guardar el archivo
    with open(nombre_fichero, "w") as archivo:
        archivo.write(contenido)
    print(f"\nEstadísticas guardadas en {nombre_fichero}")


def guardar_resultado(display, mapa, num_h):
    # Crear el nombre del archivo
    nombre_fichero = f"{mapa}-{num_h}.output"
    content = ""
    for each in display:
        content += each + "\n"

    # Guardar el archivo
    with open(nombre_fichero, "w") as archivo:
        archivo.write(content)
    print(f"Resultados guardados en {nombre_fichero} \n")


def validar_traversabilidad(destiny, map_grid):
    fallo = False
    for idx, ((ox, oy), (dx, dy)) in enumerate(destiny, start=1):
        if map_grid[oy][ox] == 'G':
            print(f"Avión {idx}: La celda de inicio ({ox}, {oy}) está bloqueada.")
            fallo = True

        if map_grid[dy][dx] == 'G':
            print(f"Avión {idx}: La celda de destino ({dx}, {dy}) está bloqueada.")
            fallo = True
    if fallo:
        sys.exit(-6)


def validar_limites(destiny, map_grid):
    # ox= " origen en x " (start); dx= "destino en x" (end)
    for idx, ((ox, oy), (dx, dy)) in enumerate(destiny, start=1):
        if ox >= len(map_grid[0]) or ox < 0:
            print(f"Coordenada de inicio del avión {idx} fuera de los límites: x={ox}")
            sys.exit(-1)
        if dx >= len(map_grid[0]) or dx < 0:
            print(f"Coordenada de destino del avión {idx} fuera de los límites: x={dx}")
            sys.exit(-2)
        if oy >= len(map_grid) or oy < 0:
            print(f"Coordenada de inicio del avión {idx} fuera de los límites: y={oy}")
            sys.exit(-3)
        if dy >= len(map_grid) or dy < 0:
            print(f"Coordenada de destino del avión {idx} fuera de los límites: y={dy}")
            sys.exit(-4)


def convertir_a_diccionario(map_grid):
    """
    Convierte el map_grid (lista de listas) a un diccionario para búsquedas rápidas.
    Clave: (x, y)
    Valor: Contenido de la celda ("B", "G", "A", etc.)
    """
    map_dict = {}
    for y, fila in enumerate(map_grid):
        for x, celda in enumerate(fila):
            map_dict[(x, y)] = celda
    return map_dict


def csv_reader(csv_path):
    st_end = []
    ends = set()
    starts = set()
    map_grid = []
    i = 1
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row[0].isdigit():
                    continue
                elif "(" in row[0]:
                    coord = []
                    a, b = row.pop(1).split()
                    row.insert(1, a)
                    row.insert(2, b)
                    for each in row:
                        new_val = int(each.replace("(", "").replace(")", ""))
                        coord.append(new_val)
                    if (coord[2], coord[3]) in ends:
                        print(f"Hay aviones con mismo destino {(coord[2], coord[3])} linea: {i + 1}")
                        sys.exit(-11)
                    if (coord[1], coord[2]) in starts:
                        print(f"Hay aviones con mismo inicio {(coord[0], coord[1])} linea: {i + 1}")
                        sys.exit(-11)
                    ends.add((coord[2], coord[3]))
                    starts.add((coord[1], coord[2]))
                    st_end.append(((coord[0], coord[1]), (coord[2], coord[3])))

                else:
                    map_grid.append(row[0].split(";"))
                i += 1
        validar_limites(st_end, map_grid)
        validar_traversabilidad(st_end, map_grid)

        # Convertir map_grid a diccionario antes de devolverlo
        return st_end, convertir_a_diccionario(map_grid)
    except Exception as error:
        print(f"Error al leer el archivo: {error}")
        sys.exit(-9)


def main():
    start_time = time.time()
    if len(sys.argv) != 3:
        print("Uso: python ASTARRodaje.py <path mapa.csv> <num-h>")
        return

    csv_path = sys.argv[1]
    num_h = sys.argv[2]
    destiny, map_grid = csv_reader(csv_path)

    # Seleccionar la heurística
    if num_h == "1":
        heuristic = heuristica_manhattan
    elif num_h == "2":
        heuristic = heuristica_euclides
    else:
        heuristic = heuristica_propia

    obstaculos = {coord for coord, valor in map_grid.items() if valor == "G"}
    displays = []
    makespan = 0
    expanded = 0
    paths = []

    # Crear el contexto
    context = Context(map_grid, heuristic, obstaculos)

    for i, ((sx, sy), (gx, gy)) in enumerate(destiny):
        path, expanded, cost = astar((sx, sy), (gx, gy), context)
        if path is None:
            print("No se encontró solución para el avión", i + 1)
            return
        reservar_ruta(path, context.reserved)
        context.reserved["reached"].add((gx, gy))
        paths.append(path)
        expanded += expanded
        makespan = max(makespan, cost)
        context.current_cost = makespan

    for each in paths:
        while len(each) < makespan + 1:
            each.append(each[-1])
        displays.append(formatter(each))

    final = time.time()
    total_time = final - start_time
    guardar_estadisticas(csv_path, num_h, total_time, makespan, heuristic, expanded, context)
    guardar_resultado(displays, csv_path, num_h)


if __name__ == "__main__":
    main()
