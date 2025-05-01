import random

from definitions import *
from item        import *
from utilities   import article, debug_move


class Player:
    """
    This class initializes and controls the player character.
    """

    def __init__(self, name="Protagonist"):
        """
        All info about the player character.
        """

        self.items = []                     # items in inventory
        self.current_room = "BEDROOM"

        # All of the following is not really in use
        self.name = name                    # name of the player
        self.gender = " "                   # m / f / o
        self.health = {                     # this could be a collection of flags for status effects
            "poisoned": False,
            "drunk"   : False,
            "wounded" : False
        }
        self.level = 1                      # in case there would be a level-up system
        self.experience = 0                 # XP
        self.next_level_xp = 100            # XP threshold for next level
        self.skills = {                     # collection of status points, taken from D&D (not in use here)
            "STR": 10,                      # strength
            "DEX": 10,                      # dexterity
            "CON": 10,                      # constitution
            "INT": 10,                      # intelligence
            "WIS": 10,                      # wisdom
            "CHA": 10                       # charisma
        }                                   # further values might be added to turn this into an RPG/Adventure

    def go_berserk(self):
        """
        Print something when player acts violently.
        """

        if random.choice([True, False]):
            print("You go berserk and start smashing everything in sight! It's surprisingly therapeutic.")
        else:
            print("You hop around, waving your arms awkwardly. Maybe violence is not an option.")

    def gain_xp(self, xp):
        """
        Increase XP
        """

        if not xp or type(xp) != int:
            return

        self.experience += xp
        while self.experience >= self.next_level_xp:
            self.level_up()

    def level_up(self):
        """
        Increase level and update threshold to following level.
        Thresholds might also be pre-defined and hard-coded.
        """

        self.level += 1
        self.next_level_xp *= 1.5
        print(f"You reached level {self.level}.")

    def move(self, direction, in_maze, rooms):
        """
        Move player character from one room to another.
        """

        if not direction:
            direction = input("Where do you want to go? ").strip().lower()

        direction_map = {"n": NORTH, "north": NORTH, "w": WEST, "west": WEST, "s": SOUTH, "south": SOUTH, "e": EAST, "east": EAST}
        direction = direction_map.get(direction)

        if direction is None:                           # no valid direction => no movement
            print("Invalid direction.")
            return self.current_room

        if in_maze:                                     # in the labyrinth, player directions are overwritten,
            direction = random.randint(1,3)             # excluding N (0) which would lead the player out

        exit_status, new_room = rooms[self.current_room].exits[direction]

        if exit_status == OPEN or exit_status == CLOSED:
            if exit_status == CLOSED:
                print("You go through the door, opening it first.")
                rooms[self.current_room].exits[direction][0] = OPEN
                opposite_direction = (direction + 2) % 4
                rooms[new_room].exits[opposite_direction][0] = OPEN
            self.current_room = new_room

        elif exit_status == LOCKED:                     # alternative: automatically unlock doors if player
            print("The door is locked.")                # has the key in their inventory

        else:                                           # no exit in this direction
            if not in_maze:
                print("With a hollow ring, you bang your head at the wall.")
            else:
                print("You helplessly stumble around.")
        return self.current_room

    def perform(self):
        """
        Choose random feedback about performance (sing, play, ...)
        """

        if random.choice([True, False]):
            print("You deliver a smashing performance. What a pity nobody has witnessed it!")
        else:
            print("You embarrass yourself. You fear the neighbours might have noticed.")

    def say(self, string):
        """
        Say something (this is not the "talk to NPC" function!)
        """

        if not string:
            print("You flawlessly say nothing.")
            return

        if string.lower() == "xyzzy":
            print("A hollow voice says 'FOOL.'")                # that's a quote from "Zork" :)

        else:
            print(f"'{string.title()}.' - You feel better having said that.")

    def show_inventory(self):
        """
        Display character inventory.
        """

        if not self.items:
            print("You do not carry anything with you at the moment.")

        else:
            inventory_contents = "Contents of your personal inventory: "
            inventory_contents += ", ".join([f"{article(item.name)} {item.name}" for item in self.items])
            print(inventory_contents + ".")

    def show_stats(self):
        """
        Display statistics about player.
        """

        print(f"{self.name} is currently on level {self.level}. You have {self.experience} XP. Next level up at {self.next_level_xp} XP.")

        if True in self.health.values():
            print("Health status: ", end="")
            for k, v in self.health.items():
                if v:
                    print(f"{k}. ", end="")
            print()

        for k, v in self.skills.items():
            print(f"{k}: {v}  ", end="")
        print()
        
    def talk_to_npc(self, npc_name, npcs, topic=None):
        """
        Talk to an NPC.
        """

        current_room = self.current_room
        if not npc_name:
            npc_name = input("Who do you want to talk to? ").strip().lower()

            if not npc_name:
                return

        npc_name_lower = npc_name.lower()
        npcs_lower = {
            name.lower(): npc for name, npc in npcs.items()
        }

        npc_found = False
        if npc_name_lower in npcs_lower:
            npc = npcs_lower[npc_name_lower]
            if npc.location == current_room:
                npc_found = npc

        if not npc_found:
            for npc in npcs.values():
                if npc.name.lower() == npc_name_lower and npc.location == current_room:
                    npc_found = npc
                    break

        if npc_found:
            npc_found.talk(topic)                           # actual talking is done by NPC class

        else:
            print(f"{npc_name.title()} is not here.")