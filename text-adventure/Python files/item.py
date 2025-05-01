from utilities import article


class Item:
    """
    This class holds the information to define an item.
    """

    def __init__(self, name, descriptor, item_type, synonyms, is_movable=True, is_visible=True, is_poisonous=False, is_healing=False):
        self.name = name
        self.descriptor = descriptor
        self.item_type = item_type
        self.synonyms = synonyms
        self.is_movable = is_movable
        self.is_visible = is_visible
        self.is_poisonous = is_poisonous
        self.is_healing = is_healing


class ItemManager:
    """
    This class holds methods to manipulate items.
    """

    def add_item(self, container, item):
        """
        Add an item to a container.
        Containers can be rooms and inventories.
        """

        if container and item:
            container.items.append(item)

    def combine_items(self, player, rooms, items, item1=None, item2=None):
        """
        Combine two existing items to create a new one.
        """

        if (not item1) and item2:               # This should never happen, just to be thorough
            item1 = item2
            item2 = None

        if not item1:
            item1 = input("Please enter first item: ").strip().lower()
            if not item1:
                return

        if not item2:
            item2 = input("Please enter second item: ").strip().lower()
            if not item2:
                return

        # Players can only manipulate items in their personal inventory.
        if self.is_item_in_inventory(item1, rooms, player) and self.is_item_in_inventory(item2, rooms, player):
            new_item, feedback = self.craft_new_item(item1, item2)

            if new_item and feedback:                           # succesful combinations give results
                print(feedback)

                # item1, item2 and new_item are strings,
                # but I need the item objects from the Item class, so I look them up:
                item1_obj    = next((item for item in player.items if item.name == item1),    None)
                item2_obj    = next((item for item in player.items if item.name == item2),    None)
                new_item_obj = next((item for item in items        if item.name == new_item), None)

                # Again, this should have worked, but I check in case the database is flawed:
                if item1_obj and item2_obj and new_item_obj:
                    player.items.remove(item1_obj)              # remove both old items from the inventory
                    player.items.remove(item2_obj)
                    player.items.append(new_item_obj)           # and add the new one
                else:
                    print("An error occurred in the game logic.")

            else:                                               # no combination of these items possible
                print("You cannot combine these items.")

        else:                                                   # at least one item is not in the inventory
            print("You do not have this with you.")

    def craft_new_item (self, ingredient1, ingredient2):
        """
        Look up combinations.
        In a real game, the combined_items dictionary (k and v are both tuples)
        would better be stored in an external file.
        """

        combined_items = {
            ("broom" , "towel") : ("flag", "You attach the towel to the broomstick. You now have a flag."),
            ("potion", "powder"): ("gum",  "After some puffs of smoke emerged and dissipated, you created a strip of chewing gum.")
        }

        # Sorting makes this independent of the order of items
        result = combined_items.get(tuple(sorted([ingredient1, ingredient2])))
        return result if result else (None, None)

    def drop_item(self, current_room, item, rooms, player):
        """
        Move an item from the personal inventory to a room inventory.
        """

        if len(player.items) == 0:
            print("You do not have anything with you.")
            return

        if not item:
            item = input("What do you want to drop? ").strip().lower()

            if not item:
                return

        if item == "all":                                   # otherwise, this should be a for loop
            print("Don't be silly.")
            return

        if not self.is_item_in_game(item, rooms, player):
            print("I do not know what you are talking about.")
            return

        item_obj = self.find_item(item, [player.items])     # find actual item object
        room_obj = rooms[current_room]                      # get actual room object

        if not item_obj:
            print(f"You do not have {article(item)} {item}.")

        else:
            print(f"You have dropped the {item_obj.name}.")
            self.move_item(player, room_obj, item_obj)      # finally, move item position

    def examine_item(self, item_name, current_room, rooms, player, npcs):
        """
        This function prints an item description if the item is approachable,
        i. e. either in the player inventory or in the current room.
        If no fitting item is found, NPCs in the current room are searched,
        and their description is shown.
        """

        if not item_name:
            item_name = input("What do you want to examine? ").strip().lower()
            if not item_name:
                return

        if not self.is_item_in_game(item_name, rooms, player):
            room = rooms[current_room]

            # "examine" works for items and NPCs, so if it's not an item, it might be an NPC.
            # I directly check the current room's NPC list to check.
            npc = room.find_npc(item_name, npcs, current_room)
            if npc:
                npc.describe()
            else:
                print(f"Nobody has ever heard of {article(item_name)} '{item_name}.'")
            return

        item = self.is_item_approachable(item_name, current_room, rooms, player)
        if item:
            print(item.descriptor)
        else:
            print(f"I cannot see {article(item_name)} {item_name} here.")

    def find_item(self, item_name, containers):
        """
        Utility function to find an item in a list of containers.
        """

        for container in containers:
            for item in container:
                if item.name == item_name or item_name in item.synonyms:
                    return item     # maybe "return item, container" might be needed in some cases
        return None

    def get_item(self, current_room, item, rooms, player):
        """
        Contrary to drop_item, this functions moves an item from a room inventory
        to the player inventory.
        """

        if not item:
            item = input("What do you want to get? ").strip().lower()

            if not item:
                return

        if item == "all":                                       # see above at "drop_item()"
            print("Don't be greedy.")
            return

        if self.is_item_in_inventory(item, rooms, player):
            print("You already have this with you.")
            return

        if not self.is_item_in_game(item, rooms, player):
            print("I do not know what you are talking about.")
            return

        if not self.is_item_in_room(item, current_room, rooms):
            print(f"I cannot see {article(item)} {item} here.")
            return

        room_obj = rooms[current_room]                          # get actual room object
        item_obj = self.find_item(item, [room_obj.items])       # find actual item object
        if item_obj:
            if item_obj.is_movable:
                print(f"You have taken the {item_obj.name}.")
                self.move_item(room_obj, player, item_obj)      # move between inventories
            else:
                print(f"You cannot move the {item_obj.name}.")

    def is_item_approachable(self, item_name, current_room, rooms, player):
        """
        Check if an item is either in the player inventory or in the current room's inventory.
        """

        return self.find_item(item_name, [rooms[current_room].items, player.items])

    def is_item_in_game(self, item_name, rooms, player):
        """
        Check if an item is anywhere in the game's databases.
        If NPCs have inventories, they should be added here.
        """

        containers = [room.items for room in rooms.values()] + [player.items]
        return self.find_item(item_name, containers)

    def is_item_in_inventory(self, item_name, rooms, player):
        """
        Check if an item is in the player inventory.
        """

        return self.find_item(item_name, [player.items])

    def is_item_in_room(self, item_name, current_room, rooms):
        """
        Check if an item is in the current room's inventory.
        """

        return self.find_item(item_name, [rooms[current_room].items])

    def move_item(self, current_container, new_container, item):
        """
        Move an item between inventories:
        add it to one inventory and remove from the other one.
        """

        self.remove_item(current_container, item)
        self.add_item(new_container, item)

    def remove_item(self, container, item):
        """
        Remove item from a container.
        """

        container.items.remove(item)

    def eat_item(self, current_room, item, rooms, player):
        """
        This function lets player characters eat an item.
        """

        if not item:
            item = input("What do you want to eat? ").strip().lower()

            if not item:
                return

        if not self.is_item_in_game(item, rooms, player):
            print("I do not know what you are talking about.")
            return

        # find the container (either player inventory or room inventory)
        if self.is_item_in_inventory(item, rooms, player):
            container = player
        elif self.is_item_in_room(item, current_room, rooms):
            container = rooms[current_room]
        else:
            print("You do not have this with you.")
            return

        item_obj = self.find_item(item, [container.items])  # find actual item object

        if item_obj.item_type != "FOOD":
            print("You cannot eat this.")
            return

        print(f"You have eaten the {item_obj.name}. ", end="")

        if item_obj.is_poisonous:
            print("You feel very sick.")
            player.health["poisoned"] = True

        else:
            print("You feel strong again.")

        # Remove the item from the container (either the player's inventory or the room)
        self.remove_item(container, item_obj)

    def drink_item(self, current_room, item, rooms, player):
        """
        This function lets player characters drink an item.
        """

        if not item:
            item = input("What do you want to eat? ").strip().lower()

            if not item:
                return

        if not self.is_item_in_game(item, rooms, player):
            print("I do not know what you are talking about.")
            return

        # find the container (either player inventory or room inventory)
        if self.is_item_in_inventory(item, rooms, player):
            container = player
        elif self.is_item_in_room(item, current_room, rooms):
            container = rooms[current_room]
        else:
            print("You do not have this with you.")
            return

        item_obj = self.find_item(item, [container.items])  # find actual item object

        if item_obj.item_type != "DRINK":
            print("You cannot drink this.")
            return
        
        print(f"You have drunk the {item_obj.name}. ", end="")
        
        if item_obj.is_healing:
            print("You feel surprisingly healthy.")
            player.health["poisoned"] = False
            
        else:
            print("You quenched your thirst.")
            
        # Remove the item from the container (either the player's inventory or the room)
        self.remove_item(container, item_obj)
    
item_manager = ItemManager()
