import customtkinter as ctk
import config
from utils import generar_ciudad_completa, buscar_ruta_bfs 

class MappyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(config.TITULO_APP)
        self.geometry(f"{config.ANCHO_VENTANA}x{config.ALTO_VENTANA}")
        
        # VARIABLES DE ESTADO
        self.mapa_datos = []
        self.botones_grilla = {}
        self.punto_inicio = None   # Guardará (fila, col)
        self.punto_destino = None  # Guardará (fila, col)

        # INTERFAZ
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Mappy v1.0", font=("Arial", 20, "bold")).pack(pady=20)

        self.entry_tamano = ctk.CTkEntry(self.sidebar, placeholder_text="Tamaño (impar ej. 15)")
        self.entry_tamano.pack(pady=10)

        self.btn_generar = ctk.CTkButton(self.sidebar, text="Generar Ciudad", command=self.crear_visualizacion_mapa)
        self.btn_generar.pack(pady=10)

        self.btn_calcular = ctk.CTkButton(self.sidebar, text="Calcular Ruta", command=self.analizar_rutas)
        self.btn_calcular.pack(pady=10)

        # Label informativo para el usuario
        self.label_info = ctk.CTkLabel(self.sidebar, text="1. Genera un mapa\n2. Clic para Inicio\n3. Clic para Destino", wraplength=150)
        self.label_info.pack(pady=20)

        self.contenedor_mapa = ctk.CTkFrame(self)
        self.contenedor_mapa.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    def crear_visualizacion_mapa(self):
        try:
            n = int(self.entry_tamano.get())
            if n % 2 == 0: n += 1 # Forzamos que sea impar para que el DFS luzca mejor
        except ValueError:
            return

        # Limpiar datos previos
        for widget in self.contenedor_mapa.winfo_children():
            widget.destroy()
        self.botones_grilla = {}
        self.punto_inicio = None
        self.punto_destino = None
        self.label_info.configure(text="Selecciona punto de INICIO")

        # Generar matriz lógica
        self.mapa_datos = generar_ciudad_completa(n, n)

        # Dibujar botones
        for f in range(n):
            for c in range(n):
                valor = self.mapa_datos[f][c]
                
                # Asignar color según config.py
                if valor == 0: color = config.COLOR_CALLE
                elif valor == 1: color = config.COLOR_EDIFICIO
                elif valor == 2: color = config.COLOR_AGUA
                else: color = config.COLOR_BLOQUEO
                
                btn = ctk.CTkButton(
                    self.contenedor_mapa, text="", width=20, height=20,
                    fg_color=color, hover_color=color, corner_radius=2,
                    command=lambda r=f, col=c: self.seleccionar_punto(r, col)
                )
                btn.grid(row=f, column=c, padx=1, pady=1)
                self.botones_grilla[(f, c)] = btn

    def seleccionar_punto(self, f, c):
        
        if self.mapa_datos[f][c] not in [0, 2]:
            return

        if self.punto_inicio is not None and self.punto_destino is not None:
            # Quitamos los caminos amarillos/púrpuras
            self.limpiar_caminos()
            # Restauramos el color original del Inicio anterior
            fi, ci = self.punto_inicio
            val_i = self.mapa_datos[fi][ci]
            color_i = config.COLOR_CALLE if val_i == 0 else config.COLOR_AGUA
            self.botones_grilla[(fi, ci)].configure(fg_color=color_i)
            
            # Restauramos el color original del Destino anterior
            fd, cd = self.punto_destino
            val_d = self.mapa_datos[fd][cd]
            color_d = config.COLOR_CALLE if val_d == 0 else config.COLOR_AGUA
            self.botones_grilla[(fd, cd)].configure(fg_color=color_d)
            
            # Limpiamos las variables para empezar de cero
            self.punto_inicio = None
            self.punto_destino = None

        if self.punto_inicio is None:
            # Ponemos el nuevo inicio
            self.punto_inicio = (f, c)
            self.botones_grilla[(f, c)].configure(fg_color=config.COLOR_INICIO)
            self.label_info.configure(text="Punto de inicio fijado.\nSelecciona el DESTINO")
            
        elif self.punto_destino is None and (f, c) != self.punto_inicio:
            # Ponemos el nuevo destino
            self.punto_destino = (f, c)
            self.botones_grilla[(f, c)].configure(fg_color=config.COLOR_DESTINO)
            self.label_info.configure(text="Destino seleccionado, ver rutas posibles.")

    def limpiar_caminos(self):
        if not self.mapa_datos:
            return

        for (f, c), btn in self.botones_grilla.items():
            # Si es el inicio o destino, no los tocamos
            if (f, c) == self.punto_inicio or (f, c) == self.punto_destino:
                continue
            
            # Obtenemos el valor original del terreno
            valor = self.mapa_datos[f][c]
            
            # Restauramos el color según config.py
            if valor == 0: color = config.COLOR_CALLE
            elif valor == 1: color = config.COLOR_EDIFICIO
            elif valor == 2: color = config.COLOR_AGUA
            elif valor == 3: color = config.COLOR_BLOQUEO
            
            btn.configure(fg_color=color)
    
    def analizar_rutas(self):
        # 1. Validación: Si no hay puntos marcados, no hacemos nada
        if self.punto_inicio is None or self.punto_destino is None:
            self.label_info.configure(text="Error: Selecciona Inicio y Destino")
            return

        # Importamos la función desde utils.py
        from utils import buscar_ruta_bfs

        # 2. ESCENARIO A: Ruta solo por calles (terreno 0)
        ruta_limpia = buscar_ruta_bfs(self.mapa_datos, self.punto_inicio, self.punto_destino, [0])

        # 3. ESCENARIO B: Ruta por calles y agua (terrenos 0 y 2)
        ruta_agua = buscar_ruta_bfs(self.mapa_datos, self.punto_inicio, self.punto_destino, [0, 2])

        # 4. Dibujamos los resultados
        if ruta_limpia:
            self.dibujar_ruta(ruta_limpia, config.COLOR_CAMINO_RAPIDO)
            self.label_info.configure(text="ruta mas corta encontrada, desea iniciar su viaje? ...")
        else:
            self.label_info.configure(text="No existe ruta solo por calles")

        # 5. Lógica de comparación: ¿Es más corto ir por el agua?
        if ruta_limpia and ruta_agua:
            if len(ruta_agua) < len(ruta_limpia):
                ahorro = len(ruta_limpia) - len(ruta_agua)
                self.label_info.configure(text=f"¡Atención!\nPor el agua ahorras {ahorro} pasos.")
                self.dibujar_ruta(ruta_agua, config.COLOR_CAMINO_AGUA)

    def dibujar_ruta(self, ruta, color):
        if not ruta:
            return

        for f, c in ruta:
            # Solo pintamos si no es el punto de inicio ni el de destino
            if (f, c) != self.punto_inicio and (f, c) != self.punto_destino:
                # Usamos nuestro diccionario para encontrar el botón rápidamente
                self.botones_grilla[(f, c)].configure(fg_color=color)

# Ejecutar
if __name__ == "__main__":
    app = MappyApp()
    app.mainloop()