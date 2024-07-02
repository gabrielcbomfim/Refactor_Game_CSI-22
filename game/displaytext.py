import os
from data.text import Font
def load_font_img():
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    dir = os.path.join(parent_dir, 'data', 'fonts', 'small_font.png')

    main_font = Font(dir, (255, 255, 255))
    black_font = Font(dir, (0, 0, 1))
    return main_font, black_font
def DisplayText(gd, global_time, display, main_font, black_font):
    offset_y = 1 if global_time % 90 > 80 else 0
    if gd.display_tutorial_text:
        if gd.current_level == 1:
            black_font.render('shoot spores with arrow keys', display, (
            gd.player.center[0] - gd.scroll[0] - main_font.width('shoot spores with arrow keys') // 2 + 1,
            gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
            main_font.render('shoot spores with arrow keys', display, (
            gd.player.center[0] - gd.scroll[0] - main_font.width('shoot spores with arrow keys') // 2,
            gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))
        if (gd.current_level == 2) and (gd.spores_left > 0):
            black_font.render('destroy red orbs', display, (
            gd.player.center[0] - gd.scroll[0] - main_font.width('destroy red orbs') // 2 + 1,
            gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
            main_font.render('destroy red orbs', display, (
            gd.player.center[0] - gd.scroll[0] - main_font.width('destroy red orbs') // 2,
            gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))

    if gd.spores_left <= 0:
        black_font.render('out of spores! press "r"', display, (
        gd.player.center[0] - gd.scroll[0] - main_font.width('out of spores! press "r"') // 2 + 1,
        gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
        main_font.render('out of spores! press "r"', display, (
        gd.player.center[0] - gd.scroll[0] - main_font.width('out of spores! press "r"') // 2,
        gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))

    if gd.current_level == 8:
        black_font.render('thanks for playing!', display, (
        gd.player.center[0] - gd.scroll[0] - main_font.width('thanks for playing!') // 2 + 1,
        gd.player.pos[1] - 11 - gd.scroll[1] + offset_y))
        main_font.render('thanks for playing!', display, (
        gd.player.center[0] - gd.scroll[0] - main_font.width('thanks for playing!') // 2,
        gd.player.pos[1] - 12 - gd.scroll[1] + offset_y))