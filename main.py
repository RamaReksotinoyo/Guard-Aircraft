import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guardian Aircraft")

# Load images
ROCK=pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets","rock.png")), (55,45)), 45)
ROCK1=pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets","rock.png")), (55,45)), 90)
ROCK2=pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets","rock.png")), (55,45)), 180)
ROCK3=pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join("assets","rock.png")), (55,45)), 360)
PESAWAT_MERAH=pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets','spaceship_red.png')), (100,100)),180)
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")), (WIDTH, HEIGHT))

#Sound
sound_laser=pygame.mixer.Sound(os.path.join("assets","Gun+Silencer.mp3"))
shoot=pygame.mixer.Sound(os.path.join("assets","Grenade+1.mp3"))

class Aircraft():
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = PESAWAT_MERAH
        self.laser_img = YELLOW_LASER
        self.lasers = []
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.cool_down_counter = 0

    def move_lasers(self, vel, objs):
        poin=0
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        pygame.mixer.Sound.play(shoot)
                        poin+=1
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1 

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1    

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

class Rock():
    COLOR_MAP = {
            "rock1": ROCK,
            "rock2": ROCK1,
            "rock3": ROCK2,
            "rock4": ROCK3
            }

    def __init__(self, x, y, color, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img=self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 10
    poin=0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    rocks=[]
    wave_length = 5
    rock_vel=1
    player_vel = 5
    laser_vel = 5

    player = Aircraft(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))

        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))

        for rock in rocks:
            rock.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 250))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 :
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(rocks) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                rock = Rock(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["rock1", "rock2", "rock3", "rock4"]))
                rocks.append(rock)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            pygame.mixer.Sound.play(sound_laser)
            player.shoot()

        for rock in rocks[:]:
            rock.move(rock_vel)
            if collide(rock, player) or rock.y + rock.get_height()>HEIGHT:
                lives -= 1
                rocks.remove(rock)

        player.move_lasers(-laser_vel, rocks)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            main()
    pygame.quit()

main_menu()