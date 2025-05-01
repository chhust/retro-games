import random

from definitions import *
from room        import get_room_identifier
from utilities   import article


class NPC:
    """
    This class contains data and methods to handle static NPCs.
    It is also the parent class for dynamic NPCs.
    """

    def __init__(self, name, description, dialogue, location):
        """
        Init function
        """

        self.name = name
        self.description = description
        self.dialogue = dialogue            # dictionary of dialogue options
        self.location = location            # room where NPC is located

        # NPCs could have personal inventories, health flags, ..., just as the player character
        # self.items = []

    def describe(self):
        """
        Show info about an NPC.
        """

        print(self.description)

    def talk(self, topic=None):
        """
        Talk to an NPC.
        """

        if not topic:
            topic = input(f"What do you want to talk to {self.name} about? ").strip().lower()

        # If no topic is given, one of the default lines is chosen.
        if not topic:
            print(f"\'{random.choice(self.dialogue['default'])},\' says {self.name}.")
            return

        if topic in self.dialogue:
            print(f"{self.name.title()} says: '{self.dialogue[topic]}'")
        else:
            print(f"{self.name.title()} doesn't know anything about that.")


class DynamicNPC(NPC):
    """
    Dynamic NPCs inherit from static NPCs and add move logic.
    """

    def __init__(self, name, description, dialogue, location):
        """
        Init function
        """

        super().__init__(name, description, dialogue, location)

    def move(self, current_room, rooms):
        """
        This will move the dynamic NPC.
        They will accidentally look for an open or closed (but unlocked) door
        and go through it.
        """

        current_room_of_npc = rooms[self.location]
        possible_exits = []

        for index, (door_status, room_key) in enumerate(current_room_of_npc.exits):
            if room_key and door_status != LOCKED:
                possible_exits.append((door_status, room_key, MAIN_DIRECTIONS[index]))

        if not possible_exits:                          # no movement possible
            return

        door_status, next_room_key, direction = random.choice(possible_exits)
        next_room = rooms[next_room_key]

        if door_status == CLOSED:                       # NPCs can pass open (but not locked) doors
            for exit in current_room_of_npc.exits:
                if exit[1] == next_room_key:
                    exit[0] = OPEN

            for exit in next_room.exits:
                if exit[1] == current_room:
                    exit[0] = OPEN

        npc_nr_name = get_room_identifier(rooms, next_room)
        npc_cr_name = get_room_identifier(rooms, current_room_of_npc)

        if npc_nr_name == current_room:
            opposite_directions = {
                "N": "south",
                "W": "east",
                "S": "north",
                "E": "west"
            }
            print(f"{self.name} enters the room from the {opposite_directions[direction]}.")

        if npc_cr_name == current_room:
            full_directions = {
                "N": "north",
                "W": "west",
                "S": "south",
                "E": "east"
            }
            print(f"{self.name} leaves the room to the {full_directions[direction]}.")

        self.location = next_room_key                   # Finally, move the location,
        current_room_of_npc.remove_npc(self)            # delete NPC from old room,
        next_room.add_npc(self)                         # and add them to the new room