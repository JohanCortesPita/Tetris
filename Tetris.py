import Random

import pygame
from pygame import Rect
import numpy as np

np.array(((0, 1), (1, 1), (1, 0),))

Ancho_Ventana, Altura_Ventana = 500, 601
Ancho_Cuadricula, Altura_Cuadricula = 300, 600
Tamano_Titulo = 30

def eliminar_columnas_vacias(arreglo, desplazamiento_x = 0, contador = True):
    """
    Elimina las columnas vacías del arreglo (es decir, las rellenas con ceros).
    El valor de retorno es (neuevo_arreglo, Desplazamiento_x), donde Despalazamiento es cómo
    gran parte de la coordenada x necesita ser aumentada para mantener
    La posición original del bloque.
    """
    for colid, columna in enumerate(arreglo.T):
        if columna.max() == 0:
            if contador:
                desplazamiento_x += 1
            # Elimina la columna actual e intenta de nuevo
            arreglo, desplazamiento_x = eliminar_columnas_vacias(
                np.dele(arreglo, colid, 1), desplazamiento_x, contador)
            break
        else:
            contador = False
    return arreglo, desplazamiento_x

class Parteinferiror(Exception):
    pass

class TopAlcanzada(Exception):
    pass

class Bloque(pygame.sprite.Sprite):

    def Chocar(bloque, grupo):
        """
        Valida si el bloque especifico choca con otro bloque dentro del grupo

        :param grupo: Bloque actual
        :return: True or False si choca
        """

        for otro_bloque in grupo:
            # Ignora el bloque actual el cual siemore chocara con si mismo.
            if bloque == otro_bloque:
                continue
            if pygame.sprite.collide_mask(bloque, otro_bloque) is not None:
                return True
            return False

    def __init__(self):
        super().__init__()
        # Obtiene un color al azar
        self.color = random.choice((
            (200, 200, 200),
            (215, 133, 133),
            (30, 145, 255),
            (0, 170, 0),
            (180, 0, 140),
            (200, 200, 0)
        ))

        self.actual = True
        self.estructura = np.array(self.estructura)
        # Rotación aleatoria inicial y de vuelta
        if random.randint(0, 1):
            self.estructura = np.rot90(self.estructura)
        if random.randint(0, 1):
            # Dar la vuelta en el eje X
            self.estructura = np.flip(self.estructura, 0)
        self.dibujar()

    def dibujar(self, x=4, y=0):
        Ancho = len(self.estructura[0]) * Tamano_Titulo
        Alto = len(self.estructura) * Tamano_Titulo
        self.imagen = pygame.surface.Surface([Ancho, Alto])
        self.imagen.set_colorkey((0, 0, 0))
        #Posicion y tamaño
        self.rect = Rect(0, 0, Ancho,  Alto)
        self.x = x
        self.y = y
        for y, fila in enumerate(self.estructura):
            for x, columna in enumerate(fila):
                if columna:
                    pygame.draw.rect(
                        self.imagen,
                        self.color,
                        Rect(x * Tamano_Titulo + 1, y * Tamano_Titulo + 1,
                             Tamano_Titulo - 2, Tamano_Titulo - 2)
                    )
        self.crear_mascara()

    def redibujar(self):
        self.dibujar(self.x, self.y)

    def crear_mascara(self):
        """
        Creamos el atributo de máscara desde la superficie principal.
        La máscara es necesaria para comprobar las colisiones. Esto debería llamarse
        Después de la creación de la superficie o actualización.

        :return:
        """
        self.mascara = pygame.mask.from_surface(self.imagen)

    def inicar_dubujo(self):
        raise NotImplementedError

    def grupo(self):
        return self.grupo()[0]

    def x(self):
        return self.x

    def x(self, valor):
        self.x = valor
        self.rect.left = valor * Tamano_Titulo

    def y(self):
        return self.y

    def y(self, valor):
        self.y = valor
        self.rect.top = valor * Tamano_Titulo

    def movimiento_izquierda(self, grupo):
        self.x -= 1
        # Comprueba si llegamos al margen izquierdo.
        if self.x < 0 or Bloque.Chocar(self, grupo):
            self.x += 1

    def movimiento_derecha(self, grupo):
        self.x += 1
        # Compruebe si llegamos al margen derecho o chocamos con otro bloque

        if self.rect.right > Ancho_Cuadricula or Bloque.Chocar(self, grupo):
            #Retroceder
            self.x -= 1

    def movimiento_abajo(self, grupo):
        self.y += 1
        # Comprueba si el bloque alcanzó el fondo o chocó con otro
        if self.rect.bottom > Altura_Cuadricula or Bloque.Chocar(self, grupo):
            # Volver a la anterior posicion
            self.y -= 1
            self.actual = False
            raise Parteinferiror

    def rotar(self, grupo):
        self.imagen = pygame.transform.rotate(self.imagen, 90)
        # Una vez girados necesitamos actualizar el tamaño y la posición.
        self.rect.width = self.imagen.obtener_Ancho()
        self.rect.height = self.imagen.obtener_Alto()
        self.crear_mascara()
        # Comprueba que la nueva posición no excede los límites o choque con otros bloques y ajústelo si es necesario
        while self.rect.right > Ancho_Cuadricula:
            self.x -= 1
        while self.rect.left < 0:
            self.x += 1
        while self.rect.bottom > Altura_Cuadricula:
            self.y -= 1
        while True:
            if not Bloque.Chocar(self, grupo):
                break
            self.y -= 1
        self.estructura = np.rot90(self.estructura)

    def actualizar(self):
        if self.actualizar:
            self.movimiento_abajo()