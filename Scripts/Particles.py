import math,pygame as pg

class Particle:
    def __init__(self, game, p_type : str, pos : tuple, scale : tuple,  velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.scale = scale
        self.velocity = velocity
        self.animation = self.game.assets["particles"][p_type].copy()
        self.animation.frame = frame

    def update(self):
        kill = False
        if self.animation.done:
            kill = True

        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

        self.animation.update()

        return kill
    
    def render(self, surface, offset=(0,0)):
        img = self.animation.img()
        img = pg.transform.scale(img, self.scale)
        surface.blit(img,
                      (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))
        

class Spark:
    def __init__(self, pos, angle, speed, color):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed
        self.color = color
        self.init_len = 3 #스@파이크
    
    def update(self):
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        self.speed = max(0, self.speed - 0.1)

        return not self.speed

    def render(self, surface, offset=(0,0)):
        render_points = [
            #앞
            (self.pos[0] + math.cos(self.angle) * self.speed * self.init_len - offset[0],
              self.pos[1] + math.sin(self.angle) * self.speed * self.init_len - offset[1]),
            #왼
            (self.pos[0] + math.cos(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[0],
              self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
            #끝
            (self.pos[0] + math.cos(self.angle + math.pi) * self.speed * self.init_len - offset[0],
              self.pos[1] + math.sin(self.angle + math.pi) * self.speed * self.init_len - offset[1]),
            #오
            (self.pos[0] + math.cos(self.angle - math.pi * 0.5) * self.speed * 0.5 - offset[0],
              self.pos[1] + math.sin(self.angle + math.pi * 0.5) * self.speed * 0.5 - offset[1]),
        ]
        
        pg.draw.polygon(surface, self.color, render_points)

        