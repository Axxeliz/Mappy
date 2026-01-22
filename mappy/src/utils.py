import random
from collections import deque

def generar_ciudad_completa(filas, columnas):
    # 1. Creamos el lienzo de edificios
    mapa = [[1 for _ in range(columnas)] for _ in range(filas)]
    espaciado = 3 

    # 2. Trazamos las "Avenidas" y "Calles"
    for f in range(filas):
        for c in range(columnas):
            if f % espaciado == 0 or c % espaciado == 0:
                mapa[f][c] = 0

    # 3. Agregamos AGUA (2) y BLOQUEOS (3) solo sobre las calles (0)
    for f in range(filas):
        for c in range(columnas):
            if mapa[f][c] == 0:  # Si es una calle...
                r = random.random()
                
                # 5% de que la calle sea un canal o tenga un charco (Agua)
                if r < 0.05:
                    mapa[f][c] = 2
                
                # 3% de que la calle esté cerrada por obras (Bloqueo)
                # (Usamos un rango pequeño para no cerrar toda la ciudad)
                elif r < 0.08:
                    mapa[f][c] = 3
    
    return mapa

def buscar_ruta_bfs(mapa, inicio, destino, terrenos_permitidos):
  
    filas = len(mapa)
    columnas = len(mapa[0])
    
    # Cola para el BFS: (posición_actual, camino_recorrido)
    cola = deque([(inicio, [inicio])])
    visitados = {inicio}

    while cola:
        (f_actual, c_actual), camino = cola.popleft()

        # Si llegamos al destino, devolvemos la lista de pasos
        if (f_actual, c_actual) == destino:
            return camino

        # Movimientos: Arriba, Abajo, Izquierda, Derecha
        for df, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nf, nc = f_actual + df, c_actual + dc

            # Validar que esté en el mapa, no visitado y que el terreno sea permitido
            if (0 <= nf < filas and 0 <= nc < columnas and 
                (nf, nc) not in visitados and 
                mapa[nf][nc] in terrenos_permitidos):
                
                visitados.add((nf, nc))
                cola.append(((nf, nc), camino + [(nf, nc)]))

    return None # Si no hay camino