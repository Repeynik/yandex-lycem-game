import pygame
import random
from os import path

img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

WIDTH = 680
HEIGHT = 400
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK = (23, 23, 23)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()
score = 0

font_name = pygame.font.match_font('Helvetica')

player_img = pygame.image.load(path.join(img_dir, 'player-ship.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (50, 44))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laser.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'bomb.png')).convert_alpha()
meteor_images = []
meteor_list = [
    'meteor1.png',
    'meteor2.png',
    'meteor4.png',
    'meteor3.png',
    'meteor5.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(1, 8):
    filename = 'vzr{}.jpg'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(DARK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    filename = 'vzr{}.jpg'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(DARK)
    explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'life-long-king.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'baff-energy.png')).convert()
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
pygame.mixer.music.set_volume(0.2)

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))


def main_menu(text):
    global screen

    main = pygame.mixer.music.load(path.join(sound_folder, "main.mp3"))
    pygame.mixer.music.play(-1)

    bg = pygame.image.load(path.join(img_dir, "holl.gif")).convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT), screen)

    screen.blit(bg, (0, 0))
    pygame.display.update()

    draw_text(screen, "ASTEROIDS", 70, WIDTH / 2, 60)

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()
        else:
            draw_text(screen, text[0], 30, WIDTH / 2, HEIGHT / 2)
            draw_text(screen, text[1], 30, WIDTH / 2, (HEIGHT / 2) + 40)
            draw_text(screen, text[2], 30, WIDTH / 2, (HEIGHT / 2) + 80)
            pygame.display.update()

    screen.fill(BLACK)
    draw_text(screen, "Приготовьтесь", 40, WIDTH / 2, HEIGHT / 2)
    pygame.display.update()


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    pct = max(pct, 0)
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (80, 67))
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.rotate(self.image, 270)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = 10
        self.rect.bottom = HEIGHT / 2
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = 10
            self.rect.bottom = HEIGHT / 2

        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        elif keystate[pygame.K_UP]:
            self.speedy = -5
        elif keystate[pygame.K_DOWN]:
            self.speedy = 5

        if keystate[pygame.K_SPACE]:
            self.shoot()

        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.right, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.bottom)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            if self.power >= 3:
                bullet1 = Bullet(self.rect.right, self.rect.top)
                bullet2 = Bullet(self.rect.right, self.rect.bottom)
                missile1 = Missile(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (10, HEIGHT / 2)


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .90 / 2)
        self.rect.x = 610
        self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
        self.speedx = random.randrange(-15, -5)
        self.speedy = random.randrange(-3, 3)
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50:
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y -= self.speedy

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 80):
            self.rect.x = 610
            self.rect.y = random.randrange(0, HEIGHT - self.rect.height)
            self.speedx = random.randrange(-15, -5)


class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 2

    def update(self):
        self.rect.y += self.speedy
        if self.rect.right > WIDTH:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.rotate(self.image, 270)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 10

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.kill()


class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.image = pygame.transform.rotate(self.image, 270)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 10

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.kill()



class Star(object):
    def __init__(self, x, y, xspeed):
        self.colour = WHITE
        self.radius = 1
        self.x = x
        self.y = y
        self.xspeed = xspeed

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.x, self.y), self.radius)

    def fall(self):
        self.x += self.xspeed

    def check(self):
        if self.x <= 0:
            self.x = WIDTH


stars = []

for i in range(100):
    x = random.randint(1, WIDTH - 1)
    y = random.randint(1, HEIGHT - 1)
    stars.append(Star(x, y, -5))

running = True
menu_display = True
text = ["Нажмите [ENTER] чтобы начать", "и [Q] чтобы выйти", "Управлять кораблем можно с помощью стрелок"]
while running:
    if menu_display:
        main_menu(text)
        pygame.time.wait(3000)

        pygame.mixer.music.stop()
        pygame.mixer.music.load(path.join(sound_folder, 'game-music.mp3 '))
        pygame.mixer.music.play(-1)

        menu_display = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        mobs = pygame.sprite.Group()
        for i in range(6):
            newmob()

        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()

        score = 0
        text = ["Нажмите [ENTER] чтобы начать", "Управление осуществляется с помощью кнопок со стрелками", "и [Q] "
                                                                                                           "чтобы "
                                                                                                           "выйти"]
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    all_sprites.update()
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)
        newmob()

    hits = pygame.sprite.spritecollide(player, mobs, True,
                                       pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            player_die_sound.play()
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100

    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()

    if player.lives == 0 and not death_explosion.alive():
        player.hide()
        text = [f"Вы набрали {score} очков", "Нажмите [Enter] чтобы начать сначала", "и [Q] чтобы выйти"]
        menu_display = True
        score = 0
        pygame.display.update()

    screen.fill(BLACK)

    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)

    draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
    for star in stars:
        star.draw()
        star.fall()
        star.check()

    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
