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
            
class Bloque_cuadrado(Bloque):
    estructura = (
        (1, 1),
        (1, 1)
    )

class Bloque_T(Bloque):
    estructura = (
        (1, 1, 1),
        (0, 1, 0)
    )


class Bloque_de_linea(Bloque):
    estructura = (
        (1,),
        (1,),
        (1,),
        (1,)
    )


class Bloque_L(Bloque):
    estructura = (
        (1, 1),
        (1, 0),
        (1, 0),
    )


class Bloque_Z(Bloque):
    estructura = (
        (0, 1),
        (1, 1),
        (1, 0),
    )

class GrupoBloques(pygame.sprite.OrderedUpdates):

    @staticmethod
    def obtener_bloque_random():
        return random.choice(
            (Bloque_cuadrado, Bloque_T, Bloque_de_linea, Bloque_L, Bloque_Z))()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.reiniciar_cuadricula()
        self.ignorar_siguiente_parada = False
        self.puntaje = 0
        self.siguiente_bloque = None
        # No hay movimiento solo se inicia el atributo
        self.detener_movimiento_bloque_actual()
        # El primer bloque
        self.crear_nuevo_bloque()

    def Verifica_Finalizacion_Linea(self):
        """
        Compruebe cada línea de la cuadrícula y elimine las que están completas
        :return:
        """

        for i, fila in enumerate(self.cuadricula[::-1]):
            if all(fila):
                self.puntaje += 5
                # Consigue los bloques afectados por la eliminación de línea y Eliminar duplicados.
                bloques_afecados = list(
                    OrderedDict.fromkeys(self.grid[-1 - i]))

                for Bloque, desplazamiento_y in bloques_afecados:
                    # Elimina los bloques que estan completados
                    Bloque.estructura = np.delete(Bloque.estructura, desplazamiento_y, 0)
                    if Bloque.estructura.any():
                        # Una vez eliminado, compruebamos si tenemos columnas vacías  ya que necesitan ser dejados caer.
                        Bloque.estructura, desplazamiento_x = \
                            eliminar_columnas_vacias(Bloque.estructura)
                        # Compensar el espacio ido con las columnas para mantener la posición original del bloque.
                        Bloque.x += desplazamiento_x
                        # Forzar actualizacion
                        Bloque.redibujar()
                    else:
                        # Si la estructura está vacía, entonces el bloque desaparece.
                        self.eliminar(Bloque)

                    # En lugar de verificar qué bloques necesitan ser movidos
                    # una vez que se completó una línea, solo intente mover todos
                    # ellos.
                    for Bloque in self:
                        # Excepto el acutal bloque.
                        if Bloque.actual:
                            continue

                        # Tire hacia abajo de cada bloque hasta que alcance el
                        # abajo o choca con otro bloque.
                        while True:
                            try:
                                Bloque.movimiento_abajo(self)
                            except Parteinferiror:
                                break

                    self.actualizar_cuadricula()
                    # Desde que hemos actualizado la cuadricula, ahora el contador i
                    # ya no es válido, así que vuelve a llamar a la función
                    # para verificar si hay otras líneas completadas en el
                    # nueva cuadricula.
                    self.Verifica_Finalizacion_Linea()
                    break

    def reiniciar_cuadricula(self):
        self.cuadricula = [[0 for _ in range(10)] for _ in range(20)]

    def crear_nuevo_bloque(self):
        nuevo_bloque = self.siguiente_bloque or GrupoBloques.obtener_bloque_random()
        if Bloque.Chocar(nuevo_bloque, self):
            raise TopAlcanzada
        self.add(nuevo_bloque)
        self.siguiente_bloque = GrupoBloques.obtener_bloque_random()
        self.actualizar_cuadricula()
        self.Verifica_Finalizacion_Linea()

    def actualizar_cuadricula(self):
        self.reiniciar_cuadricula()
        for Bloque in self:
            for desplazamiento_y, fila in enumerate(Bloque.estructura):
                for desplazamiento_x, digit in enumerate(fila):
                    # Evitar la sustitución de bloques anteriores.
                    if digit == 0:
                        continue
                    rowid = Bloque.y + desplazamiento_y
                    colid = Bloque.x + desplazamiento_x
                    self.cuadricula[rowid][colid] = (Bloque, desplazamiento_y)

    def bloque_actual(self):
        return self.sprites()[-1]

    def actualizar_bloque_actual(self):
        try:
            self.bloque_actual.movimiento_abajo(self)
        except Parteinferiror:
            self.detener_movimiento_bloque_actual()
            self.crear_nuevo_bloque()
        else:
            self.actualizar_cuadricula()

    def mover_bloque_actual(self):
        # Primero verifica si hay algo para mover
        if self.bloque_de_movimiento_actual is None:
            return
        accion = {
            pygame.K_DOWN: self.bloque_actual.movimiento_abajo,
            pygame.K_LEFT: self.bloque_actual.movimiento_izquierda,
            pygame.K_RIGHT: self.bloque_actual.movimiento_derecha
                }
        try:
            # Cada función requiere que el grupo sea el primer argumento.
            # para comprobar cualquier posible colisión.

            accion[self.bloque_de_movimiento_actual](self)
        except Parteinferiror:
            self.detener_movimiento_bloque_actual()
            self.crear_nuevo_bloque()
        else:
            self.actualizar_cuadricula()

    def empieza_movimiento_bloque(self, llave):
        if self.bloque_de_movimiento_actual is not None:
            self.ignorar_siguiente_parada = True
        self.bloque_de_movimiento_actual = llave

    def detener_movimiento_bloque_actual(self):
        if self.ignorar_siguiente_parada:
            self.ignorar_siguiente_parada = False
        else:
            self.bloque_de_movimiento_actual = None

    def rotar_bloque_actual(self):
        # Evitar la rotación de bloques cuadrados..
        if not isinstance(self.bloque_actual, Bloque_cuadrado):
            self.bloque_actual.rotar(self)
            self.actualizar_cuadricula()

def dibujar_cuadricula(Fondo):
    """Dibuja la cuadrícula de fondo."""
    color_cuadricula = 50, 50, 50
    # Lineas Verticales.
    for i in range(11):
        x = Tamano_Titulo * i
        pygame.draw.line(
            Fondo, color_cuadricula, (x, 0), (x, Altura_Cuadricula)
        )
    # Lineas Horizontales.
    for i in range(21):
        y = Tamano_Titulo * i
        pygame.draw.line(
            Fondo, color_cuadricula, (0, y), (Ancho_Cuadricula, y)
        )
def dibujar_superficie_centrada(pantalla, suerficie, y):
    pantalla.blit(suerficie, (400 - suerficie.get_width() / 2, y))

def main():
    pygame.init()
    pygame.display.set_caption("Tetris JODA")
    pantalla = pygame.display.set_mode((Ancho_Ventana, Altura_Ventana))
    correr = True
    pausar = False
    perder = False
    # Crear fondo.
    fondo = pygame.Surface(pantalla.get_size())
    bgcolor = (0, 0, 0)
    fondo.fill(bgcolor)
    # Dibujar la cuadrícula en la parte superior del fondo.
    dibujar_cuadricula(fondo)
    # Esto hace que blitear más rápido.
    background = fondo.convert()

    try:
        fuente = pygame.font.Font("Roboto-Regular.ttf", 20)
    except OSError:
        # Si la fuente no esta disponible sera usado por defecto.
        pass
    siguiente_bloque_del_texto = fuente.render("Siguiente figura:", True, (255, 255, 255), bgcolor)
    Pausa_bloque_del_texto = fuente.render("Pause Tecla P:", True, (255, 255, 255), bgcolor)

    mensaje_puntaje_texto = fuente.render("Puntaje:", True, (255, 255, 255), bgcolor)
    pierdes_texto = fuente.render("¡Juego terminado!", True, (255, 220, 0), bgcolor)

    # Constantes Eventos.
    MOVIMIENTOS_CLAVES = pygame.K_LEFT, pygame.K_RIGHT, pygame.K_DOWN
    ACTUALIZACIÓN_ACTUAL_BLOQUE_ACTUAL = pygame.USEREVENT + 1
    EVENTO_MOVIMIENTO_BLOQUE_ACTUAL = pygame.USEREVENT + 2
    pygame.time.set_timer(ACTUALIZACIÓN_ACTUAL_BLOQUE_ACTUAL, 1000)
    pygame.time.set_timer(EVENTO_MOVIMIENTO_BLOQUE_ACTUAL, 100)

    bloques = GrupoBloques()

    while correr:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                correr = False
                break
            elif evento.type == pygame.KEYUP:
                if not pausar and not perder:
                    if evento.key in MOVIMIENTOS_CLAVES:
                        bloques.detener_movimiento_bloque_actual()
                    elif evento.key == pygame.K_UP:
                        bloques.rotar_bloque_actual()
                if evento.key == pygame.K_p:
                    pausar = not pausar

            # Stop moving blocks if the game is over or paused.
            if perder or pausar:
                continue

            if evento.type == pygame.KEYDOWN:
                if evento.key in MOVIMIENTOS_CLAVES:
                    bloques.empieza_movimiento_bloque(evento.key)

            try:
                if evento.type == EVENTO_MOVIMIENTO_BLOQUE_ACTUAL:
                    bloques.actualizar_bloque_actual()
                elif evento.type == EVENTO_MOVIMIENTO_BLOQUE_ACTUAL:
                    bloques.actualizar_bloque_actual()
            except TopAlcanzada:
                perder = True

        # Draw background and grid.
        pantalla.blit(background, (0, 0))
        # Blocks.
        bloques.draw(pantalla)
        # Sidebar with misc. information.
        dibujar_superficie_centrada(pantalla, siguiente_bloque_del_texto, 50)
        dibujar_superficie_centrada(pantalla, bloques.siguiente_bloque.imagen, 100)
        dibujar_superficie_centrada(pantalla, mensaje_puntaje_texto, 240)
        dibujar_superficie_centrada(pantalla, Pausa_bloque_del_texto, 500)
        mensaje_puntaje_texto = fuente.render(
            str(bloques.puntaje), True, (255, 255, 255), bgcolor)
        dibujar_superficie_centrada(pantalla, mensaje_puntaje_texto, 270)
        if perder:
             dibujar_superficie_centrada(pantalla, pierdes_texto, 360)
        # Update.
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
     
