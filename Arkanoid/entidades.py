import pygame as pg
from pygame.locals import *
from Arkanoid import DIMENSIONES_JUEGO, FPS

import random
import sys


pg.init()

def colision(yo, otro):
    VrelX = otro.vx - yo.vx
    VrelY = otro.vy - yo.vy

    hay_colision = yo.rect.colliderect(otro.rect)
    if not hay_colision: 
        return False

    penetracionX = abs(otro.rect.centerx - yo.rect.centerx) - (yo.rect.w/2 + otro.rect.w/2)
    penetracionY = abs(otro.rect.centery - yo.rect.centery) - (yo.rect.h/2 + otro.rect.h/2)

    if abs(penetracionX) > abs(VrelX):
        yo.vy *= -1
        otro.vy *= -1

    if abs(penetracionY) > abs(VrelY):
        yo.vx *= -1
        otro.vx *= -1

    return True

class Ladrillo(pg.sprite.Sprite):
    w = 64
    h = 32
    def __init__(self, x, y):
        self.vx = 0
        self.vy = 0
        self.__alive = True

        self.imagen = pg.Surface((self.w, self.h))
        self.imagen.fill((255, 255, 255))
        pg.draw.rect(self.imagen, (255, 0 , 0), Rect((2, 2), (self.w-4, self.h-4)))
        self.rect = self.imagen.get_rect(x=x, y=y)

    @property
    def died(self):
        return not self.__alive

    @died.setter
    def died(self, value):
        self.__alive = not value
        if not self.__alive:
            del self


class Raqueta(pg.sprite.Sprite):
    def __init__(self, x, y, vx, vy=0):
        super().__init__()
        self.vx = vx
        self.vy = 0

        self.imagen = pg.image.load("resources/images/regular_racket.png")
        self.rect = self.imagen.get_rect(x=x, y=y)

    def update(self, dt):
        self.rect.x += self.vx
        if self.rect.x + 128 >= DIMENSIONES_JUEGO[0]:
            self.rect.x = DIMENSIONES_JUEGO[0] - 128
        if self.rect.x <= 0:
            self.rect.x = 0

    def manejar_eventos(self):
        teclas_pulsadas = pg.key.get_pressed()
        if teclas_pulsadas[K_RIGHT]:
            self.vx = 10
        elif teclas_pulsadas[K_LEFT]:
            self.vx = -10
        else:
            self.vx = 0



class Pelota(pg.sprite.Sprite):
    imagenes_files = ['brown_ball.png', 'blue_ball.png', 'red_ball.png', 'green_ball.png']
    num_imgs_explosion = 8
    retardo_animaciones = 5

    def __init__(self, x, y, vx, vy):
        pg.sprite.Sprite.__init__(self)
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
        self.rect = self.imagen.get_rect(x=x, y=y)

    def cargaExplosion(self):
        return [pg.image.load(f"resources/images/explosion0{i}.png") for i in range(self.num_imgs_explosion)]


    def cargaImagenes(self):
        lista_imagenes = []
        for img in self.imagenes_files:
            lista_imagenes.append(pg.image.load(f"resources/images/{img}"))

        return lista_imagenes


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

        self.rect.x += self.vx
        self.rect.y += self.vy

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
        hay_colision = colisio(self, algo)        
        
        if hay_colision and debe_morir:
            algo.died = True

        return hay_colision

    def comprobar_colisiones(self, grupo, debe_morir=False):
        pass

    
    def update(self, dt):
        self.actualizar_posicion()

        if self.muriendo:
            return self.explosion(dt)
        else:
            self.actualizar_disfraz()
        

class Game:
    def __init__(self):
        self.pantalla = pg.display.set_mode(DIMENSIONES_JUEGO)
        pg.display.set_caption("Futuro Arkanoid")

        self.playerSprites = pg.sprite.Group()
        self.obstaclesSprites = pg.sprite.Group()
        self.allSprites = pg.sprite.Group()

        self.pelota = Pelota(400, 300, 5, 5)
        self.raqueta = Raqueta(336, 550, 0)
        self.playerSprites.add(self.raqueta)

        self.obstaclesSprites.add(self.creaLadrillos())
        self.allSprites.add(self.pelota, self.playerSprites, self.obstaclesSprites)

        xo = 16
        yo = 16
        for c in range(12):
            for f in range(5):
                l = Ladrillo(xo + c * Ladrillo.w, yo + f * Ladrillo.h)
                self.ladrillos.append(l)
        
        self.clock = pg.time.Clock()

    def creaLadrillos(self):
        ladrillos = pg.sprite.Group()
        xo = 16
        yo = 16
        for c in range(12):
            for f in range(5):
                l = Ladrillo(xo + c * Ladrillo.w, yo + f * Ladrillo.h)
                ladrillos.add(l)

        return ladrillos


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

            for ladrillo in self.ladrillos:
                if self.pelota.comprobar_colision(ladrillo, True):
                    self.ladrillos.remove(ladrillo)

            self.pantalla.fill((0,0,255))

            self.pantalla.blit(self.pelota.imagen, (self.pelota.rect.x, self.pelota.rect.y))
            self.pantalla.blit(self.raqueta.imagen, (self.raqueta.rect.x, self.raqueta.rect.y))

            for ladrillo in self.ladrillos:
                self.pantalla.blit(ladrillo.imagen, (ladrillo.rect.x, ladrillo.rect.y))


            '''
            Refrescar pantalla
            '''
            pg.display.flip()
