"""
This is a wild mix of some small utility functions
and a lot of debugging helpers I needed and didn't want to discard completely.
"""


def article(string):
    """
    "an apple" vs. "a banana"
    """

    return "an" if string[0] in "aeiou" else "a"


def debug_move(dir, curr, next, status):
    """
    Give info about an intended movement.
    """

    print(f"DEBUG: Trying to move {dir} from {curr} to {next} with exit status {status}.")


def debug_round(curr, prev, fl):
    """
    Debugger for last round: from where to where did the character move?
    """

    print("\t --> DEBUG: current room", curr + ".  Previous room", prev + ".")
    print("\t -->        in_maze flag", fl + ".")


def debug_parser (ac, v, o):
    """
    Show what the parser has done.
    """

    print(f"DEBUG: The parser split the input to '{v}' and '{o}',\n       action class {ac}.")


def show_all_rooms_info(rooms):
    """
    This function gives an overview of the rooms and doors.
    """

    print("\nROOM STATUS DEBUGGER\n")

    for room_name, room in rooms.items():
        print(f"Room: {room.name.title()}")
        print(f"Description: {room.descriptor}")
        room.show_items()

        print("Exits: ", end="")
        first_line = True
        for direction, exit in enumerate(room.exits):
            status, destination = exit
            if status:
                if first_line:
                    print(f"{MAIN_DIRECTIONS[direction]} to {rooms[destination].name.title()} ({EXIT_STATUS[status]})")
                    first_line = False
                else:
                    print(f"       {MAIN_DIRECTIONS[direction]}: {destination} ({EXIT_STATUS[status]})")
        print("")


def show_all_rooms_inventories(rooms):
    """
    This functions shows all items that are placed in rooms.
    """

    print("DEBUGGER: OBJECTS & INVENTORIES")
    for room_name, room in rooms.items():
        print(f"Room: {room_name} // ", end="")
        room.show_items()


def split_at_first_whitespace(string):
    """
    This function splits a string at the first whitespace character.
    """

    if not string:
        return None, None

    parts = str(string).split(maxsplit=1)
    return (parts[0], parts[1]) if len(parts) == 2 else (parts[0], None)


def test_item_management():
    """
    This function runs a series of tests to see if the item management works.
    """

    print("\nITEM MANAGEMENT DEBUGGER\n")
    print("Initial contents of personal inventory, hallway, and living room:")

    player.show_inventory()
    rooms["HALLWAY"].show_items()
    rooms["LIVING_ROOM"].show_items()

    print("\nTaking lamp from hallway to personal inventory:")

    item_manager.move_item(rooms["HALLWAY"], player, items[3])

    player.show_inventory()
    rooms["HALLWAY"].show_items()
    rooms["LIVING_ROOM"].show_items()

    print("\nDropping lamp from personal inventory to living room:")

    item_manager.move_item(player, rooms["LIVING_ROOM"], items[3])

    player.show_inventory()
    rooms["HALLWAY"].show_items()
    rooms["LIVING_ROOM"].show_items()