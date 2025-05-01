# Control Parameters

DEBUG_MODE = {
    "room_generation"          : False,
    "corridor_generation"      : False,
    "extra_corridor_generation": False
}

OUTPUT_MODE = {
    "ascii"   : False,
    "graphics": True
}

RUNNING_MODE = {
    "brute_force": False,   # create a large number of levels to check if the code crashes
    "level_gen"  : False,   # create levels
    "play"       : True     # gameplay
}

TEST_NUM  = 1000            # numbers of levels to create in "brute force" mode

AUTO_GEN  = False           # run an endless loop of dungeon generation, best in ASCII mode
DELAY     = 5               # show level for n seconds


import pygame
from pygame.color import THECOLORS


# Level Dimensions

LEVEL_WIDTH   =   80    # 80 x 25 reflects a typical 1970s UNIX console
LEVEL_HEIGHT  =   25


# Room Creation

MIN_ROOM_SIZE =    5    # minimal and maximal breadth and width of rooms
MAX_ROOM_SIZE =   10
ROOM_BUFFER   =    3    # buffer between rooms
MAX_ATTEMPTS  = 1000    # max attempts of room generation attempts

MIN_ROOMS     =    5    # minimal and maximal number of rooms to be created
MAX_ROOMS     =   12


# Corridor Creation

THRESHOLD_DISTANCE_FOR_EXTRA_CORRIDORS  = 25
# Alternative: extra_corridor_prob = max(0.1, min(0.5, len(rooms) / 20)). This would create probabilities from
# 10 % to 50 %, based on the level density (i.e., the number of rooms). Lots of parameters to play with!
PROBABILITY_FOR_EXTRA_CORRIDOR_CREATION =  0.25


# ASCII Representation

H_WALL        = "-"
V_WALL        = "|"
FLOOR_TILE    = "."
STANDARD_DOOR = "+"
CORRIDOR_TILE = "#"
ROCK_TILE     = " "
EXIT_TILE     = ">"
PLAYER_TILE   = "@"


# Graphics Output

TILE_SIZE        = 20       # tile size in pixels
COLOR_FLOOR      = THECOLORS["grey40"]
COLOR_WALL       = THECOLORS["black"]
COLOR_CORRIDOR   = THECOLORS["grey"]
COLOR_DOOR       = THECOLORS["darkorange"]
COLOR_BACKGROUND = THECOLORS["ghostwhite"]
PLAYER_COLOR     = THECOLORS["red"]
TEXT_COLOR       = THECOLORS["blue"]
EXIT_COLOR       = THECOLORS["green"]


# Keyboard Behavior
# Took a bit of time to create a natural feel for this

INITIAL_DELAY   = 400  # delay before repeats start with pressed keys (in ms)
REPEAT_INTERVAL =  40  # delay between repeats


# Movement Keys

KNOWN_KEYS = {
    "up": [pygame.K_UP, pygame.K_w],  # up arrow and W key
    "down": [pygame.K_DOWN, pygame.K_s],  # down arrow and S key
    "left": [pygame.K_LEFT, pygame.K_a],  # left arrow and A key
    "right": [pygame.K_RIGHT, pygame.K_d]  # right arrow and D key
}