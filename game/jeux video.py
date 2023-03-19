import pygame
import random
import math
pygame.init()
class SoundManager:
    def __init__(self):
        self.sounds = {
            'click' : pygame.mixer.Sound('assets jeux video/sabre.mp3'),
            'game_over' : pygame.mixer.Sound('assets jeux video/game over.wav'),
            'meteorite' : pygame.mixer.Sound('assets jeux video/pet.mp3'),
            'tir' : pygame.mixer.Sound('assets jeux video/tir.wav'),
        }
        
    def play(self, name):
        self.sounds[name].play()
#créer une clase pour gérer cette comete
class Comet(pygame.sprite.Sprite):
    def __init__(self, comet_event):
        super().__init__()
        #definir l'image associée à cette comette
        self.image = pygame.image.load('assets jeux video/portugal.png')
        self.rect = self.image.get_rect()
        self.velocity = random.randint(3, 5)
        self.rect.x = random.randint(20, 800)
        self.rect.y = - random.randint(0, 800)
        self.comet_event = comet_event
    def remove(self):
        self.comet_event.game.sound_manager.play('meteorite')
        self.comet_event.all_comets.remove(self)
        if len(self.comet_event.all_comets) == 0:
            print("L'évenement est fini")
            self.comet_event.reset_percent()
            self.comet_event.game.spawn_monster()
            self.comet_event.game.spawn_monster()
    
    
    def fall(self):
        self.rect.y += self.velocity
        #ne tombe pas sur le sol
        if self.rect.y>= 500:
            print("sol")
            self.remove()
            if len(self.comet_event.all_comets) == 0:
                print("L'évenement est fini")
                self.comet_event.reset_percent()
                self.comet_event.fall_mode = False

        #verifie
        if self.comet_event.game.check_collision(
            self, self.comet_event.game.all_players
        ):
            print("Joueur touché !")
            #retirer
            self.remove()
            self.comet_event.game.player.damage(20)
       
class CometFallEvent:
    #chargement crée compteur
    def __init__(self, game):
        self.percent = 0
        self.percent_speed = 5
        self.game = game
        self.fall_mode = False
        #definir un groupe de sprite pour stocker
        self.all_comets    = pygame.sprite.Group()
    def add_percent(self):
        self.percent += self.percent_speed /100
    def is_full_loaded(self):
        return self.percent >= 100
    def reset_percent(self):
        self.percent = 0
    def meteor_fall(self):
        for i in range(1, 10):

        #apparaitre 1 boule de feu
            self.all_comets.add(Comet(self))
    def attempt_fall(self):
        #la jauge d'évenement est chargée
        if self.is_full_loaded() and len(self.game.all_monsters) == 0:
            print("pluie de cometes !!")
            self.meteor_fall()
           
            self.fall_mode = True

    def update_bar(self, surface):
        #ajouter du pourcentage à la bar
        self.add_percent()
        #appel de la methode declenchecometes
       
        #barre noir
        pygame.draw.rect(surface, (119, 181, 254), [
            0,#en x
            surface.get_height()-20,#en y
            surface.get_width(),#longeur de la fenetre
            10
        ])
        # #barre rouge
        pygame.draw.rect(surface, (255, 215, 0), [
            0,#en x
            surface.get_height()-20,#en y
            (surface.get_width() / 100)*self.percent,#longeur de la fenetre
            10
        ])
        

#créer une classe qui va gérer la notion de monstre sur notre jeu
class Monster(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game=game
        self.health = 100
        self.max_health = 100
        self.attack = 1
        self.image = pygame.image.load('assets jeux video/zombies.png')
        self.image = pygame.transform.scale(self.image, (170, 170))
        self.rect = self.image.get_rect()
        self.rect.x =700 + random.randint(0, 300)
        self.rect.y =473
        self.velocity= random.randint(1, 4)
       
    def damage(self, amount):
        self.health -= amount
        if self.health <=0:
            self.rect.x = 1000 + random.randint(0, 300)
            self.velocity = random.randint(1, 2)
            self.health =self.max_health
            self.game.score += 20
        if  self.game.comet_event.is_full_loaded():
            self.game.all_monsters.remove(self)
            self.game.comet_event.attempt_fall()

    def update_health_bar(self, surface):
        bar_color =(255, 0, 0)
        back_bar_color =(60, 63, 60)
        bar_position = [self.rect.x +50 , self.rect.y-20, self.health, 5]
        back_bar_position = [self.rect.x +50 , self.rect.y-20, self.max_health, 5]
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)
    
       

    def forward(self):
        if not self.game.check_collision(self, self.game.all_players):
            self.rect.x -= self.velocity
            #collision avec joueur
        else:
            self.game.player.damage(self.attack)
   



 #definir la classe qui va gérer le projectile de notre joueur
class Projectile(pygame.sprite.Sprite):
    #def le constructeur de cette classe 
    def __init__(self, player):
        super().__init__()
        self.velocity = 3
        self.player = player
        self.image = pygame.image.load('assets jeux video/kunai.png')
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x + 170
        self.rect.y = player.rect.y + 150
        self.origin_image = self.image
        self.angle = 0
    
    
    def rotate(self):
        self.angle+=3
        self.image = pygame.transform.rotozoom(self.origin_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)


    
    def remove(self):
        self.player.all_projectiles.remove(self)
    
    def move(self):
        self.rect.x += self.velocity
        self.rotate()
        for monster in self.player.game.check_collision(self, self.player.game.all_monsters):
            self.remove()
            monster.damage(self.player.attack)
            

        #verifier si notre projectile n'est plus présent sur l'écran 
        if self.rect.x> 1080:
            self.remove()
            print("suppr")
 

#creer une seconde classe qui va representer notre jeu 
class Game:

    def __init__(self):
        #definir si notre jeu a commencé ou nom
        self.is_playing = False
        #generer joueur
        
        self.all_players = pygame.sprite.Group()
        self.player=Player(self)
        self.all_players.add(self.player)
        #generer l'évenement
        self.comet_event =  CometFallEvent(self)
        #groupe de monstres
        self.all_monsters = pygame.sprite.Group()
        self.pressed = {}
        self.font = pygame.font.SysFont("monospace", 16)
        self.score = 0
        self.spawn_monster()
        self.spawn_monster()
        self.sound_manager = SoundManager()
        
    def start(self):
        self.is_playing=True
        self.spawn_monster()
        self.spawn_monster()

    def game_over(self):
        #revenir à 0
        self.all_monsters = pygame.sprite.Group()
        self.comet_event.all_comets = pygame.sprite.Group()
        self.player.health = self.player.max_health
        self.comet_event.reset_percent()
        self.is_playing = False
        self.score = 0
        self.sound_manager.play('game_over')
        
        
    def update(self, screen):   
       
        score_text =self.font.render(f"Score : {self.score}", 1,(240,0,32))
        screen.blit(score_text, (20, 20))
        #appliquer l'image de mon joueur 
        screen.blit(self.player.image, self.player.rect)
        #actualiser la barre de vie 
        self.player.update_health_bar(screen)
        #actualiser la barre d'evenement du jeu 
        self.comet_event.update_bar(screen)
        #recuperer les projectile du joueur
        for projectile in self.player.all_projectiles:
            projectile.move()
        for monster in self.all_monsters:
            monster.forward()
            monster.update_health_bar(screen)        
        #recuperer comete
        for comet in self.comet_event.all_comets:
            comet.fall() 
        #appliquer ensemble des images projectiles
        self.player.all_projectiles.draw(screen)
    

        #appliquer l'ensemble des images de mon groupe de monstre
        self.all_monsters.draw(screen)
        # #appliquer l'ensemble des images de mon groupe de cometes
        self.comet_event.all_comets.draw(screen)
        #verifier si le joueur gauche droite 
        if self.pressed.get(pygame.K_RIGHT) and self.player.rect.x<855:
            self.player.move_right()
        elif self.pressed.get(pygame.K_LEFT) and self.player.rect.x > -75:
            self.player.move_left()
            print(self.player.rect.x)
        
        
    def check_collision(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)

    def spawn_monster(self):
        monster = Monster(self)
        self.all_monsters.add(monster)

#creer une premiere classe qui va representer notre joueur
class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.health=100
        self.max_health = 100
        self.attack=50
        self.velocity = 4
        self.all_projectiles = pygame.sprite.Group()
        self.image=pygame.image.load('assets jeux video/ninja player.png')
        self.rect=self.image.get_rect()
        self.rect.x =300
        self.rect.y =420
    def damage(self, amount):
        if self.health -amount> amount:
            self.health -= amount
        else:
            #si le joueur n'a plus de vie 
            self.game.game_over()

    def move_right(self):
        if not self.game.check_collision(self, self.game.all_monsters):
            self.rect.x+= self.velocity

    def move_left(self):
        self.rect.x-= self.velocity

    def launch_projectile(self):
        self.all_projectiles.add(Projectile(self))
        self.game.sound_manager.play('tir')

    def update_health_bar(self, surface):
        bar_color =(255, 0, 0)
        back_bar_color =(60, 63, 60)
        bar_position = [self.rect.x +80 , self.rect.y-5 , self.health, 5]
        back_bar_position = [self.rect.x +80 , self.rect.y-5, self.max_health, 5]
        pygame.draw.rect(surface, back_bar_color, back_bar_position)
        pygame.draw.rect(surface, bar_color, bar_position)

    
    
#genere la fenetre 
pygame.display.set_caption("La Guerre des Znrd")
screen = pygame.display.set_mode((1080, 720))
#importer de charger l'arriere plan de notre jeu 
backround = pygame.image.load('assets jeux video/zombie screen.png')
backround = pygame.transform.scale(backround, (1080, 720))
#importer charger notre banniére
banner = pygame.image.load('assets jeux video/menu jeu.png')
banner = pygame.transform.scale(banner, (400, 400))
banner_rect = banner.get_rect()
banner_rect.x = screen.get_width() / 3
#importer charger boutons play
play_button = pygame.image.load('assets jeux video/red button.png')
play_button = pygame.transform.scale(play_button, (200, 100))
play_button_rect= play_button.get_rect()
play_button_rect.x = screen.get_width() / 2.5
play_button_rect.y = screen.get_height() / 1.5
#charger notre jeu
game = Game()
#charger notre joueur
player=Player(game)
game.player.image = pygame.transform.scale(player.image, (player.rect.width//2, player.rect.height//2))



running = True

#bouvle tant que cette condition est vrai
while running:
    #appliquer l'arrire plan 
    screen.blit(backround, (0, 0))
    if game.is_playing:
        game.update(screen)
    # verifier si notre jeu ' pas commencé
    else:
        screen.blit(banner, (banner_rect))
        screen.blit(play_button, play_button_rect)

     #mettre à jour l'ecran
    pygame.display.flip()
         #si le joueur ferme cette fenetre
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Ferme le jeu ")
        #detcter si un joueur lache une touvhe du clavier 
        elif event.type == pygame.KEYDOWN:
            game.pressed[event.key] = True
            if event.key == pygame.K_SPACE:
                game.player.launch_projectile()
        elif event.type == pygame.KEYUP:
            game.pressed[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #verif souris choc boutton
            if play_button_rect.collidepoint(event.pos):
                #mettre le jeu en meode lancé
                game.start()
                game.sound_manager.play('click')
   
        