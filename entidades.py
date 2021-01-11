import pygame as pg

class Pelota:
    def __init__(self, x, y, vx, vy, color, escala):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.escala = escala

        self.imagen = pg.Surface((self.escala, self.escala))
        self.imagen.fill(self.color)


    @property
    def rect(self):
        return pg.Rect(self.x, self.y, self.escala, self.escala)

    @property
    def right(self):
        return self.rect.right

    @property 
    def left(self):
        return self.rect.left

    @property 
    def top(self):
        rect = pg.Rect(self.x, self.y, self.escala, self.escala)
        return rect.top

    @property 
    def bottom(self):
        rect = pg.Rect(self.x, self.y, self.escala, self.escala)
        return rect.bottom
