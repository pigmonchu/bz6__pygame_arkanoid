import pygame as pg
from pygame.locals import *
from Arkanoid import DIMENSIONES_JUEGO, FPS

import random
import sys


pg.init()

def colision(yo, otro):
    VrelX = otro.vx - yo.vx
    VrelY = otro.vy - yo.vy

    minTop = min(yo.rect.top, otro.rect.top)
    maxBottom = minTop + yo.rect.h + otro.rect.h
    realBottom = max(yo.rect.bottom, otro.rect.bottom)

    minLeft = min(yo.rect.left, otro.rect.left)
    maxRight = minLeft + yo.rect.w + otro.rect.w
    realRight = max(yo.rect.right, otro.rect.right)

    hay_colision = realBottom <= maxBottom and realRight <= maxRight

    if not hay_colision: 
        return False

    penetracionX = otro.rect.centerx - yo.rect.centerx - (yo.rect.w/2 + otro.rect.w/2)
    penetracionY = otro.rect.centery - yo.rect.centery - (yo.rect.h/2 + otro.rect.h/2)

    if abs(penetracionX) > abs(VrelX):
        yo.vy *= -1
        otro.vy *= -1

    if abs(penetracionY) > abs(VrelY):
        yo.vx *= -1
        otro.vx *= -1

    return True

class LadrilloMovil:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.__alive = True

        self.imagen = pg.image.load(f"resources/images/{random.choice(['red', 'purple', 'green', 'cyan'])}_brick.png")

    @property
    def rect(self):
        return self.imagen.get_rect(topleft=(self.x, self.y))

    def actualizar(self):
        if self.rect.left <= 0 or self.rect.right > DIMENSIONES_JUEGO[0]:
            self.vx *= -1
        if self.rect.top <= 0 or self.rect.bottom > DIMENSIONES_JUEGO[1]:
            self.vy *= -1

        self.x += self.vx
        self.y += self.vy

    def comprobar_colision(self, algo, debe_morir=False):
        hay_colision = colision(self, algo)        
        
        if debe_morir:
            algo.died = True


    @property
    def died(self):
        return not self.__alive

    @died.setter
    def died(self, value):
        self.__alive = not value
        if not self.__alive:
            del self

class Ladrillo:
    w = 64
    h = 32
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.__alive = True

        self.imagen = pg.Surface((self.w, self.h))
        self.imagen.fill((255, 255, 255))
        pg.draw.rect(self.imagen, (255, 0 , 0), Rect((2, 2), (self.w-4, self.h-4)))

    @property
    def rect(self):
        return self.imagen.get_rect(topleft=(self.x, self.y))

    def actualizar(self):
        pass

    @property
    def died(self):
        return not self.__alive

    @died.setter
    def died(self, value):
        self.__alive = not value
        if not self.__alive:
            del self


class Raqueta:
    def __init__(self, x, y, vx, vy=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = 0

        self.imagen = pg.image.load("resources/images/regular_racket.png")


    def actualizar(self):
        self.x += self.vx
        if self.x + 128 >= DIMENSIONES_JUEGO[0]:
            self.x = DIMENSIONES_JUEGO[0] - 128
        if self.x <= 0:
            self.x = 0

    @property
    def rect(self):
        return self.imagen.get_rect(topleft=(self.x, self.y))


    def manejar_eventos(self):
        teclas_pulsadas = pg.key.get_pressed()
        if teclas_pulsadas[K_RIGHT]:
            self.vx = 10
        elif teclas_pulsadas[K_LEFT]:
            self.vx = -10
        else:
            self.vx = 0



class Pelota:
    imagenes_files = ['brown_ball.png', 'blue_ball.png', 'red_ball.png', 'green_ball.png']
    num_imgs_explosion = 8
    retardo_animaciones = 5

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.imagenes = self.cargaImagenes()
        self.imagenes_explosion = self.cargaExplosion()
        self.imagen_act = 0
        self.ix_explosion = 0
        self.ciclos_tras_refresco = 0
        self.ticks_acumulados = 0
        self.ticks_por_frame_de_animacion = 1000//FPS * self.retardo_animaciones
        self.muriendo = False
        
        self.imagen = self.imagenes[self.imagen_act]

    def cargaExplosion(self):
        return [pg.image.load(f"resources/images/explosion0{i}.png") for i in range(self.num_imgs_explosion)]


    def cargaImagenes(self):
        lista_imagenes = []
        for img in self.imagenes_files:
            lista_imagenes.append(pg.image.load(f"resources/images/{img}"))

        return lista_imagenes


    @property
    def rect(self):
        return self.imagen.get_rect(topleft=(self.x, self.y))


    def actualizar_posicion(self):
        if self.muriendo:
            return
        '''
        Gestionar posición de pelota
        '''
        if self.rect.left <= 0 or self.rect.right >= DIMENSIONES_JUEGO[0]:
            self.vx = -self.vx

        if self.rect.top <= 0:
            self.vy = -self.vy

        if self.rect.bottom >= DIMENSIONES_JUEGO[1]:
            self.muriendo = True
            self.ciclos_tras_refresco = 0
            return

        self.x += self.vx
        self.y += self.vy

    def actualizar_disfraz(self):
        '''
        Gestionar imagen activa (disfraz) de pelota
        '''
        self.ciclos_tras_refresco += 1

        if self.ciclos_tras_refresco % self.retardo_animaciones == 0:
            self.imagen_act += 1
            if self.imagen_act >= len(self.imagenes):
                self.imagen_act = 0
        
        self.imagen = self.imagenes[self.imagen_act]
        
    def explosion(self, dt):
        if self.ix_explosion >= len(self.imagenes_explosion):
            return True


        self.imagen = self.imagenes_explosion[self.ix_explosion]

    
        self.ticks_acumulados += dt
        if self.ticks_acumulados >= self.ticks_por_frame_de_animacion:
            self.ix_explosion += 1
            self.ticks_acumulados = 0
        
        return False

    def comprobar_colision(self, algo, debe_morir=False):
        hay_colision = colision(self, algo)        
        
        if debe_morir:
            algo.died = True

    def actualizar(self, dt):
        self.actualizar_posicion()

        if self.muriendo:
            return self.explosion(dt)
        else:
            self.actualizar_disfraz()
        
        

class Game1:
    def __init__(self):

        self.pantalla = pg.display.set_mode(DIMENSIONES_JUEGO)
        pg.display.set_caption("Colisiones")
    

        self.l1 = LadrilloMovil(random.randint(0,750), random.randint(0,550), random.randint(2, 6)*random.choice([-1, 1]), random.randint(2, 6)*random.choice([-1, 1]))
        self.l2 = LadrilloMovil(random.randint(0,750), random.randint(0,550), random.randint(2, 6)*random.choice([-1, 1]), random.randint(2, 6)*random.choice([-1, 1]))
        self.clock = pg.time.Clock()


    def bucle_principal(self):
        game_over = False
        
        while not game_over:
            dt = self.clock.tick(FPS)
            '''
            Gestion de eventos
            '''
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            '''
            Actualización de elementos del juego
            '''
            self.l1.actualizar()
            self.l2.actualizar()
            self.l1.comprobar_colision(self.l2, True)

            self.pantalla.fill((0,0,255))
            self.pantalla.blit(self.l1.imagen, (self.l1.x, self.l1.y))
            self.pantalla.blit(self.l2.imagen, (self.l2.x, self.l2.y))


            '''
            Refrescar pantalla
            '''
            pg.display.flip()


class Game:
    def __init__(self):

        self.pantalla = pg.display.set_mode(DIMENSIONES_JUEGO)
        pg.display.set_caption("Futuro Arkanoid")
        
        self.pelota = Pelota(400, 300, 5, 5)
        self.raqueta = Raqueta(336, 550, 0)

        self.El_ladrillo = Ladrillo(400, 300)
        self.El_ladrillo = None
        self.ladrillos = []
        xo = 16
        yo = 16
        for c in range(12):
            for f in range(5):
                l = Ladrillo(xo + c * Ladrillo.w, yo + f * Ladrillo.h)
                self.ladrillos.append(l)
        
        self.clock = pg.time.Clock()


    def bucle_principal(self):
        game_over = False
        
        while not game_over:
            dt = self.clock.tick(FPS)
            '''
            Gestion de eventos
            '''
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.raqueta.manejar_eventos()

            '''
            Actualización de elementos del juego
            '''
            game_over = self.pelota.actualizar(dt)
            self.raqueta.actualizar()
            self.pelota.comprobar_colision(self.raqueta)

            self.pantalla.fill((0,0,255))
            self.pantalla.blit(self.pelota.imagen, (self.pelota.x, self.pelota.y))
            self.pantalla.blit(self.raqueta.imagen, (self.raqueta.x, self.raqueta.y))

            for ladrillo in self.ladrillos:
                self.pantalla.blit(ladrillo.imagen, (ladrillo.x, ladrillo.y))


            '''
            Refrescar pantalla
            '''
            pg.display.flip()
