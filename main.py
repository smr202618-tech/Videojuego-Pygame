import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Ascenso Infinito")

# ======================
# COLORES
# ======================
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)
AMARILLO = (255, 215, 0)
NARANJA = (255, 140, 0)
NARANJA_OSCURO = (200, 100, 0)

reloj = pygame.time.Clock()
FPS = 60

# ======================
# MÚSICA (ruta corregida)
# ======================
pygame.mixer.music.set_endevent(pygame.USEREVENT)

playlist = [
    "./assets/audio/music1.mp3",
    "./assets/audio/music2.mp3"
]

current_track = 0

def play_music(index):
    pygame.mixer.music.load(playlist[index])
    pygame.mixer.music.play()

play_music(current_track)

# ======================
# RECORD
# ======================
ARCHIVO_RECORD = "record.txt"

def cargar_record():
    if os.path.exists(ARCHIVO_RECORD):
        try:
            with open(ARCHIVO_RECORD, "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def guardar_record(valor):
    with open(ARCHIVO_RECORD, "w") as f:
        f.write(str(valor))

record = cargar_record()

# ======================
# FONDO
# ======================
def obtener_color_fondo(altura):
    if altura < 1000:
        return (135, 206, 235)
    elif altura < 5000:
        return (200, 200, 200)
    elif altura < 20000:
        return (5, 5, 20)
    else:
        return (255, 140, 0)

# ======================
# GAME OVER
# ======================
def pantalla_game_over():
    fuente_grande = pygame.font.Font(None, 90)
    fuente_peq = pygame.font.Font(None, 40)

    pantalla.fill(BLANCO)
    texto = fuente_grande.render("GAME OVER", True, NEGRO)
    sub = fuente_peq.render("Pulsa cualquier tecla para salir", True, NEGRO)

    pantalla.blit(texto, (ANCHO//2 - texto.get_width()//2, 250))
    pantalla.blit(sub, (ANCHO//2 - sub.get_width()//2, 350))
    pygame.display.flip()

    esperando = True
    while esperando:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                esperando = False

# ======================
# CLASES
# ======================
class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(AZUL)
        self.rect = self.image.get_rect(center=(ANCHO // 2, ALTO - 120))
        self.vel_x = 5
        self.vel_auto = 2
        self.vel_manual = 4
        self.vel_bajar = 8

    def update(self, velocidad_extra=0):
        self.rect.y -= (self.vel_auto + velocidad_extra)

        teclas = pygame.key.get_pressed()

        if teclas[pygame.K_w]:
            self.rect.y -= self.vel_manual

        if teclas[pygame.K_s]:
            self.rect.y += self.vel_bajar

        if teclas[pygame.K_a] and self.rect.left > 0:
            self.rect.x -= self.vel_x

        if teclas[pygame.K_d] and self.rect.right < ANCHO:
            self.rect.x += self.vel_x

        if self.rect.top < 40:
            self.rect.top = 40

        if self.rect.bottom > ALTO:
            self.rect.bottom = ALTO


class Objeto(pygame.sprite.Sprite):
    def __init__(self, ancho, alto, color):
        super().__init__()
        self.image = pygame.Surface((ancho, alto))
        self.image.fill(color)
        self.rect = self.image.get_rect(
            x=random.randint(0, ANCHO - ancho),
            y=-alto
        )
        self.velocidad = 4

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.kill()

# ======================
# GRUPOS
# ======================
todos = pygame.sprite.Group()
rojos = pygame.sprite.Group()
verdes = pygame.sprite.Group()
monedas = pygame.sprite.Group()
frenesis = pygame.sprite.Group()

jugador = Jugador()
todos.add(jugador)

altura_total = 0
enemigos_derrotados = 0

modo_protegido = False
tiempo_protegido = 0

modo_frenesi = False
tiempo_frenesi = 0

contador_spawn = 0
fuente = pygame.font.Font(None, 30)
fuente_grande = pygame.font.Font(None, 80)

ejecutando = True

# ======================
# LOOP
# ======================
while ejecutando:
    reloj.tick(FPS)

    for evento in pygame.event.get():

        # Cambio automático de canción
        if evento.type == pygame.USEREVENT:
            current_track = (current_track + 1) % len(playlist)
            play_music(current_track)

        if evento.type == pygame.QUIT:
            ejecutando = False

    # TIMERS
    if modo_protegido:
        tiempo_protegido -= 1
        if tiempo_protegido <= 0:
            modo_protegido = False

    if modo_frenesi:
        tiempo_frenesi -= 1
        if tiempo_frenesi <= 0:
            modo_frenesi = False

    # SPAWN
    contador_spawn += 1
    limite_spawn = 15 if modo_frenesi else 30

    if contador_spawn >= limite_spawn:
        r = random.randint(1, 8)

        if r == 1:
            m = Objeto(20, 20, AMARILLO)
            todos.add(m)
            monedas.add(m)

        elif r == 2:
            f = Objeto(30, 30, NARANJA)
            todos.add(f)
            frenesis.add(f)

        elif r <= 5:
            o = Objeto(50, 50, ROJO)
            todos.add(o)
            rojos.add(o)

        else:
            v = Objeto(40, 40, VERDE)
            todos.add(v)
            verdes.add(v)

        contador_spawn = 0

    velocidad_extra = 2 if modo_frenesi else 0
    jugador.update(velocidad_extra)

    for sprite in todos:
        if sprite != jugador:
            sprite.update()

    # ALTURA
    altura_total += jugador.vel_auto + velocidad_extra
    if pygame.key.get_pressed()[pygame.K_w]:
        altura_total += jugador.vel_manual

    altura = altura_total // 10

    if altura > record:
        record = altura
        guardar_record(record)

    # COLISIONES
    if pygame.sprite.spritecollide(jugador, monedas, True):
        modo_protegido = True
        tiempo_protegido = FPS * 5

    if pygame.sprite.spritecollide(jugador, frenesis, True):
        modo_frenesi = True
        tiempo_frenesi = FPS * 5

    enemigos_derrotados += len(
        pygame.sprite.spritecollide(jugador, verdes, True)
    )

    rojos_col = pygame.sprite.spritecollide(jugador, rojos, True)

    if rojos_col:
        if modo_protegido or modo_frenesi:
            enemigos_derrotados += len(rojos_col)
        else:
            pantalla_game_over()
            pygame.quit()
            sys.exit()

    # DIBUJADO
    if modo_frenesi:
        pantalla.fill(NARANJA_OSCURO)
        pygame.draw.rect(pantalla, AMARILLO, (0, 0, ANCHO, ALTO), 10)
    else:
        pantalla.fill(obtener_color_fondo(altura))

    todos.draw(pantalla)

    pantalla.blit(fuente.render(f"Altura: {altura}", True, NEGRO), (10, 10))
    pantalla.blit(fuente.render(f"Record: {record}", True, NEGRO), (10, 40))
    pantalla.blit(fuente.render(f"Enemigos: {enemigos_derrotados}", True, NEGRO), (10, 70))

    pygame.display.flip()

pygame.quit()
sys.exit()
