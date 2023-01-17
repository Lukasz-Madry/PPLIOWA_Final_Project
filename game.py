from time import sleep
import pygame
import sqlite3
import pygame_menu
import os
from pygame_menu import themes
from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes
import random

DATABASE = 'database.db'
# Start the game
pygame.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
# pygame.display.set_caption("Bricks")
floor = pygame.Rect(100, 550, 200, 10)
ball = pygame.Rect(50, 250, 10, 10)
score = 0
move = [1, 1]
continueGame = True
#playername = ""

loading = pygame_menu.Menu('Loading the Game...', 600, 400, theme=themes.THEME_DARK)
loading.add.progress_bar("Progress", progressbar_id="1", default=0, width=200, )

arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))

update_loading = pygame.USEREVENT + 0

GREEN = (28, 252, 106)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (252, 3, 152)
ORANGE = (252, 170, 28)
RED = (255, 0, 0)

# bricks
b1 = [pygame.Rect(1 + i * 100, 60, 98, 38) for i in range(6)]
b2 = [pygame.Rect(1 + i * 100, 100, 98, 38) for i in range(6)]
b3 = [pygame.Rect(1 + i * 100, 140, 98, 38) for i in range(6)]


def start_the_game():
    mainmenu._open(loading)
    pygame.time.set_timer(update_loading, 30)


def setplayername(name):
    global playername
    print('Player name is', name)
    playername = name

mainmenu = pygame_menu.Menu('Welcome', 600, 400, theme=themes.THEME_SOLARIZED)
mainmenu.add.text_input('Name: ', default='username', onchange= setplayername)
mainmenu.add.button('Play', start_the_game)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)


def writetodb(playername, score):
    print(playername)
    print(score)
    # if os.path.isfile(DATABASE):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("insert into scores (player,score) VALUES (?,?)", (playername, score))
    con.commit()
    con.close()


# Draw bricks on screen
def draw_brick(bricks):
    for i in bricks:
        pygame.draw.rect(screen, ORANGE, i)


def rand_bounce(mv):
    seed = random.randint(0, 1)
    if seed == 0:
        mv[0] = -mv[0]
        mv[1] = -mv[1]
    if seed == 1:
        mv[0] = -mv[0]
        mv[1] = mv[1]
    return mv[0], mv[1]



while True:
    events = pygame.event.get()
    for event in events:
        if event.type == update_loading:
            progress = loading.get_widget("1")
            progress.set_value(progress.get_value() + 1)
            if progress.get_value() == 100:
                while continueGame:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            continueGame = False
                    screen.fill(BLACK)
                    pygame.draw.rect(screen, PINK, floor)
                    font = pygame.font.Font(None, 34)
                    text = font.render("CURRENT SCORE: " + str(score), True, WHITE)
                    screen.blit(text, (180, 10))

                    keys = pygame.key.get_pressed()
                    # floor move
                    if keys[pygame.K_RIGHT]:
                        if floor.x < 540:
                            floor.x = floor.x + 3

                    if keys[pygame.K_LEFT]:
                        if floor.x > 0:
                            floor.x = floor.x - 3

                    # Bricks
                    draw_brick(b1)
                    draw_brick(b2)
                    draw_brick(b3)

                    # Ball
                    ball.x = ball.x + move[0]
                    ball.y = ball.y + move[1]

                    if ball.x > 590 or ball.x < 0:
                        move[0] = -move[0]
                    if ball.y <= 3:
                        move[1] = -move[1]
                    if floor.collidepoint(ball.x, ball.y):
                        move[1] = -move[1]
                    #print(move)
                    if ball.y >= 590:
                        font = pygame.font.Font(None, 74)
                        text = font.render("Game Over!", True, RED)
                        screen.blit(text, (150, 300))
                        font = pygame.font.Font(None, 50)
                        text = font.render("YOUR FINAL SCORE: " + str(score), True, GREEN)
                        screen.blit(text, (100, 350))
                        pygame.display.flip()
                        pygame.time.wait(300)  # disp message after winning
                        break

                    pygame.draw.rect(screen, WHITE, ball)

                    for i in b1:
                        if i.collidepoint(ball.x, ball.y):
                            b1.remove(i)
                            move[0], move[1] = rand_bounce(move)
                            score = score + 1

                    for i in b2:
                        if i.collidepoint(ball.x, ball.y):
                            b2.remove(i)
                            move[0], move[1] = rand_bounce(move)
                            score = score + 1

                    for i in b3:
                        if i.collidepoint(ball.x, ball.y):
                            b3.remove(i)
                            move[0], move[1] = rand_bounce(move)
                            score = score + 1

                    if score == 18:
                        font = pygame.font.Font(None, 74)
                        text = font.render("YOU WON", True, GREEN)
                        screen.blit(text, (150, 350))
                        pygame.display.flip()
                        pygame.time.wait(300)  # disp message after winning
                        break

                    pygame.time.wait(1)
                    pygame.display.flip()

                    # End the game
                writetodb(playername, score)
                pygame.quit()

        if event.type == pygame.QUIT:
            exit()

    if mainmenu.is_enabled():
        mainmenu.update(events)
        mainmenu.draw(screen)
        if mainmenu.get_current().get_selected_widget():
            arrow.draw(screen, mainmenu.get_current().get_selected_widget())

    pygame.display.update()