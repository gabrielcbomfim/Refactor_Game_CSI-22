
import sys
import os


main_font = Font('data/fonts/small_font.png', (255, 255, 255))
black_font = Font('data/fonts/small_font.png', (0, 0, 1))

def DisplayText(gd, global_time, display):
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