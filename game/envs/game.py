import pygame
import math

screenWidth = 900
screenHeight = 900
checkPoints = ((800, 100), (800, 280), (450, 350), (810, 430), (750, 810), (550, 540), 
            (380, 810), (70, 500), (130, 80), (260, 450), (100, 100))

def getDistance(p1, p2):
	return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

def rotateCenter(image, angle):
    originalRect = image.get_rect()
    rotateIMG = pygame.transform.rotate(image, angle)
    rotateRect = originalRect.copy()
    rotateRect.center = rotateIMG.get_rect().center
    rotateIMG = rotateIMG.subsurface(rotateRect).copy()
    return rotateIMG

class Car:
    def __init__(self, carIMG, trackIMG, pos):
        self.car = pygame.image.load(carIMG)
        self.track = pygame.image.load(trackIMG)
        self.car = pygame.transform.scale(self.car, (65, 65))
        self.rotateCar = self.car
        self.pos = pos
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.eyes = []
        self.backEyes = []
        self.alive = True
        self.checkPoint = 0
        self.prevDistance = 0
        self.currentDistance = 0
        self.finish = False
        self.checkFlag = False
        self.distance = 0
        self.time = 0

        for d in range(-90, 120, 45):
            self.checkEyes(d)
            self.checkBackEyes(d)

    #Draws current car state to screen
    def draw(self, screen):
        screen.blit(self.rotateCar, self.pos)

    # Checks which eyes should be drawn
    def checkEyes(self, degrees):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degrees))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degrees))) * len)

        while not self.track.get_at((x, y)) == (0, 0, 0, 255):
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degrees))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degrees))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.eyes.append([(x, y), dist])

    #Checks which eyes should be drawn in the back
    def checkBackEyes(self, degrees):
        len = 0
        x = int(self.center[0] - math.cos(math.radians(360 - (self.angle + degrees))) * len)
        y = int(self.center[1] - math.sin(math.radians(360 - (self.angle + degrees))) * len)

        while not self.track.get_at((x, y)) == (0, 0, 0, 255):
            len = len + 1
            x = int(self.center[0] - math.cos(math.radians(360 - (self.angle + degrees))) * len)
            y = int(self.center[1] - math.sin(math.radians(360 - (self.angle + degrees))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.backEyes.append([(x, y), dist])
        
    #Draws 9 eyes in front of car
    def drawEyes(self, screen):
        for r in self.eyes:
            pos, dist = r
            pygame.draw.line(screen, (255, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (255, 255, 0), pos, 5)
        for r in self.backEyes:
            pos, dist = r
            pygame.draw.line(screen, (255, 255, 0), self.center, pos, 1)
            pygame.draw.circle(screen, (255, 255, 0), pos, 5)

    #Check for collision using colours
    def checkCollision(self):
        self.alive = True
        for p in self.corners:
            if self.track.get_at((int(p[0]), int(p[1]))) == (0, 0, 0, 255):
                self.alive = False
                break

    #Check if car reached a checkpoint
    def checkCheckPoint(self):
        p = checkPoints[self.checkPoint]
        self.prevDistance = self.currentDistance
        dist = getDistance(p, self.center)
        if dist < 70:
            self.checkPoint += 1
            self.prevDistance = 9999
            self.checkFlag = True
            if self.checkPoint >= len(checkPoints):
                self.checkPoint = 0
                self.finish = True
            else:
                self.finish = False

        self.currentDistance = dist

    #Car actions and updates
    def update(self):
        #check speed
        self.speed -= 0.5
        if self.speed > 5:
            self.speed = 5
        if self.speed < 0.5:
            self.speed = 0.5

        #check position
        self.rotateCar = rotateCenter(self.car, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed

        self.distance += self.speed
        self.time += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + 32.5, int(self.pos[1]) + 32.5]
        len = 20
        LT = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        RT = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        LB = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        RB = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.corners = [LT, RT, LB, RB]

class CarAI:
    def __init__(self, render = True):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 25)
        self.car = Car('images/car.png', 'images/track-border.png', [400, 50])
        self.game_speed = 60
        self.render = render
        self.mode = 0
        self.backgroundIMG = pygame.image.load("images/background.png")
        self.background = pygame.transform.smoothscale(self.backgroundIMG, (screenWidth, screenHeight))
        self.trackIMG = pygame.image.load("images/track.png")
        self.track = pygame.transform.smoothscale(self.trackIMG, (screenWidth, screenHeight))

    def action(self, action):
        if action == 0:
            self.car.speed += 2
        if action == 1:
            self.car.angle += 5
        elif action == 2:
            self.car.angle -= 5

        self.car.update()
        self.car.checkCollision()
        self.car.checkCheckPoint()

        self.car.eyes.clear()
        self.car.backEyes.clear()
        for d in range(-90, 120, 45):
            self.car.checkEyes(d)
            self.car.checkBackEyes(d)

    def evaluate(self):
        reward = 0
        if not self.car.alive:
            reward = -10000 + self.car.distance - (self.car.time/8)

        elif self.car.finish:
            reward = -10000 + self.car.distance - (self.car.time/8) + 2000
        return reward

    def finished(self):
        if not self.car.alive or self.car.finish:
            self.car.checkPoint = 0
            self.car.distance = 0
            return True
        return False

    def observe(self):
        # return state
        eyes = self.car.eyes
        ret = [0, 0, 0, 0, 0]
        i = 0
        for r in eyes:
            ret[i] = int(r[1] / 20)
            i += 1

        return ret

    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.track, (0,0))


        if self.mode == 1:
            self.screen.fill((0, 0, 0))

        self.car.eyes.clear()
        self.car.backEyes.clear()
        for d in range(-90, 105, 15):
            self.car.checkEyes(d)
            self.car.checkBackEyes(d)
        pygame.draw.circle(self.screen, (255 ,215 ,0), checkPoints[self.car.checkPoint], 15)
        text = self.font.render(str(checkPoints.index(checkPoints[self.car.checkPoint])+1), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (checkPoints[self.car.checkPoint])
        self.screen.blit(text, textRect)
        self.car.drawEyes(self.screen)
        self.car.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(self.game_speed)
