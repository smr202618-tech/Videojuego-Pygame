import pygame
import subprocess
import sys
import os

pygame.init()

ANCHO, ALTO = 900, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("ping.internacional")
reloj = pygame.time.Clock()
fuente_titulo = pygame.font.SysFont(None, 70)
fuente_boton = pygame.font.SysFont(None, 48)

# Colores
FONDO = (15, 18, 28)
DORADO = (255, 215, 0)
BLANCO = (255, 255, 255)
ROJO = (220, 50, 50)
ROJO_HOVER = (255, 70, 70)
ROJO_OSCURO = (150, 30, 30)

# Cargar imagen de fondo
fondo_imagen = None
ruta_fondo = os.path.join("assets", "imagenes", "fondo_menu.png")
if not os.path.exists(ruta_fondo):
    ruta_fondo = os.path.join("assets", "imagenes", "fondo_menu.jpg")

try:
    if os.path.exists(ruta_fondo):
        fondo_imagen = pygame.image.load(ruta_fondo)
        fondo_imagen = pygame.transform.scale(fondo_imagen, (ANCHO, ALTO))
except pygame.error as e:
    print(f"No se pudo cargar la imagen de fondo: {e}")
    fondo_imagen = None


class Boton:
    def __init__(self, x, y, ancho, alto, texto, accion):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.accion = accion
        self.hover = False
    
    def dibujar(self, pantalla):
        # Color interior del botón
        color = ROJO_HOVER if self.hover else ROJO
        pygame.draw.rect(pantalla, color, self.rect, border_radius=10)
        # Borde rojo oscuro
        pygame.draw.rect(pantalla, ROJO_OSCURO, self.rect, 3, border_radius=10)
        
        # Texto blanco
        texto_surface = fuente_boton.render(self.texto, True, BLANCO)
        texto_rect = texto_surface.get_rect(center=self.rect.center)
        pantalla.blit(texto_surface, texto_rect)
    
    def verificar_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    
    def verificar_click(self, pos):
        if self.rect.collidepoint(pos):
            self.accion()
            return True
        return False


def iniciar_juego():
    pygame.quit()
    subprocess.Popen([sys.executable, 'main.py'])
    sys.exit()


def configuracion():
    print("Configuración (próximamente)")


def creditos():
    print("Créditos (próximamente)")


def main_menu():
    # Crear botones
    ancho_boton = 180
    alto_boton = 45
    x_centro = ANCHO // 2 - ancho_boton // 2
    espacio = 65
    
    botones = [
        Boton(x_centro, 280, ancho_boton, alto_boton, "JUGAR", iniciar_juego),
        Boton(x_centro, 280 + espacio, ancho_boton, alto_boton, "CONFIGURACIÓN", configuracion),
        Boton(x_centro, 280 + espacio * 2, ancho_boton, alto_boton, "CRÉDITOS", creditos)
    ]
    
    while True:
        reloj.tick(60)
        
        # Dibujar fondo
        if fondo_imagen:
            pantalla.blit(fondo_imagen, (0, 0))
        else:
            pantalla.fill(FONDO)
        
        # Título
        titulo = fuente_titulo.render("ping.internacional", True, DORADO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 80))
        
        # Obtener posición del mouse
        mouse_pos = pygame.mouse.get_pos()
        
        # Actualizar y dibujar botones
        for boton in botones:
            boton.verificar_hover(mouse_pos)
            boton.dibujar(pantalla)
        
        pygame.display.flip()
        
        # Eventos
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:  # Click izquierdo
                    for boton in botones:
                        boton.verificar_click(mouse_pos)


if __name__ == "__main__":
    main_menu()
    
