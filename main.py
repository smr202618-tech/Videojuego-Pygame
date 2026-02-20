import pygame
import sys
import random
import subprocess
import json
from pathlib import Path

# ======================================================
# CONFIGURACIÓN E INICIALIZACIÓN (NO RECORTADO)
# ======================================================
pygame.init()
pygame.mixer.init()  # Inicializar el mezclador de audio

ANCHO, ALTO = 900, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Rocket Ascent: Mega Fusion Gold Edition")

reloj = pygame.time.Clock()
FPS = 60

# ======================================================
# FUNCIONES DE AUDIO
# ======================================================
def start_main_game_music():
    try:
        pygame.mixer.music.load('./assets/audio/music1.mp3')
        pygame.mixer.music.play(-1)  # Bucle infinito
    except pygame.error:
        print("Error: No se pudo cargar music1.mp3")

def start_minigame_music():
    try:
        pygame.mixer.music.load('./assets/audio/music2.mp3')
        pygame.mixer.music.play(-1)  # Bucle infinito
    except pygame.error:
        print("Error: No se pudo cargar music2.mp3")

# ======================================================
# CONSTANTES DE MUNDO Y FÍSICAS
# ======================================================
PIXELS_POR_METRO = 12.5
VEL_LATERAL = 7

# NUEVA FÍSICA CON INERCIA (NO REEMPLAZA, AMPLÍA)
ACELERACION = 0.6
FRICCION = 0.93
VELOCIDAD_MAX = 8
GRAVEDAD = 0.25

# COLORES Y ESTÉTICA
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (220, 50, 50)
VERDE = (50, 220, 50)
AZUL = (0, 100, 255)
AMARILLO = (255, 215, 0)
NARANJA = (255, 140, 0)
FUEGO = (255, 170, 60)
CIELO_BAJO = (140, 190, 255)
CIELO_MEDIO = (90, 145, 235)
CIELO_ALTO = (60, 100, 200)
ESPACIO = (5, 5, 20)
RUTA_GUARDADO = Path('./partida_guardada.json')


def cargar_sprites_meteoritos():
    rutas_preferidas = [
        Path(f"./assets/sprites/meteorito{i}.png") for i in range(1, 5)
    ]
    rutas = [ruta for ruta in rutas_preferidas if ruta.exists()]

    if not rutas:
        rutas = sorted(Path('./assets/sprites').glob('meteorito*.png'))

    if not rutas:
        rutas = sorted(Path('./assets/sprites').glob('metorito*.png'))

    sprites = []
    for ruta in rutas:
        try:
            sprites.append(pygame.image.load(str(ruta)).convert_alpha())
        except pygame.error:
            continue

    return sprites


def crear_imagen_meteorito(tamano):
    if SPRITES_METEORITOS:
        base = random.choice(SPRITES_METEORITOS)
        meteorito = pygame.transform.smoothscale(base, (tamano, tamano))
        return pygame.transform.rotate(meteorito, random.randint(0, 359))

    fallback = pygame.Surface((tamano, tamano), pygame.SRCALPHA)
    pygame.draw.circle(fallback, NARANJA, (tamano // 2, tamano // 2), tamano // 2)
    return fallback

# ======================================================
# VARIABLES DE ESTADO GLOBALES
# ======================================================
metros = 0
monedas_totales = 0
monedas_para_minijuego = 0
nivel = 1
velocidad_global = 3.0
juego_iniciado = False
camara_y = 0.0

pool_minijuegos = ["lluvia", "laberinto", "esquiva", "verdes", "supervivencia"]
random.shuffle(pool_minijuegos)

# NUEVOS ELEMENTOS ESPACIALES
luna_y = -900
planetas = []
estrellas = []
SPRITES_METEORITOS = cargar_sprites_meteoritos()

# ======================================================
# CLASE JUGADOR (INERCIA REAL Y MOVIMIENTO COMPLETO)
# ======================================================
class Cohete(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        sprite_base = pygame.image.load('./assets/sprites/sprite.png').convert_alpha()
        self.image = pygame.transform.smoothscale(sprite_base, (40, 65))
        self.rect = self.image.get_rect(center=(ANCHO//2, ALTO - 120))
        self.escudo = False

        # NUEVAS VARIABLES DE VELOCIDAD
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        teclas = pygame.key.get_pressed()

        # Aceleración horizontal
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.vel_x -= ACELERACION
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.vel_x += ACELERACION

        # Vertical SIEMPRE activo (modo normal y minijuego)
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.vel_y -= ACELERACION * 1.4
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.vel_y += ACELERACION

        # Gravedad ligera constante
        self.vel_y += GRAVEDAD

        # Limitar velocidades
        self.vel_x = max(-VELOCIDAD_MAX, min(VELOCIDAD_MAX, self.vel_x))
        self.vel_y = max(-VELOCIDAD_MAX, min(VELOCIDAD_MAX, self.vel_y))

        # Aplicar fricción
        self.vel_x *= FRICCION
        self.vel_y *= FRICCION

        # Aplicar movimiento
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        self.rect.clamp_ip(pantalla.get_rect())

    def draw(self, surf):
        surf.blit(self.image, self.rect)

        # Fuego animado mejorado
        for _ in range(5):
            f_x = self.rect.centerx + random.randint(-8, 8)
            f_y = self.rect.bottom + random.randint(2, 20)
            pygame.draw.circle(surf, FUEGO,
                               (f_x, f_y), random.randint(4, 10))

# ======================================================
# FONDO DINÁMICO CON LUNA, PLANETAS Y PARALLAX
# ======================================================
def dibujar_fondo_dinamico():
    h = abs(camara_y) / PIXELS_POR_METRO

    if h < 150:
        factor = h / 150
        color = [int(CIELO_BAJO[i] + (CIELO_MEDIO[i] - CIELO_BAJO[i]) * factor) for i in range(3)]
    elif h < 400:
        factor = (h - 150) / 250
        color = [int(CIELO_MEDIO[i] + (CIELO_ALTO[i] - CIELO_MEDIO[i]) * factor) for i in range(3)]
    elif h < 800:
        factor = (h - 400) / 400
        color = [int(CIELO_ALTO[i] + (ESPACIO[i] - CIELO_ALTO[i]) * factor) for i in range(3)]
    else:
        color = ESPACIO

    pantalla.fill(color)

    # Estrellas reales generadas una vez
    if not estrellas:
        for _ in range(80):
            estrellas.append((random.randint(0, ANCHO),
                              random.randint(0, ALTO)))

    if h > 250:
        for ex, ey in estrellas:
            pygame.draw.circle(
                pantalla,
                BLANCO,
                (ex, int(ey - camara_y * 0.1) % ALTO),
                1
            )

    # Luna
    pygame.draw.circle(
        pantalla,
        (230, 230, 230),
        (ANCHO - 150, int(luna_y - camara_y * 0.3)),
        60
    )

    # Planetas con parallax
    for planeta in planetas:
        px = planeta["x"]
        py = planeta["y"] - camara_y * 0.2
        pygame.draw.circle(
            pantalla,
            planeta["color"],
            (int(px), int(py)),
            planeta["radio"]
        )
# ======================================================
# LOS 5 MINIJUEGOS (COMPLETOS Y AJUSTADOS)
# ======================================================

def minijuego_lluvia():
    start_minigame_music() # CAMBIO DE MÚSICA
    p = Cohete()
    enemigos = pygame.sprite.Group()
    inicio = pygame.time.get_ticks()

    while pygame.time.get_ticks() - inicio < 8000:
        reloj.tick(FPS)
        pantalla.fill((30, 30, 50))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Spawn menos agresivo
        if random.randint(1, 8) == 1:
            en = pygame.sprite.Sprite()
            en.image = crear_imagen_meteorito(25)
            en.rect = en.image.get_rect(
                center=(random.randint(0, ANCHO), -30))
            enemigos.add(en)

        # Velocidad reducida
        for en in enemigos:
            en.rect.y += 6

        p.update()

        if pygame.sprite.spritecollide(p, enemigos, False):
            start_main_game_music() # RESTAURAR MÚSICA
            return False

        enemigos.draw(pantalla)
        p.draw(pantalla)
        pygame.display.flip()

    start_main_game_music() # RESTAURAR MÚSICA
    return True


def minijuego_laberinto():
    start_minigame_music() # CAMBIO DE MÚSICA
    p = Cohete()
    p.rect.topleft = (40, 40)

    meta = pygame.Rect(ANCHO-110, ALTO-110, 70, 70)

    paredes = [
        pygame.Rect(180, 0, 40, 500),
        pygame.Rect(420, 200, 40, 500),
        pygame.Rect(680, 0, 40, 550)
    ]

    while not p.rect.colliderect(meta):
        reloj.tick(FPS)
        pantalla.fill((10, 10, 15))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        p.update()

        for pared in paredes:
            pygame.draw.rect(pantalla, AZUL, pared)
            if p.rect.colliderect(pared):
                start_main_game_music() # RESTAURAR MÚSICA
                return False

        pygame.draw.rect(pantalla, VERDE, meta)
        p.draw(pantalla)
        pygame.display.flip()

    start_main_game_music() # RESTAURAR MÚSICA
    return True


def minijuego_esquiva():
    start_minigame_music() # CAMBIO DE MÚSICA
    p = Cohete()
    enemigos = pygame.sprite.Group()
    inicio = pygame.time.get_ticks()

    while pygame.time.get_ticks() - inicio < 7500:
        reloj.tick(FPS)
        pantalla.fill((50, 10, 10))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Spawn reducido
        if random.randint(1, 10) == 1:
            en = pygame.sprite.Sprite()
            en.image = crear_imagen_meteorito(35)
            en.rect = en.image.get_rect(
                center=(random.randint(0, ANCHO), -30))
            enemigos.add(en)

        # Velocidad ligeramente menor
        for en in enemigos:
            en.rect.y += 8

        p.update()

        if pygame.sprite.spritecollide(p, enemigos, False):
            start_main_game_music() # RESTAURAR MÚSICA
            return False

        enemigos.draw(pantalla)
        p.draw(pantalla)
        pygame.display.flip()

    start_main_game_music() # RESTAURAR MÚSICA
    return True


def minijuego_verdes():
    start_minigame_music() # CAMBIO DE MÚSICA
    p = Cohete()
    items = pygame.sprite.Group()
    recolectados = 0
    fuente = pygame.font.SysFont(None, 40)

    while recolectados < 10:
        reloj.tick(FPS)
        pantalla.fill((10, 45, 10))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Spawn menos frecuente
        if random.randint(1, 20) == 1:
            it = pygame.sprite.Sprite()
            it.image = pygame.Surface((25, 25), pygame.SRCALPHA)
            pygame.draw.circle(it.image, VERDE, (12, 12), 12)
            it.rect = it.image.get_rect(
                center=(random.randint(50, ANCHO-50),
                        random.randint(50, ALTO-50)))
            items.add(it)

        p.update()

        if pygame.sprite.spritecollide(p, items, True):
            recolectados += 1

        txt = fuente.render(
            f"Bio-muestras: {recolectados}/10", True, BLANCO)

        items.draw(pantalla)
        p.draw(pantalla)
        pantalla.blit(txt, (20, 20))
        pygame.display.flip()

    start_main_game_music() # RESTAURAR MÚSICA
    return True


def minijuego_supervivencia():
    start_minigame_music() # CAMBIO DE MÚSICA
    p = Cohete()
    drones = pygame.sprite.Group()
    inicio = pygame.time.get_ticks()

    while pygame.time.get_ticks() - inicio < 11000:
        reloj.tick(FPS)
        pantalla.fill((5, 5, 5))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if random.randint(1, 20) == 1:
            d = pygame.sprite.Sprite()
            d.image = pygame.Surface((20, 20))
            d.image.fill(AMARILLO)
            d.rect = d.image.get_rect(
                center=(random.choice([0, ANCHO]),
                        random.randint(0, ALTO)))
            drones.add(d)

        for d in drones:
            vel = 2.2

            # IA con margen de error
            if random.random() < 0.85:
                dx = vel if p.rect.x > d.rect.x else -vel
                dy = vel if p.rect.y > d.rect.y else -vel
            else:
                dx = random.choice([-vel, vel])
                dy = random.choice([-vel, vel])

            d.rect.x += dx
            d.rect.y += dy

        p.update()

        if pygame.sprite.spritecollide(p, drones, False):
            start_main_game_music() # RESTAURAR MÚSICA
            return False

        drones.draw(pantalla)
        p.draw(pantalla)
        pygame.display.flip()

    start_main_game_music() # RESTAURAR MÚSICA
    return True
# ======================================================
# SISTEMA DE EVENTOS Y ALEATORIEDAD (BARAJA)
# ======================================================
def activar_evento_aleatorio():
    global pool_minijuegos, velocidad_global, nivel

    if not pool_minijuegos:
        pool_minijuegos = ["lluvia", "laberinto", "esquiva", "verdes", "supervivencia"]
        random.shuffle(pool_minijuegos)

    seleccion = pool_minijuegos.pop()

    # Pantalla de transición
    pantalla.fill(NEGRO)
    f = pygame.font.SysFont(None, 80)
    aviso = f.render(f"¡{seleccion.upper()}!", True, AMARILLO)
    pantalla.blit(aviso, (ANCHO//2 - aviso.get_width()//2, ALTO//2 - 40))
    pygame.display.flip()
    pygame.time.delay(1200)

    juegos = {
        "lluvia": minijuego_lluvia,
        "laberinto": minijuego_laberinto,
        "esquiva": minijuego_esquiva,
        "verdes": minijuego_verdes,
        "supervivencia": minijuego_supervivencia
    }

    exito = juegos[seleccion]()
    if exito:
        nivel += 1
        velocidad_global += 0.5
        return True
    return False


# ======================================================
# LÓGICA DE GAME OVER
# ======================================================
def mostrar_game_over():
    global nivel
    fuente_g = pygame.font.SysFont(None, 100)
    fuente_p = pygame.font.SysFont(None, 50)
    nivel = 1
    
    # Detener música al morir si se desea, o dejarla.
    # pygame.mixer.music.stop() 

    while True:
        pantalla.fill(NEGRO)

        txt1 = fuente_g.render("MISIÓN FALLIDA", True, ROJO)
        txt2 = fuente_p.render(f"Altura alcanzada: {int(metros)}m", True, BLANCO)
        txt3 = fuente_p.render("Pulsa Enter para acceder al menu principal", True, VERDE)

        pantalla.blit(txt1, (ANCHO//2 - txt1.get_width()//2, 200))
        pantalla.blit(txt2, (ANCHO//2 - txt2.get_width()//2, 320))
        pantalla.blit(txt3, (ANCHO//2 - txt3.get_width()//2, 400))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                pygame.quit()
                subprocess.Popen([sys.executable, 'menu.py'])
                return


def guardar_partida(jugador):
    datos = {
        "metros": metros,
        "monedas_totales": monedas_totales,
        "monedas_para_minijuego": monedas_para_minijuego,
        "nivel": nivel,
        "velocidad_global": velocidad_global,
        "juego_iniciado": juego_iniciado,
        "camara_y": camara_y,
        "jugador_x": jugador.rect.x,
        "jugador_y": jugador.rect.y,
        "jugador_vel_x": jugador.vel_x,
        "jugador_vel_y": jugador.vel_y,
    }

    with RUTA_GUARDADO.open('w', encoding='utf-8') as archivo:
        json.dump(datos, archivo, indent=2)


def mostrar_menu_pausa(jugador):
    opciones = ["Guardar", "Reiniciar", "Salir"]
    indice = 0
    fuente_titulo = pygame.font.SysFont(None, 70)
    fuente_opcion = pygame.font.SysFont(None, 46)
    fuente_info = pygame.font.SysFont(None, 34)
    guardado_ok = False

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return "salir"
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                    return "continuar"
                if evento.key in (pygame.K_UP, pygame.K_w):
                    indice = (indice - 1) % len(opciones)
                if evento.key in (pygame.K_DOWN, pygame.K_s):
                    indice = (indice + 1) % len(opciones)
                if evento.key == pygame.K_RETURN:
                    seleccion = opciones[indice]

                    if seleccion == "Guardar":
                        guardar_partida(jugador)
                        guardado_ok = True
                    elif seleccion == "Reiniciar":
                        return "reiniciar"
                    elif seleccion == "Salir":
                        return "salir"

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        pantalla.blit(overlay, (0, 0))

        titulo = fuente_titulo.render("PAUSA", True, BLANCO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 170))

        for i, opcion in enumerate(opciones):
            color = AMARILLO if i == indice else BLANCO
            texto = fuente_opcion.render(opcion, True, color)
            pantalla.blit(texto, (ANCHO // 2 - texto.get_width() // 2, 280 + i * 65))

        ayuda = fuente_info.render("Usa flechas/W-S y Enter. ESC/P para continuar", True, BLANCO)
        pantalla.blit(ayuda, (ANCHO // 2 - ayuda.get_width() // 2, 520))

        if guardado_ok:
            msg = fuente_info.render("Partida guardada en partida_guardada.json", True, VERDE)
            pantalla.blit(msg, (ANCHO // 2 - msg.get_width() // 2, 560))

        pygame.display.flip()
        reloj.tick(FPS)


# ======================================================
# BUCLE PRINCIPAL DEL JUEGO
# ======================================================
def main():
    global metros, monedas_totales, monedas_para_minijuego
    global velocidad_global, juego_iniciado, camara_y
    global planetas

    # Iniciar música principal
    start_main_game_music()

    # Reinicio completo de estado
    metros = 0
    monedas_totales = 0
    monedas_para_minijuego = 0
    velocidad_global = 3.0
    juego_iniciado = False
    camara_y = 0.0
    planetas = []

    # Generar planetas al iniciar partida
    for _ in range(4):
        planetas.append({
            "x": random.randint(100, ANCHO - 100),
            "y": random.randint(-2500, -400),
            "radio": random.randint(30, 70),
            "color": random.choice([
                (200, 200, 255),
                (255, 180, 180),
                (180, 255, 200),
                (255, 220, 150)
            ])
        })

    jugador = Cohete()
    monedas = pygame.sprite.Group()
    obstaculos = pygame.sprite.Group()

    while True:
        reloj.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    juego_iniciado = True
                if evento.key in (pygame.K_ESCAPE, pygame.K_p) and juego_iniciado:
                    decision = mostrar_menu_pausa(jugador)
                    if decision == "reiniciar":
                        return "reiniciar"
                    if decision == "salir":
                        pygame.quit()
                        subprocess.Popen([sys.executable, 'menu.py'])
                        return "salir"

        if juego_iniciado:
            camara_y -= velocidad_global
            metros = abs(camara_y) / PIXELS_POR_METRO

            # Movimiento con nueva física
            jugador.update()

            # Generación de monedas
            if random.randint(1, 45) == 1:
                m = pygame.sprite.Sprite(monedas)
                m.image = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(m.image, AMARILLO, (10, 10), 10)
                m.rect = m.image.get_rect(
                    center=(random.randint(50, ANCHO-50), -30)
                )

            # Generación de obstáculos
            if random.randint(1, 65) == 1:
                o = pygame.sprite.Sprite(obstaculos)
                o.image = crear_imagen_meteorito(35)
                o.rect = o.image.get_rect(
                    center=(random.randint(50, ANCHO-50), -30)
                )

            # Movimiento relativo al ascenso
            for s in list(monedas) + list(obstaculos):
                s.rect.y += velocidad_global + 2
                if s.rect.top > ALTO:
                    s.kill()

            # Colisiones
            if pygame.sprite.spritecollide(jugador, obstaculos, False):
                mostrar_game_over()

            if pygame.sprite.spritecollide(jugador, monedas, True):
                monedas_totales += 1
                monedas_para_minijuego += 1

                if monedas_para_minijuego >= 5:
                    monedas_para_minijuego = 0
                    if not activar_evento_aleatorio():
                        mostrar_game_over()

        # RENDERIZADO
        dibujar_fondo_dinamico()

        suelo_y = (ALTO - 80) - camara_y
        if suelo_y < ALTO + 100:
            pygame.draw.rect(
                pantalla,
                (100, 100, 100),
                (ANCHO//2 - 100, suelo_y, 200, 20)
            )
            pygame.draw.rect(
                pantalla,
                (80, 150, 80),
                (0, suelo_y + 20, ANCHO, 500)
            )

        monedas.draw(pantalla)
        obstaculos.draw(pantalla)
        jugador.draw(pantalla)

        # HUD
        f_hud = pygame.font.SysFont(None, 30)
        c_txt = BLANCO if metros > 300 else NEGRO

        pantalla.blit(
            f_hud.render(f"ALTURA: {int(metros)}m", True, c_txt),
            (20, 20)
        )
        pantalla.blit(
            f_hud.render(f"MONEDAS: {monedas_totales}", True, AMARILLO),
            (20, 50)
        )
        pantalla.blit(
            f_hud.render(f"NIVEL: {nivel}", True, c_txt),
            (20, 80)
        )

        if not juego_iniciado:
            msg = f_hud.render(
                "PULSA ESPACIO PARA INICIAR EL DESPEGUE",
                True,
                NEGRO
            )
            pantalla.blit(
                msg,
                (ANCHO//2 - msg.get_width()//2, ALTO//2)
            )

        pygame.display.flip()


if __name__ == "__main__":
    while True:
        estado = main()
        if estado != "reiniciar":
            break
