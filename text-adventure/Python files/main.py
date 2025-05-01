import random

from definitions import *
from world       import World
from room        import Room
from item        import ItemManager, Item
from player      import Player
from npc         import NPC, DynamicNPC
from utilities   import article, split_at_first_whitespace


# Import debugging functions if needed
# from utilities   import debug_move, debug_round, debug_parser
# from utilities   import show_all_rooms_info, show_all_rooms_inventories, test_item_management


# Functions to initialize game world

def add_npcs_to_rooms(npcs, rooms):
    """
    Add all NPCs to their starting rooms.
    """

    for npc in npcs.values():
        rooms[npc.location].add_npc(npc)


def create_map():
    """
    Define and create the map layout.
    In a real game, this might better be loaded from a JSON file.
    """

    rooms = {
        "HALLWAY": Room(
            "hallway",
            "You are standing in the hallway. One door leads to the west to the other rooms, while the front door leads outside to the east. You can hear the sound of cars driving by. A door to the north leads to your garden.",
            [[CLOSED, "GARDEN"], [CLOSED, "LIVING_ROOM"], [NONE, ""], [LOCKED, "OUTSIDE"]]),

        "LIVING_ROOM": Room(
            "living room",
            "You are in the living room. There are doors leading in all directions.",
            [[CLOSED, "BEDROOM"], [CLOSED, "KITCHEN"], [CLOSED, "BATHROOM"], [CLOSED, "HALLWAY"]]),

        "BATHROOM": Room(
            "bathroom",
            "You are standing in a small, cramped bathroom. In the south, you can spot an ominous portal leading into a dark abyss. You can return to the safety of your living room by taking the north door.",
            [[CLOSED, "LIVING_ROOM"], [NONE, ""], [OPEN, "PASSAGES"], [NONE, ""]]),

        "KITCHEN": Room(
            "kitchen",
            "The kitchen is surprisingly large, but very untidy. You can escape the mess by going back east into the living room.",
            [[NONE, ""], [NONE, ""], [NONE, ""], [CLOSED, "LIVING_ROOM"]]),

        "BEDROOM": Room(
            "bedroom",
            "You are in your bedroom. Outside, you hear birds chirping.",
            [[NONE, ""], [LOCKED, "LIBRARY"], [CLOSED, "LIVING_ROOM"], [NONE, ""]]),

        "OUTSIDE": Room(
            "outside",
            "You have finally reached the outside.",
            [[NONE, ""], [LOCKED, "HALLWAY"], [NONE, ""], [NONE, ""]]),

        "PASSAGES": Room(
            "labyrinth",
            "You are in a maze of twisty little passages, all alike.",
            [[OPEN, "BATHROOM"], [NONE, ""], [NONE, ""], [NONE, ""]]),

        "GARDEN": Room(
            "garden",
            "You are in a small garden. A small white fence shields it from the street and the adjacent small gardens. Small white clouds are reflected in the water of your small pond surrounded by a small patch of lawn. Chirping with a small voice, a small bird sits on a small tree. A sense of idyllic bliss washes over you, producing a small smile on your small face.",
            [[NONE, ""], [NONE, ""], [CLOSED, "HALLWAY"], [NONE, ""]]),
        
        "LIBRARY": Room(
            "library",
            "You are in a dimly lit library filled with ancient books and scrolls. Dust motes dance in the slivers of light that pierce through the high, narrow windows. Shelves line the walls from floor to ceiling, packed with volumes whose titles have long faded. The scent of old paper and leather bindings fills the air, mingling with a faint hint of something else. Perhaps it's magic, or the secrets of ages past, or rotten cheese. A heavy silence pervades the room, broken only by the occasional creak of the wooden floorboards underfoot and the occasional aches of an old man pondering ancient lore at an impressively carved oak table.",
            [[CLOSED, "LABORATORY"], [NONE, ""], [NONE, ""], [LOCKED, "BEDROOM"]]),
        
        "LABORATORY": Room(
        "laboratory",
        "You are in an alchemist's laboratory, filled with strange apparatus and the pungent smell of herbs and chemicals. Shelves are crammed with jars of mysterious substances, and a large cauldron bubbles over a fire. Ancient tomes and alchemical texts lie open on a sturdy wooden table, hinting at experiments both successful and disastrously failed. You especially notice a handwritten note, a translucent powder, and an eerie silver potion.",
        [[NONE, ""], [NONE, ""], [CLOSED, "LIBRARY"], [NONE, ""]]
        )
    }
    return rooms


def create_items(rooms, item_manager):
    """
    Define and create the items (again, this might be loaded from a JSON file),
    then populate rooms with items.
    """

    items = [
        Item("key", "This is a plain metal key that unlocks every door in your apartment.", "KEY", [""]),

        Item("apple", "This apple looks healthy. Or is it poisoned?", "FOOD", ["fruit", "vegetable"], is_poisonous=True),

        Item("bottle of water", "The blueish-tinted bottle contains clear water. This has to taste boring.", "DRINK", ["water", "flask", "jug", "bottle"]),

        Item("lamp", "This brass lantern looks like it comes from another game.", "LAMP", ["light", "lantern"]),

        Item("towel", "This is a large, soft, red towel. You feel well-prepared just looking at and admiring it.", "OTHER", ["cloth", "washcloth"]),

        Item("leaf-blower", "This is a state-of-the-art leaf-blower powered by the latest AI technology. It will automatically detect falling leaves, blowing them right into your least favorite neighbors' garden. Made of titanium-enforced aluminum, it looks as good as it was overpriced. Pity it's broke.", "OTHER", ["blower", "device", "apparatus"]),

        Item("axe", "You carefully examine this sharp, deadly axe and ponder that you will probably never need to use it.", "WEAPON", "weapon"),

        Item("broom", "The broomstick is long enough to be a flagpole.", "OTHER", ["broomstick", "stick"]),

        Item("flag", "This is a red flag. How metaphoric!", "OTHER", []),

        Item("book", "An old, dust-covered folio tome that looks like it contains forbidden knowledge. Or is it a recipe book?", "OTHER", ["volume", "tome"]),

        Item("scroll", "Gnawed by worms, this ancient scroll of parchment (or is it papyrus?) seems to have endured millennia. It might hold Mesopotamian curses. Attempting to read it will surely drive you beyond the thin veil that separates sanity from utter madness -- and right into the realm of really bad ideas. (I hope you read that with a loud droning voice in your head.)", "OTHER", ["parchment", "manuscript", "roll", "codex", "papyrus"]),

        Item("note", "You decipher a text written on this note in small, spidery letters: 'If thou mixeth the powder of translucency with the moonlight potion, thy result shall be of the most peculiar kynde.'", "OTHER", []),

        Item("powder", "The translucent powder shimmers faintly in the light, its particles so fine they seem to float like ethereal dust. It has an almost otherworldly quality, appearing nearly invisible except for the subtle glint that betrays its presence.", "OTHER", []),

        Item("potion", "The moonlight potion glows with a soft, silvery luminescence, resembling liquid moonbeams captured in a bottle. Its surface undulates gently, casting delicate patterns of light and shadow. It emits a gentle and serene light.", "OTHER", []),

        Item("gum", "It's a strip of chewing gum. It has a light mint flavor.", "OTHER", ["chewing gum", "chewing"]),

        Item("table", "Tim sits at an impressive, heavy-looking oaken table. You see ancient runes carved into its sides.", "FURNITURE", [], is_movable=False, is_visible=False),

        Item("bookshelves", "The bookshelves tower above you, their dark, Gothic architecture casting intricate shadows on the walls. Each shelf is meticulously carved, with ornate arches and pointed spires that seem to reach for the ceiling. Every inch of space is occupied by ancient, leather-bound books in varying sizes, bindings, and languages.", "FURNITURE", ["shelf", "bookshelf", "shelves"], is_movable=False, is_visible=False),

        Item("cake", "You see a perfect cake standing on the counter.", "FOOD", []),

        Item("cup of tea", "It's a cup of tea. It seems to be just at the right temperature for drinking.", "DRINK", ["cup", "tea"], is_healing=True)
    ]

    # As the item position management is done in the Room class, I did not specify a room info in the
    # item definition. As a result, rooms are allocated 'manually' now. If this would be loaded from a file,
    # initial item positions might be added directly there.
    item_manager.add_item(rooms["LIVING_ROOM"], items[0])       # key
    item_manager.add_item(rooms["KITCHEN"],     items[1])       # apple
    item_manager.add_item(rooms["KITCHEN"],     items[2])       # bottle
    item_manager.add_item(rooms["HALLWAY"],     items[3])       # lamp
    item_manager.add_item(rooms["BATHROOM"],    items[4])       # towel
    item_manager.add_item(rooms["GARDEN"],      items[5])       # leaf-blower
    item_manager.add_item(rooms["BEDROOM"],     items[6])       # axe
    item_manager.add_item(rooms["KITCHEN"],     items[7])       # broom
    item_manager.add_item(rooms["LIBRARY"],     items[9])       # book
    item_manager.add_item(rooms["LIBRARY"],     items[10])      # scroll
    item_manager.add_item(rooms["LABORATORY"],  items[11])      # note
    item_manager.add_item(rooms["LABORATORY"],  items[12])      # powder
    item_manager.add_item(rooms["LABORATORY"],  items[13])      # potion
    item_manager.add_item(rooms["LIBRARY"],     items[15])      # table
    item_manager.add_item(rooms["LIBRARY"],     items[16])      # bookshelves
    item_manager.add_item(rooms["KITCHEN"],     items[17])      # cake
    item_manager.add_item(rooms["KITCHEN"],     items[18])      # tea

    return items


def create_npcs():
    """
    Finally, this function defines and creates the NPCs.
    NPC characters are static (i.e., they stay where they are unless hard-codedly moved around),
    DynamicNPC characters move around freely and independently of player actions.
    """

    # Default answers are given when the player doesn't specify a conversation topic.
    npcs = {
        "stranger": NPC("Tim", "With his pointed hat, long beard, and wooden staff, Tim looks like a wizard.",
            {"anne"       : "What an enchanting personality she has!",
             "book"       : "Read it carefully if you dare. The scrambled-eggs recipe is really delicious.",
             "books"      : "Some of the books in this library contain centuries-old secret knowledge.",
             "catalog"    : "There is no catalog.",
             "door"       : "The door to the outside? It opens with a key.",
             "dumbledore" : "He's dead.",
             "flag"       : "Oh. That's a red flag to me.",
             "game"       : "Well, it's not good, but it's where I live.",
             "gandalf"    : "Distant relative of mine.",
             "job"        : "I'm a wizard, Harry!",
             "leaf-blower": "It works like magic!",
             "library"    : "So you finally found the secret library. Be careful of what it contains.",
             "player"     : "I am sure you are doing your best.",
             "python"     : "A deadly snake, daughter of lindworms, mother of dragons!",
             "quest"      : "Venture forth, adventurer! The world is waiting!",
             "rincewind"  : "Has he finally graduated?",
             "rumors"     : "I've heard of treasure outside.",
             "scroll"     : "Nobody ever dared to read this ancient scroll.",
             "weather"    : "Nice sunny day, eh?",
             "default"    : ["Good day!", "How do you do?", "What a nice day!", "Greetings!", "Shush!", "Quiet!"]
        }, "LIBRARY"),

        "neighbor": DynamicNPC("Anne", "Your neighbor Anne always looks like there's a bad smell in the air. Her perpetually sour expression is a perfect match for her notoriously bad temper.",
            {"adventure": "Adventure? More like a waste of time!",
             "friends"  : "Friends? You???",
             "game"     : "It's a poorly programmed abomination.",
             "help"     : "Me helping you? Think again.",
             "job"      : "Yeah, you should sure find one.",
             "library"  : "A library is a collection of books, you fool.",
             "player"   : "Well. You. Not much to say about you.",
             "quest"    : "Do I look like a quest giver? Do you think I'm an NPC!?",
             "rumors"   : "People say you're dumb.",
             "scroll"   : "You mean that dusty old thing? Why bother?",
             "tim"      : "Guess he read too much novels.",
             "weather"  : "What an original topic.",
             "world"    : "Don't ask me, it's all so bad.",
             "default"  : ["Hey.", "Please get out of my way.", "Sorry, I just can't stand you."]
            }, "KITCHEN")
    }
    return npcs


# Game logic functions

def parse_input(string):
    """
    Mostly an elementary two-token parsing routine splits up after first whitespace.
    The result is verb (command) and "object".
    Action classes are looked up in the verb_dictionary.
    There's a hint of a three-token parser for AC 17,
    and there's another three-token routine at "combine" below that should be moved here.
    This parser might be expanded to a real multiple-token parser,
    and there might be a possibility to store commands in a list to enable "n, w, e"
    or "do this THEN do that" sequences.
    """

    action_class = None
    verb, obj = split_at_first_whitespace(string)

    if verb in verb_dictionary:
        action_class = verb_dictionary[verb]

    if verb in ["north", "n", "west", "w", "south", "s", "east", "e"]:
        obj = verb                          # the move function expects the direction as obj

    elif action_class == 17:                # AC 17 is "talk to NPC"
        if obj and obj.startswith("to "):
            obj = obj[3:]                   # remove the "to " from the object (= name)

    return action_class, verb, obj


def twisty_little_passages():
    """
    A rudimentary implementation of a labyrinth with a 20 percent escaping chance
    """

    passages = [
        (90, "You see the skeleton of an unlucky adventurer in the distance. "),
        (80, "You hear eerie sounds from far away. "),
        (70, "A sullen werewolf passes. "),
        (60, "You have a bad feeling about this. "),
        (50, "It is pitch black. You are likely to be eaten by a grue. "),
        (40, "The walls seem to close in on you. "),
        (30, "The ground shakes slightly. "),
        (20, "Your senses fail you. "),
        (10, "A passing ghoul politely greets you but ushers on. "),
        ( 0, "It's getting uncomfortably hot. ")
    ]

    rn = random.randint(0, 100)

    for threshold, message in passages:
        if rn >= threshold:
            print(message, end="")
            break

    return random.randint(0, 100) >= 20                 # 20 % chance to escape


# Main game loop and main (init) function

def game_loop():
    """
    This is the main game loop.
    """

    print("TINY TEXT ADVENTURE")
    print("-------------------")
    print("Welcome! You just woke up and your quest is to leave the apartment.")

    moves_counter = 0                                   # counter for player moves
    in_maze = False                                     # is player in maze?
    found_out = False                                   # has player found out of the apartment?
    look_around = False                                 # give full descriptions at next round
    verbose = False                                     # verbose mode off/on
    quit = False                                        # player wants to quit the game
    current_room = "BEDROOM"                            # starting point
    previous_room = ""
    prev_obj = None                                     # enable "it" replacing objects

    while True:
        # Determine if long or short feedback is to be displayed.
        if current_room != previous_room or look_around or in_maze or verbose:
            if verbose or (not rooms[current_room].visited) or look_around or not in_maze:
                print(rooms[current_room].descriptor)
                rooms[current_room].show_items()
                rooms[current_room].show_npcs()
                rooms[current_room].show_exits(rooms)
            else:
                print("You are in the", rooms[current_room].name.lower() + ".")
                rooms[current_room].show_items()
                rooms[current_room].show_npcs()
                rooms[current_room].show_exits(rooms)

        previous_room = current_room

        look_around = False                                 # reset flag (set to True for "look" command)
        rooms[current_room].visited = True                  # mark the room as visited
        moves_counter += 1

        if moves_counter % 2:                               # dynamic NPCs move every second turn (might be randomized)
            for npc_key, npc in npcs.items():
                if isinstance(npc, DynamicNPC):
                    npc.move(current_room, rooms)

        action_class = None

        while action_class == None:                         # get input
            action_class, verb, obj = parse_input(input("> ").strip().lower())

            # For some action classes, "it" will refer to the last object in use.
            # For example, "examine apple" -- "take it"
            if action_class in [6, 8, 13, 21, 22] and obj == "it" and prev_obj:
                obj = prev_obj

            if random.random() < 0.1:                           # 10% chance to update weather
                game_world.update_weather()

            if action_class == None and verb:                   # unknown command
                print("I do not know how to do this.")

            if action_class == 0:                               # quit game: set flag
                quit = game_world.quit()
                break

            elif action_class == 1:                             # move player somewhere
                current_room = player.move(obj, in_maze, rooms)

            elif action_class == 2:                             # perform
                player.perform()

            elif action_class == 3:                             # say something
                player.say(obj)

            elif action_class == 4:                             # wait
                game_world.wait()

            elif action_class == 5:                             # kill
                player.go_berserk()

            elif action_class == 6:                             # get item
                item_manager.get_item(current_room, obj, rooms, player)

            elif action_class == 7:                             # inventory
                player.show_inventory()
                moves_counter -= 1

            elif action_class == 8:                             # drop, throw
                if in_maze:                                     # prevent dropping stuff in the maze
                    print("You would never find this again in this labyrinth!")
                else:
                    item_manager.drop_item(current_room, obj, rooms, player)

            elif action_class == 9:                             # open door
                rooms[current_room].open_door(obj, rooms)

            elif action_class == 10:                            # close door
                rooms[current_room].close_door(obj, rooms)

            elif action_class == 11:                            # unlock door
                rooms[current_room].unlock_door(obj, current_room, rooms, player)

            elif action_class == 12:                            # lock door
                rooms[current_room].lock_door(obj, current_room, rooms, player)

            elif action_class == 13:                            # examine an item
                item_manager.examine_item(obj, current_room, rooms, player, npcs)

            elif action_class == 14:                            # turn to brief mode
                verbose = game_world.enable_brief_mode(verbose)
                moves_counter -= 1

            elif action_class == 15:                            # turn to verbose mode
                verbose = game_world.enable_verbose_mode(verbose)
                moves_counter -= 1

            elif action_class == 16:                            # look around room
                look_around = game_world.look_around()

            elif action_class == 17:                            # talk to NPC
                if obj and " about " in obj:                    # additional code to simulate a multiple-word parser
                    name, topic = obj.split(" about ")          # see following comments
                    player.talk_to_npc(name, npcs, topic)
                else:
                    if obj and " about" in obj:
                        obj, about = obj.split(" about")
                    player.talk_to_npc(obj, npcs)

            elif action_class == 18:                            # combine items
                if obj:                                         # additional code to simulate a multiple-word parser
                    if " and " in obj:                          #            (a nicer solution would be to do this in
                        item1, item2 = obj.split(" and ")       #             the parser function and return a list
                    elif " with " in obj:                       #             of objects)
                        item1, item2 = obj.split(" with ")
                    elif obj.endswith(" and"):
                        item1 = obj[:-len(" and")]
                        item2 = None
                    elif obj.endswith(" with"):
                        item1 = obj[:-len(" with")]
                        item2 = None
                    elif " " in obj:
                        item1, item2 = obj.split(" ")
                    else:
                        item1 = obj
                        item2 = None
                else:
                    item1 = None
                    item2 = None
                try:
                    item1.strip()
                    item2.strip()
                except:
                    pass
                item_manager.combine_items(player, rooms, items, item1, item2)

            elif action_class == 19:                            # show status
                player.show_stats()

            elif action_class == 20:                            # show all commands
                game_world.commands(verb_dictionary)

            elif action_class == 21:                            # eat
                item_manager.eat_item(current_room, obj, rooms, player)

            elif action_class == 22:                            # drink
                item_manager.drink_item(current_room, obj, rooms, player)

            # Prepare the "it" / previous object substitution for suitable action classes
            if action_class in [6, 8, 13, 21, 22] and obj:
                prev_obj = obj
            else:
                prev_obj = None

        if current_room == "OUTSIDE":                       # game solved
            found_out = True
            break

        if quit:
            break

        if current_room == "PASSAGES":                      # player is in maze
            in_maze = True

        if in_maze:
            in_maze = twisty_little_passages()              # labyrinth output and decision about escape

            if not in_maze:
                print("You miraculously escape the maze. Phew, close call!")
                current_room = "BATHROOM"
                previous_room = "BATHROOM"
                player.move("n", False, rooms)               # move player out of labyrinth
                look_around = True

            if quit or found_out:
                break

    # Out of the main loop: player has either quit or solved the game
    if quit:
        print("You spectacularly failed your quest to save life, the universe, and everything. Actually, you did not even find out of your own apartment.", end=" ")

    else:
        print(rooms["OUTSIDE"].descriptor, end=" ")
        print(f"You took {len(player.items)} items with you.", end=" ")
    print(f"Thank you for playing this useless game for {moves_counter} moves.")



"""
Create heaven and earth ;) ,
then start the game
"""

game_world = World()
rooms = create_map()
item_manager = ItemManager()
items = create_items(rooms, item_manager)
player = Player()
npcs = create_npcs()
add_npcs_to_rooms(npcs, rooms)

game_loop()

input("\nPress ENTER to close the window.")