from definitions import *
from item        import item_manager
from utilities   import article


class Room:
    """
    This class controls everything related to rooms.
    """

    def __init__(self, name, descriptor, exits, visited=False):
        """
        Init function
        """

        self.name = name                  # room name
        self.descriptor = descriptor      # room description
        self.exits = exits                # list of [status, destination] for NWSE
        self.visited = visited            # True/False flag
        self.items = []                   # list of items in the room
        self.npcs = []                    # list of NPCs in the room

    def add_npc(self, npc):
        """
        Add an NPC to the NPCs list of a specific room.
        """

        self.npcs.append(npc)

    def close_door(self, direction, rooms):
        """
        Close a door.
        """

        available_directions = [
            i for i, exit in enumerate(self.exits) if exit[0] in [OPEN, CLOSED, LOCKED]     # excluding NONE
        ]

        if not direction or direction == "door":                # no direction given
            if len(available_directions) == 1:                  # just one door available? take it
                dir_index = available_directions[0]
                direction = MAIN_DIRECTIONS[dir_index].lower()

            elif len(available_directions) == 0:                # no doors available? should not occur
                print("There are no doors. I wonder how you came in.")
                return

            else:                                               # let player choose a direction
                self.show_exits(rooms)
                direction = input("Which door do you want to close? ").strip().lower()
                if not direction:
                    return

        if direction not in ["n", "north", "w", "west", "s", "south", "east", "e"]:
            print("Invalid direction.")
            return

        dir_index = MAIN_DIRECTIONS.index(direction[0].upper())
        exit_status, destination = self.exits[dir_index]

        if exit_status == OPEN:
            self.exits[dir_index][0] = CLOSED
            rooms[destination].exits[(dir_index + 2) % 4][0] = CLOSED
            print("You close the door.")

        elif exit_status == CLOSED:
            print("The door is already closed.")

        elif exit_status == LOCKED:
            print("Wanna close a locked door, eh!? Good luck with that.")

        else:
            print("In your mind, you quietly close the imaginary door. In reality, nothing happens.")

    def display_room(self):
        """
        Show all info about a room.
        """

        print(self.descriptor)
        self.show_items()
        self.show_npcs()
        self.show_exits()

    def find_npc(self, npc_name, npcs, current_room):
        """
        Look for a NPC in the current room.
        """

        npc_name_lower = npc_name.lower()

        for key, npc in npcs.items():
            if (key.lower() == npc_name_lower or npc.name.lower() == npc_name_lower) and npc.location == current_room:
                return npc

        return None

    def lock_door(self, direction, current_room, rooms, player):
        """
        Lock a door.
        """

        available_directions = [i for i, exit in enumerate(self.exits) if exit[0] in [CLOSED, LOCKED, OPEN]]

        if not direction or direction == "door":                    # see above at "close door"
            if len(available_directions) == 1:
                dir_index = available_directions[0]
                direction = MAIN_DIRECTIONS[dir_index].lower()

            elif len(available_directions) == 0:
                print("There are no doors. I wonder how you came in.")
                return

            else:
                self.show_exits(rooms)
                direction = input("Which door do you want to lock? ").strip().lower()
                if not direction:
                    return

        if direction not in ["n", "north", "w", "west", "s", "south", "east", "e"]:
            print("Invalid direction.")
            return

        dir_index = MAIN_DIRECTIONS.index(direction[0].upper())
        exit_status, destination = self.exits[dir_index]

        if item_manager.is_item_in_room("key", current_room, rooms):    # key in current room's inventory
            print("You should take the key first.")
            return

        if not item_manager.is_item_in_inventory("key", rooms, player): # key not in player's inventory
            print("You have no key.")
            return

        if exit_status == CLOSED or exit_status == OPEN:
            self.exits[dir_index][0] = LOCKED
            rooms[destination].exits[(dir_index + 2) % 4][0] = LOCKED
            print("You lock the door.")

        elif exit_status == LOCKED:
            print("The door is already locked.")

        else:
            print("You try to lock the imaginary door.")

    def open_door(self, direction, rooms):
        """
        Open a door.
        """

        available_directions = [i for i, exit in enumerate(self.exits) if exit[0] in [CLOSED, LOCKED, OPEN]]

        if not direction or direction == "door":                    # see above at "close door"
            if len(available_directions) == 1:
                dir_index = available_directions[0]
                direction = MAIN_DIRECTIONS[dir_index].lower()

            elif len(available_directions) == 0:
                print("There are no doors. I wonder how you came in.")
                return

            else:
                self.show_exits(rooms)
                direction = input("Which door do you want to open? ").strip().lower()
                if not direction:
                    return

        if direction not in ["n", "north", "w", "west", "s", "south", "east", "e"]:
            print("Invalid direction.")
            return

        dir_index = MAIN_DIRECTIONS.index(direction[0].upper())
        exit_status, destination = self.exits[dir_index]

        if exit_status == CLOSED:
            self.exits[dir_index][0] = OPEN
            rooms[destination].exits[(dir_index + 2) % 4][0] = OPEN
            print("You open the door.")

        elif exit_status == OPEN:
            print("The door is already open.")

        elif exit_status == LOCKED:
            print("The door is locked.")

        else:
            print("You try to open the imaginary door.")

    def remove_npc(self, npc):
        """
        Remove an NPC from the NPCs list of a specific room.
        """

        self.npcs.remove(npc)

    def show_exits(self, rooms):
        """
        Display all exits from a room.
        """

        # This should never happen
        if not self.exits:
            print("There are no exits here. I wonder how you came in.")

        else:
            exits_list = []
            for direction, exit in enumerate(self.exits):
                status, destination = exit
                if status:
                    # I want to differentiate between rooms that the player has already visited
                    # and doors leading to "unknown" rooms; in one case, the game will display
                    # the adjacent room name, in the other case, it will only give the direction
                    if rooms[destination].visited:
                        exits_list.append(f"{MAIN_DIRECTIONS[direction]} to {rooms[destination].name} ({EXIT_STATUS[status]})")
                    else:
                        exits_list.append(f"{MAIN_DIRECTIONS[direction]} ({EXIT_STATUS[status]})")
            print("Exits: " + ", ".join(exits_list) + ".")

    def show_items(self):
        """
        Show the items in the current room's inventory.
        """

        if self.items:
            output_string = ", ".join([f"{article(item.name)} {item.name}" for item in self.items if item.is_visible])
            print(f"In the {self.name}, you see: {output_string}.")

    def show_npcs(self):
        """
        Show all NPCs in the current room.
        """

        if self.npcs:
            # " and " works right now with two NPCs, but it needs to be changed to ", " for more
            npc_names = " and ".join([npc.name for npc in self.npcs])
            verb = "are" if " and " in npc_names else "is"
            print(f"{npc_names}", verb, "here.")

    def unlock_door(self, direction, current_room, rooms, player):
        """
        Unlock a door.
        """

        available_directions = [i for i, exit in enumerate(self.exits) if exit[0] in [CLOSED, LOCKED, OPEN]]

        if not direction or direction == "door":                    # see above at "close door"
            if len(available_directions) == 1:
                dir_index = available_directions[0]
                direction = MAIN_DIRECTIONS[dir_index].lower()

            elif len(available_directions) == 0:
                print("There are no doors. I wonder how you came in.")
                return

            else:
                self.show_exits(rooms)
                direction = input("Which door do you want to unlock? ").strip().lower()
                if not direction:
                    return

        if direction not in ["n", "north", "w", "west", "s", "south", "east", "e"]:
            print("Invalid direction.")
            return

        dir_index = MAIN_DIRECTIONS.index(direction[0].upper())
        exit_status, destination = self.exits[dir_index]

        if item_manager.is_item_in_room("key", current_room, rooms):        # see above at "lock door"
            print("You should take the key first.")
            return

        if not item_manager.is_item_in_inventory("key", rooms, player):
            print("You have no key.")
            return

        if exit_status == LOCKED:
            self.exits[dir_index][0] = CLOSED
            rooms[destination].exits[(dir_index + 2) % 4][0] = CLOSED
            print("You unlock the door.")

        elif exit_status == CLOSED or exit_status == OPEN:
            print("The door is already unlocked.")

        else:
            print("You try to unlock the imaginary door.")


def get_room_identifier(rooms, room_object):
    """
    This is a utility function, not a method!
    It returns a room ID.
    """

    for room_id, room in rooms.items():
        if room == room_object:
            return room_id
    return None