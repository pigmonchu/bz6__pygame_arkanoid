import pygame as pg
from Arkanoid import GAME_DIMENSIONS, FPS

import random
import sys


pg.init()

class Pelota:
    imagenes_files = ['brown_ball.png', 'blue_ball.png', 'red_ball.png', 'green_ball.png']
    num_imgs_explosion = 8

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.imagenes = self.cargaImagenes()
        self.imagenes_explosion = self.cargaExplosion()
        self.imagen_act = 0
        self.ix_explosion = 0
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
        if self.rect.left <= 0 or self.rect.right >= GAME_DIMENSIONS[0]:
            self.vx = -self.vx

        if self.rect.top <= 0:
            self.vy = -self.vy

        if self.rect.bottom >= GAME_DIMENSIONS[1]:
            self.muriendo = True
            return

        self.x += self.vx
        self.y += self.vy

    def actualizar_disfraz(self):
        '''
        Gestionar imagen activa (disfraz) de pelota
        '''
        self.imagen_act += 1
        if self.imagen_act >= len(self.imagenes):
            self.imagen_act = 0
        self.imagen = self.imagenes[self.imagen_act]


    def actualizar(self):
        self.actualizar_posicion()

        if self.muriendo:
            self.explosion()
        else:
            self.actualizar_disfraz()
        
    def explosion(self):
        if self.ix_explosion >= len(self.imagenes_explosion):
            #terminar programa
            self.ix_explosion = 0

        self.imagen = self.imagenes_explosion[self.ix_explosion]

        self.ix_explosion += 1

        


class Game:
    def __init__(self):

        self.pantalla = pg.display.set_mode(GAME_DIMENSIONS)
        pg.display.set_caption("Futuro Arkanoid")
        self.pelota = Pelota(400, 300, 10, 10)
        self.clock = pg.time.Clock()


    def bucle_principal(self):
        game_over = False
        
        while not game_over:
            print(self.clock.tick(FPS))
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.pelota.actualizar()

            self.pantalla.fill((0,0,255))
            self.pantalla.blit(self.pelota.imagen, (self.pelota.x, self.pelota.y))

            pg.display.flip()
