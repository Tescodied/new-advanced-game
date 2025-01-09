import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame, os, re
from random import choice, randint

pygame.init()

# DISPLAY
W, H = 1000, 1000
WH_AVG = (W + H) / 2  #for fonts
FPS = 60

win = pygame.display.set_mode((W, H))
pygame.display.set_caption("New original game")


# FILES
def find_file_path(name, need_quit=True):
    path = os.path.abspath(name)  #make sure to cd the idle with a path
    
    if need_quit:
        print(f"Full path : {path}")
        quit()
    return path + "\\"

path = find_file_path("pics", need_quit=False)

def make_image(file_name, width, height, additional_path=""):
    return pygame.transform.scale(pygame.image.load(f"{path}{additional_path}{file_name}").convert_alpha(), (width , height))


# MAIN BACKGROUND
top_road, bot_road = H // 2.55 , H - H // 15


# PAUSE BUTTON
pause_button_width, pause_button_height = W / 20, H / 20
pause_buttonx, pause_buttony = W - W / 50 - pause_button_width, H / 50 
pause_button = make_image("pause button.png", pause_button_width, pause_button_height)
pause_button_hitbox = pygame.rect.Rect(pause_buttonx, pause_buttony, pause_button_width, pause_button_height)
pause_button_mask = pygame.mask.from_surface(pause_button)


# MAIN CHARACTER / CURSER
player_width, player_height = W / 7.5, H / 5
player = make_image("main character.png", player_width, player_height, "player\\")

player_bullet = make_image("bullet.png", W / 57, H / 200, "player\\")
bullet_mask = pygame.mask.from_surface(player_bullet)
curser = make_image("curser.png", W / 20, H / 20, "player\\")
curser_point_mask = pygame.mask.Mask((1, 1), fill = True)


# COLOURS
BLACK = (0,0,0)
WHITE = (255, 255, 255)
LIGHT_GREY = (200, 200, 200)
TEXT_COL = (224, 180, 103)

GREEN =         (0, 200, 100)
DARK_GREEN =    (0, 100, 50)
RED =           (255,50,50)



# VOLUME / SOUND / MUSIC
general_vol = music_vol = 50


# FONT / TEXT
cool_font_name = f"{path}fonts\\KnightWarrior-w16n8.otf"

def find_centre_screen(text, width_centre=2, height_centre=2):
    return W / width_centre - text.get_width() / 2, H /height_centre - text.get_height() / 2 # W


# LEVELS / MAP
map_bg = make_image("map bg.png", W, H, "map\\")

def levels_info(width, height):

    folder_path_levels = f"{path}map\\"
    files = [f for f in os.listdir(folder_path_levels) if os.path.isfile(os.path.join(folder_path_levels, f))]

    text_files = [file for file in files if "text" in file]
    text_files.sort(key=lambda x: int(re.match(r"(\d+)", x).group()))
    level_name_order = tuple(name[4:-9].capitalize() for name in text_files)

    level_files = [file for file in files if "level" in file]
    txt_surfaces = [make_image(text, width, (height ) if " " in level_name_order[i] else height / 2, folder_path_levels[-4:]) for i, text in enumerate(text_files)]

    num_level_heights = 3
    num_levels = len(level_name_order) # 9
    num_colours = len(level_files)

    surface_list = [make_image(name, width, height, folder_path_levels[-4:]) for name in level_files]
    levels_cols = [surface_list[0] for _ in range(num_levels)]

    map_blackness_padding = H / 3.9525
    ypadding =  H / 20
    start_x, end_x = W / 12.5, W / 25
    bottom_levely = H - ypadding - map_blackness_padding - height # top for y cor of level

    yspacing = (H - (ypadding * 2 + map_blackness_padding * 2 + height * num_level_heights)) / (num_level_heights - 1) #between each ship yes
    xspacing = (W - (end_x + start_x + width * num_levels)) / num_levels - 1

    cors = [
        [
        round(start_x + (width * index + xspacing * index), 1), 
        round(bottom_levely - (height * (index % 4 if index % 2 != 1 else 1) + yspacing * (index % 4 if index % 2 != 1 else 1)), 1)
        ]
    for index in range(num_levels)
    ]
    
    level_bgs = []
    for count, bg in enumerate(level_name_order[:-1]):
        for num_bg in range(1,3):
            try:
                level_bgs.append(make_image(f"{count + 1} - {bg.lower()} - {num_bg}.png", W, H, "backgrounds\\"))
            except FileNotFoundError:
                continue
    
    level_bgs = level_bgs[::-1]

    return cors, levels_cols, level_name_order, num_levels, level_bgs, num_colours, surface_list, txt_surfaces, map_blackness_padding


# GAME
def draw_dots_map(level, level_cors, levels_map_bg, level_width, level_height, level_3cols):
    clock = pygame.time.Clock()
    running = True

    num_dots_per_level = 3
    dot_radius = 3
    outline_dot_radius = dot_radius + 2

    while running:
        clock.tick(FPS)

        win.fill(BLACK)
        win.blit(levels_map_bg, (0,0))

        for surface, cors in zip(level_3cols, level_cors):
            win.blit(surface, cors)

        for i, cors1 in enumerate(level_cors):
            if i + 1 == level:
                break

            try: 
                cors2 = level_cors[i + 1] 
            except IndexError: 
                continue
            
            xdif, ydif = round(cors2[0] - cors1[0], 1), round(cors2[1] - cors1[1], 1)
            ydif += level_height if ydif < 0 else -level_height

            xspacing = round(xdif / (num_dots_per_level + 1), 1)
            yspacing = round(ydif / (num_dots_per_level + 1), 1)

            dot_cors = [
                [
                cors1[0] + level_width / 2 + (i + 1) * xspacing,
                cors1[1] + (i + 1) * yspacing + (level_height if yspacing > 0 else 0)
                ]
            for i in range(num_dots_per_level)]

            for cors in dot_cors:
                pygame.draw.circle(win, BLACK, cors, outline_dot_radius)
                pygame.draw.circle(win, LIGHT_GREY, cors, dot_radius)
                
        win.blit(curser, (pygame.mouse.get_pos()))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()


def display_level(level, num_levels, level_width, level_height, level_3cols, levelcors, num_colours, colours_levels, original_cols, txt_surfaces, blackness):
    clock = pygame.time.Clock()
    running = True
    time_wait = 2 * FPS

    red_levelx = 0
    red_levely = 0

    red_location = level - 1
    colours_levels[red_location] = level_3cols[2]
    red_level_surface = colours_levels[red_location]

    red_level_mask = pygame.mask.from_surface(red_level_surface)

    level_font = pygame.font.Font(cool_font_name, 100)
    level_text = level_font.render(f"Level {level}", True, TEXT_COL)

    while running:
        clock.tick(FPS)
        mousex, mousey = pygame.mouse.get_pos()

        win.fill(BLACK)
        win.blit(map_bg, (0,0))
        win.blit(level_text, (W / 2 - level_text.get_width() / 2, blackness / 2 - level_text.get_height() / 2))

        red_level_colliding = curser_point_mask.overlap(red_level_mask, (red_levelx - mousex, red_levely - mousey))    

        if time_wait <= 0:
            for i, ((levelx, levely), txt) in enumerate(zip(levelcors, txt_surfaces)):
                blit_cors = (levelx, levely)

                if i == red_location:

                    scale_multiplier = 1
                    if red_level_colliding:
                        scale_multiplier = 1.1

                    colours_levels[level - 1] = pygame.transform.scale(red_level_surface, (level_width * scale_multiplier, level_height * scale_multiplier))
                    red_levelx, red_levely = levelx - (level_width * scale_multiplier - level_width) / 2, levely - (level_height * scale_multiplier - level_height) / 2

                    blit_cors = (red_levelx, red_levely)
                
                win.blit(colours_levels[i], blit_cors)
                win.blit(txt, (levelx, levely + level_height))
                

            if pygame.mouse.get_pressed()[0] and red_level_colliding: #if left click and hovering level
                running = False
        else:
            time_wait -= 1
            for i, cors in enumerate(levelcors):
                win.blit(original_cols[i], cors)

        #if level > 1:
        #    draw_dots_map(level, levelcors, map_bg, level_width, level_height, original_cols)

        win.blit(curser, (mousex, mousey))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()


def loading_screen(main_bg1, main_bg2):
    running = True
    clock = pygame.time.Clock()

    wait_duration = 3 # countdown start value e.g. 3 2 1 
    time_onscreen = FPS * 1 #time on screen in seconds
    text_items = [str(i) for i in range(wait_duration, 0, -1)] + ["GO"]
    
    displaying_counter = [item for item in text_items for _ in range(time_onscreen)]

    slice_counter = 0
    last_slice = len(displaying_counter)

    display_font = pygame.font.Font(cool_font_name, int(WH_AVG // 3.3))

    chosen_bg = choice([main_bg1, main_bg2])

    while running:
        clock.tick(FPS)
        mousex, mousey = pygame.mouse.get_pos()

        win.blit(chosen_bg, (0,0))

        if slice_counter < last_slice:
            display_text = display_font.render(displaying_counter[slice_counter], True, TEXT_COL)
            win.blit(display_text, (W / 2 - display_text.get_width() / 2, H / 2 - display_text.get_height() / 2))
            slice_counter += 1
        else:
            running = False

        win.blit(curser, (mousex, mousey))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()



def pause_menu(main_bg, general_vol, music_vol):
    clock = pygame.time.Clock()
    running = True

    menu_width, menu_height = W / 1.5, H / 1.5
    bg_menux, bg_menuy = W / 2 - menu_width / 2, H / 2 - menu_height / 2
    bg_menu = make_image("background menu.png", menu_width, menu_height, "pause menu\\")

    resume_outline_width, resume_outline_height = W / 2.857 , H / 8.696
    resume_buttonx, resume_buttony = W / 2 - resume_outline_width / 2, H / 3.2

    vol_colour = (129, 139, 4)
    volumes_width, volumes_height = W / 4.348, H / 50
    volumesx = W / 2.135

    general_vol_max = pygame.rect.Rect(volumesx, H / 1.95, volumes_width, volumes_height)
    music_vol_max = pygame.rect.Rect(volumesx, H / 1.525, volumes_width, volumes_height) 
    vol_mulyiplier = volumes_width / 100  #100 for volume limit

    while running:
        clock.tick(FPS)

        mousex, mousey = pygame.mouse.get_pos()
        curser_point_rect = pygame.rect.Rect(mousex, mousey, 1, 1)

        general_vol_adjust = pygame.rect.Rect(volumesx, H / 1.96, max(0, general_vol * vol_mulyiplier), volumes_height)
        music_vol_adjust = pygame.rect.Rect(volumesx, H / 1.5225, max(0, music_vol * vol_mulyiplier), volumes_height) 

        resume_rect_outline = pygame.rect.Rect(resume_buttonx, resume_buttony, resume_outline_width, resume_outline_height)

        hovering_resume = curser_point_rect.colliderect(resume_rect_outline)
        hovering_general = curser_point_rect.colliderect(general_vol_max)
        hovering_music = curser_point_rect.colliderect(music_vol_max)

        resume_button_multuplier = 1
        if hovering_resume:
            resume_button_multuplier = 1.1

        new_resume_outline_width = resume_outline_width * resume_button_multuplier
        new_resume_outline_height = resume_outline_height * resume_button_multuplier

        resume_button = make_image("resume button.png", new_resume_outline_width * 1.9, new_resume_outline_height * 6, "pause menu\\")#
        resume_buttonx, resume_buttony = W / 2 - new_resume_outline_width / 2, H / 3.2 - (new_resume_outline_height - resume_outline_height) / 2

        win.blit(main_bg, (0,0))
        win.blit(bg_menu, (bg_menux, bg_menuy))
        win.blit(resume_button, (resume_buttonx, resume_buttony))

        pygame.draw.rect(win, vol_colour, music_vol_adjust)
        pygame.draw.rect(win, vol_colour, general_vol_adjust)

        win.blit(curser, (mousex, mousey))

        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[0]:
            if hovering_music:
                music_vol = round(abs(curser_point_rect.x - volumesx) / vol_mulyiplier, 1)
            if hovering_general:
                general_vol = round(abs(curser_point_rect.x - volumesx) / vol_mulyiplier, 1)
            if hovering_resume:
                running = False
                return general_vol, music_vol
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

def start():
    loading_bg = make_image("loading screen background.png", W, H, "start\\")
    button_width, button_height = W / 3.3, H / 5

    clock = pygame.time.Clock()
    running = True
    pygame.mouse.set_visible(False)

    original_play_button = make_image("play button.png", button_width, button_height, "start\\")
    button_mask = pygame.mask.from_surface(original_play_button)
    buttonx, buttony = W / 2 - button_width/ 2, H / 1.5 - button_height / 2

    while running:
        clock.tick(FPS)

        mousex, mousey = pygame.mouse.get_pos()

        play_offset = mousex - buttonx, mousey - buttony
        button_overlapping = button_mask.overlap(curser_point_mask, play_offset)

        button_change = 1
        if button_overlapping:
            button_change = 1.1

        pause_offset = mousex - pause_buttonx, mousey - pause_buttony
        pause_colliding = pause_button_mask.overlap(curser_point_mask, pause_offset)

        pause_button_change = 1
        if pause_colliding:
            pause_button_change = 1.1

        blitted_pause_button = pygame.transform.scale(
            pause_button, 
            (pause_button_width * pause_button_change, pause_button_height * pause_button_change)
        )

        blitted_play_button = pygame.transform.scale(
            original_play_button, 
            (button_width * button_change, button_height * button_change)
        )

        buttonx, buttony = W / 2 - blitted_play_button.get_width() / 2, H / 1.5 - blitted_play_button.get_height() / 2

        win.blit(loading_bg, (0, 0))
        win.blit(blitted_pause_button, (pause_buttonx - (pause_button_change * pause_button_width - pause_button_width) / 2, 
                                        pause_buttony - (pause_button_change * pause_button_height - pause_button_height) / 2))
        win.blit(blitted_play_button, (buttonx, buttony))
        win.blit(curser, (mousex, mousey))

        pygame.display.flip()

        if pygame.mouse.get_pressed()[0]:  #if left click
            if button_overlapping:
                running = False
                return loading_bg

            if pause_colliding:
                global general_vol, music_vol
                general_vol, music_vol = pause_menu(loading_bg, general_vol, music_vol)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()

def game_over(bg):
    clock = pygame.time.Clock()
    running = True
    wait_time = FPS * 1

    lost_font = pygame.font.Font(cool_font_name, 200)
    lost_text = lost_font.render("You died.", True, TEXT_COL)

    while running:
        clock.tick(FPS)
        if wait_time > 0:
            wait_time -= 1
        else:
            mousex, mousey = pygame.mouse.get_pos()

            win.blit(bg, (0,0))
            win.blit(lost_text, (W / 2 - lost_text.get_width() / 2, H / 2 - lost_text.get_height() / 2))
            win.blit(curser, (mousex, mousey))

            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()


def level_completed_screen(bg, bullet_increase):
    running = True
    clock = pygame.time.Clock()
    wait_time = FPS * 1

    winning_fontsize = 100
    winning_font = pygame.font.Font(cool_font_name, winning_fontsize)
    bullet_font = pygame.font.Font(cool_font_name, int(winning_fontsize * 3/4))

    text_gap = 100
    rect_text_gap = 20
    rect_tickness = 10

    button_rect = pygame.rect.Rect(0,0,0,0)  # initiate object

    while running:
        clock.tick(FPS)

        if wait_time > 0:
            wait_time -= 1
        else:
            win.blit(bg, (0,0))

            mousex, mousey = pygame.mouse.get_pos()
            curser_hitbox = pygame.rect.Rect(mousex, mousey, 1, 1)  

            option_hovering = curser_hitbox.colliderect(button_rect)
            button_text_multiplier = 1

            if option_hovering:
                button_text_multiplier = 1.1
            
            options_font = pygame.font.Font(cool_font_name, int(50 * button_text_multiplier))

            winning_text = winning_font.render("Level completed!", True, TEXT_COL)
            bullets_text = bullet_font.render(f"+{bullet_increase} Bullets", True, TEXT_COL)
            proceed_option_text = options_font.render("Proceed", True, TEXT_COL)

            winnning_text_xcor, winning_text_ycor = W / 2 - winning_text.get_width() / 2, H / 2 - winning_text.get_height() - text_gap / 2
            bullets_text_xcor, bullets_text_ycor = W / 2 - bullets_text.get_width() / 2, winning_text_ycor + winning_text.get_height() / 1.25

            win.blit(winning_text, (winnning_text_xcor, winning_text_ycor))
            win.blit(bullets_text, (bullets_text_xcor, bullets_text_ycor))

            button_rect = pygame.rect.Rect(W / 2 - proceed_option_text.get_width() / 2 * button_text_multiplier - rect_text_gap, 
                                    H / 2 + text_gap / 2 - rect_text_gap * button_text_multiplier, 
                                    proceed_option_text.get_width() * button_text_multiplier + rect_text_gap * 2, 
                                    proceed_option_text.get_height() * (1 + (button_text_multiplier - 1) / 2) + rect_text_gap * 2)
            
            pygame.draw.rect(win, TEXT_COL, button_rect, rect_tickness)
            win.blit(proceed_option_text, (W / 2 - proceed_option_text.get_width() / 2, H / 2 + text_gap / 2 - proceed_option_text.get_height() * (button_text_multiplier - 1) / 2))
            
            win.blit(curser, (mousex, mousey))

            if pygame.mouse.get_pressed()[0] and option_hovering:
                running = False

            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()


def game_finished(main_bg):
    clock = pygame.time.Clock()
    running = True

    win_font = pygame.font.Font(cool_font_name, int(WH_AVG // 10))
    win_text_l1 = win_font.render("You have beat ", True, TEXT_COL)
    win_text_l2 = win_font.render("the game for now.", True, TEXT_COL)
    text_l2_ycor = H / 1.6 - win_text_l2.get_height() / 2 + win_text_l1.get_height()

    rect_text_gap = 20
    rect_tickness = 10
    text_gap = 50

    quit_rect = pygame.rect.Rect(0,0,0,0)  # initiate object

    while running:
        clock.tick(FPS)

        mousex, mousey = pygame.mouse.get_pos()

        win.blit(main_bg, (0,0))

        win.blit(win_text_l1, (W / 2 - win_text_l1.get_width() / 2, H / 1.6 - win_text_l1.get_height() / 2))
        win.blit(win_text_l2, (W / 2 - win_text_l2.get_width() / 2, text_l2_ycor))

        curser_hitbox = pygame.rect.Rect(mousex, mousey, 1, 1)  

        option_hovering = curser_hitbox.colliderect(quit_rect)
        button_text_multiplier = 1

        if option_hovering:
            button_text_multiplier = 1.1
        
        options_font = pygame.font.Font(cool_font_name, int(50 * button_text_multiplier))

        quit_option_text = options_font.render("Quit", True, TEXT_COL)

        quit_rect = pygame.rect.Rect(W / 2 - quit_option_text.get_width() / 2 * button_text_multiplier - rect_text_gap, 
                                text_l2_ycor + win_text_l2.get_height() + text_gap - rect_text_gap * button_text_multiplier, 
                                quit_option_text.get_width() * button_text_multiplier + rect_text_gap * 2, 
                                quit_option_text.get_height() * (1 + (button_text_multiplier - 1) / 2) + rect_text_gap * 2)
        
        pygame.draw.rect(win, TEXT_COL, quit_rect, rect_tickness)
        win.blit(quit_option_text, (W / 2 - quit_option_text.get_width() / 2, text_l2_ycor + win_text_l2.get_height() + text_gap - quit_option_text.get_height() * (button_text_multiplier - 1) / 2))

        win.blit(curser, (mousex, mousey))

        pygame.display.flip()

        if pygame.mouse.get_pressed()[0] and option_hovering:
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit()


def main():
    level = 1
    main_game = True
    num_bullets = 100
    
    level_width, level_height = 120, 50
    levelcors, colours_levels, names_list, num_levels, level_bgs, num_cols, level_3cols, txt_surfaces, map_blackness_padding = levels_info(level_width, level_height)
    original_cols = colours_levels
    main_bg = start()

    while main_game:

        if not level_bgs:
            game_finished(main_bg)
            main_game = False
            break

        bg1, bg2 = level_bgs.pop(), level_bgs.pop()

        display_level(level, num_levels, level_width, level_height, level_3cols, levelcors, num_cols, colours_levels, original_cols, txt_surfaces, map_blackness_padding)
        loading_screen(bg1, bg2)


        #MAIN LOOP 
        running = True
        clock = pygame.time.Clock()

        zombies_needed_kill = level * 2 + 4
        wait_time = FPS * 5
        wait_counter = 0
        
        #BG
        bg1_xcor, bg2_xcor = 0, W
        bg_speed = 3

        #PLAYER
        player_speed = 7
        player_xcor = W / 30
        player_ycor = (bot_road + top_road) / 2 - player.get_height() / 2
        
        player_health_width, player_health_height = player_width / 1.375 , 20
        player_health_spacing = 10
        player_health_lost_num = 0
        total_player_health = 30
        player_health_offset_xcor = 15 # due to pistol centre gets offset so its under centre of only player

        #ZOMBIE
        zombie_width, zombie_height = player_width, player_height
        zombie = make_image("zombie 1.png", zombie_width, zombie_height, "zombie\\")
        zombie_mask = pygame.mask.from_surface(zombie)
        zombie_health_width, zombie_health_height = zombie_width / 1.5 , 20

        zombie_speed = bg_speed * 1.1
        zombie_xcor = W + 100
        zombie_ycor = H / 2 - zombie_height / 2
        zombie_health_lost_num = 0
        total_zombie_health = 30
        generated_yyet = False
        zombies_killed = 0

        blit_additional_ammo = False
        additional_ammo = None

        #BULLET
        bullet_speed = 30
        bullet_body_spacing = 10
        initial_bulletx = player_xcor + player_width + bullet_body_spacing #.get_width()
        bulletx = initial_bulletx
        shot_dmg = total_zombie_health / 4

        shoot = False
        max_cooldown = W / (1.5 * bullet_speed)
        cooldown = 0
        activate_cooldown = False
        
        no_ammo = False
        no_bullets_length = FPS
        no_bullets_counter = 0

        #FONTS
        level_font = pygame.font.Font(cool_font_name, 100)
        level_name_text = level_font.render(f"Level: {names_list[level - 1]}", True, TEXT_COL)

        bullet_font = pygame.font.Font(cool_font_name, 50)

        def generate_death_ammo(zombiex, zombiey, generated_ammo, ammo, num_bullets):
            if not generated_ammo:
                ammo = randint(0, zombies_needed_kill // 2)
                num_bullets += ammo
                generated_ammo = True

            blit_font = pygame.font.Font(cool_font_name, 25)
            add_ammo_text = blit_font.render(f"+{ammo}", True, TEXT_COL)

            newx = zombiex + zombie_width / 2 - add_ammo_text.get_width() / 2
            newy = zombiey + zombie_height / 2 - add_ammo_text.get_height() / 2

            if ammo != 0 and newx > -add_ammo_text.get_width():
                win.blit(add_ammo_text, (newx, newy))

            return generated_ammo, ammo, num_bullets


        while running:
            win.fill(BLACK)
            clock.tick(FPS)

            num_bullets_text = bullet_font.render(f"Bullets: {num_bullets}", True, TEXT_COL)
            zombies_killed_text = bullet_font.render(f"Zombies killed: {zombies_killed}/{zombies_needed_kill}", True, TEXT_COL)
            
            mousex, mousey = pygame.mouse.get_pos()
            curser_hitbox = pygame.rect.Rect(mousex, mousey, 1, 1)

            pause_button_collding = curser_hitbox.colliderect(pause_button_hitbox)

            if bg1_xcor - bg_speed < -W:
                bg1_xcor = W
            if bg2_xcor - bg_speed < -W:
                bg2_xcor = W
            if zombie_xcor < 0 - zombie_width:
                zombie_health_lost_num = 0
                zombie_xcor = W + 100

            bg1_xcor -= bg_speed
            bg2_xcor -= bg_speed
            if wait_counter < wait_time:
                wait_counter += 1
            else:
                zombie_xcor -= zombie_speed
            
            win.blit(bg1, (bg1_xcor, 0))
            win.blit(bg2, (bg2_xcor, 0))
            win.blit(level_name_text, (W / 2 - level_name_text.get_width() / 2, -8))

            player_max_health = pygame.rect.Rect(player_xcor + player_width / 2 - player_health_width / 2 - player_health_offset_xcor, 
                                                player_ycor + player_height + player_health_spacing, 
                                                player_health_width, 
                                                player_health_height)
            player_health = pygame.rect.Rect(player_xcor + player_width / 2 - player_health_width / 2 - player_health_offset_xcor , 
                                            player_ycor + player_height + player_health_spacing, 
                                            max(0, player_health_width - (player_health_lost_num * player_health_width / total_player_health)) , 
                                            player_health_height)
            
            zombie_too_far = zombie_xcor < player_xcor - 10

            pygame.draw.rect(win, RED, player_max_health)
            pygame.draw.rect(win, DARK_GREEN, player_health)


            zombie_max_health = pygame.rect.Rect(zombie_xcor + player_width / 2 - zombie_health_width / 2,
                                                zombie_ycor + zombie_height, 
                                                zombie_health_width, 
                                                zombie_health_height)
            zombie_health = pygame.rect.Rect(zombie_xcor + zombie_width / 2 - zombie_health_width / 2 , 
                                            zombie_ycor + zombie_height, 
                                            max(1, zombie_health_width - (zombie_health_lost_num * zombie_health_width / total_zombie_health)) , 
                                            zombie_health_height)
            
            zombie_disapear = zombie_health_lost_num >= total_zombie_health # = dead
            
            if not zombie_disapear and not zombie_too_far:
                if not generated_yyet:
                    zombie_ycor = randint(top_road - zombie_height, bot_road - zombie_height)
                    generated_yyet = True

                win.blit(zombie, (zombie_xcor, zombie_ycor))
                pygame.draw.rect(win, RED, zombie_max_health)
                pygame.draw.rect(win, DARK_GREEN, zombie_health)
            else:
                if zombie_too_far:
                    player_health_lost_num += total_player_health // 2
                    if player_health_lost_num >= total_player_health:
                        game_over(bg1)
                        running = False
                        main_game = False
                        break
                else:
                    zombies_killed += 1
                    if zombies_killed >= zombies_needed_kill:
                        win_compensation = level * 5 # bullet increase for winning 
                        num_bullets += win_compensation
                        level_completed_screen(bg1, win_compensation)

                        colours_levels[level - 1] = level_3cols[1]
                        level += 1
                        running = False
                        break

                deadx, deady = zombie_xcor, zombie_ycor
                zombie_health_lost_num = 0
                zombie_xcor = W + 100
                generated_yyet = False
                blit_additional_ammo = True
                generated_ammo = False

            if activate_cooldown:
                cooldown += 1
                if cooldown >= max_cooldown:
                    cooldown = 0
                    activate_cooldown = False

            if shoot and num_bullets > 0:
                if bulletx == initial_bulletx:
                    bullety = player_ycor + player_height / 2.275 - player_bullet.get_width() / 2

                win.blit(player_bullet, (bulletx, bullety))
                bulletx += bullet_speed

                if bullet_mask.overlap(zombie_mask, (zombie_xcor - bulletx , zombie_ycor - bullety)):
                    shoot = False
                    zombie_health_lost_num += shot_dmg
                    bulletx = initial_bulletx
                if bulletx > W + bullet_body_spacing:
                    shoot = False
                    bulletx = initial_bulletx

            if blit_additional_ammo:
                deadx -= bg_speed
                generated_ammo, additional_ammo, num_bullets = generate_death_ammo(deadx, deady, generated_ammo, additional_ammo, num_bullets)
        
            if no_ammo and no_bullets_counter <= no_bullets_length:
                no_bullets_counter += 1
                no_bullets_text = level_font.render("Out of Ammo", True, TEXT_COL)
                win.blit(no_bullets_text, (W / 2 - no_bullets_text.get_width() / 2, H / 2 - no_bullets_text.get_height() / 2))
            else:
                no_bullets_counter = 0
                no_ammo = False

            win.blit(player, (player_xcor, player_ycor))
            win.blit(num_bullets_text, (50 , H - 60 - num_bullets_text.get_height()))
            win.blit(zombies_killed_text, (W - 50 - zombies_killed_text.get_width() , H - 60 - zombies_killed_text.get_height()))
            win.blit(pause_button, (pause_buttonx, pause_buttony))
            win.blit(curser, (mousex, mousey))

            mouse_pressed = pygame.mouse.get_pressed()

            if mouse_pressed[0]:
                if pause_button_collding:
                    global general_vol, music_vol
                    pause_menu(bg1, general_vol, music_vol)

            keys_pressed = pygame.key.get_pressed()

            if (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w] or keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]) and player_ycor > top_road - player_height:
                player_ycor -= player_speed
            if (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s] or keys_pressed[pygame.K_d]or keys_pressed[pygame.K_RIGHT]) and player_ycor < bot_road - player_height:
                player_ycor += player_speed
            if (keys_pressed[pygame.K_SPACE] or mouse_pressed[2]) and num_bullets > 0 and not activate_cooldown and not shoot:
                num_bullets -= 1
                shoot = True
                activate_cooldown = True
            elif keys_pressed[pygame.K_SPACE] and num_bullets == 0:
                no_ammo = True

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    main_game = False
                    break

    pygame.quit()
    quit("Thanks for playing")
    

if __name__ == "__main__":
    main()


            # To do list:
"""
.       audio
. DONE  levels aligned how i wanted
.       dots animation when walking to new level
.       fix bullet ammo gain when kill if still on screen it resests or gives none hypothesis
. DONE  arrangement of level num bullets etc
.       fix if w h change i.e. insead of width = 100, width = W / 10
.       fix button on win game and level complete
.       more efficient e.g. function in fonts
.       rules button for how to play

"""
