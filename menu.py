import pygame
import subprocess
import sys

pygame.init()

ANCHO, ALTO = 900, 700
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Menu Principal")
reloj = pygame.time.Clock()
fuente_titulo = pygame.font.SysFont(None, 80)
fuente_texto = pygame.font.SysFont(None, 42)


def main_menu():
    while True:
        reloj.tick(60)
        pantalla.fill((15, 18, 28))

        titulo = fuente_titulo.render("MENU PRINCIPAL", True, (255, 215, 0))
        instruccion = fuente_texto.render("Pulsa Enter para jugar", True, (255, 255, 255))
        salir = fuente_texto.render("Pulsa Esc para salir", True, (200, 200, 200))

        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 220))
        pantalla.blit(instruccion, (ANCHO // 2 - instruccion.get_width() // 2, 340))
        pantalla.blit(salir, (ANCHO // 2 - salir.get_width() // 2, 395))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    pygame.quit()
                    subprocess.Popen([sys.executable, 'main.py'])
                    return
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main_menu()
