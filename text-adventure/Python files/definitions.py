# Door status, main directions
NONE, LOCKED, CLOSED, OPEN = range(4)
EXIT_STATUS = ["none", "locked", "closed", "open"]
NORTH, WEST, SOUTH, EAST = range (4)
MAIN_DIRECTIONS = ["N", "W", "S", "E"]

# commands: verbs (keys) and action codes (values)
verb_dictionary = {
    "quit": 0, "q": 0, "exit": 0, "end": 0, "surrender": 0,
    "go": 1, "walk": 1, "move": 1, "proceed": 1, "head": 1, "travel": 1, "explore": 1, "navigate": 1, "run": 1, "wander": 1, "venture": 1, "stroll": 1,
    "north": 1, "n": 1, "west": 1, "w": 1, "south": 1, "s": 1, "east": 1, "e": 1,
    "dance": 2, "sing": 2, "entertain": 2, "perform": 2,
    "say": 3, "utter": 3, "scream": 3,
    "wait": 4,
    "kill": 5, "punch": 5, "kick": 5, "hit": 5, "destroy": 5, "fight": 5, "stomp": 5,
    "get": 6, "take": 6, "obtain": 6, "fetch": 6, "collect": 6, "receive": 6, "grab": 6, "acquire": 6, "attain": 6, "gain": 6,
    "i": 7, "inventory": 7,
    "drop": 8, "ditch": 8, "throw": 8, "toss": 8, "release": 8, "leave": 8, "discharge": 8, "relinquish": 8, "discard": 8, "abandon": 8,
    "open": 9,
    "close": 10,
    "unlock": 11, "unseal": 11, "unbolt": 11, "unlatch": 11, "unblock": 11, "unchain": 11,
    "lock": 12, "secure": 12, "seal": 12, "bolt": 12, "latch": 12, "block": 12, "chain": 12,
    "examine": 13, "x": 13,
    "brief": 14,
    "verbose": 15,
    "look": 16, "l": 16,
    "talk": 17, "speak": 17, "converse": 17, "chat": 17, "ask": 17,
    "combine": 18, "craft": 18, "use": 18, "mix": 18,
    "status": 19, "stats": 19,
    "commands": 20, "help": 20, "verbs": 20,
    "eat": 21, "consume": 21,
    "drink": 22, "gulp": 22
}
