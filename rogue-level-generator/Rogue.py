import random
import time

from collections import deque           # double-ended queue
from dataclasses import dataclass
from typing import Tuple                # for the dataclass type definitions

from settings import *


def namespace(cls):
    """
    I define this simply to have a "namespace" decorator to explain the current "class Door".
    """

    return cls


# @dataclass automatically generates the __init__ function and indicates a class that mostly stores data-
@dataclass
class Room:
    """
    Represents one single room with x,y coordinates for top left corner, width and height, and an ID.
    """

    x: int
    y: int
    width: int
    height: int
    id: int
    visible: bool = False

    @property       # this generates a pseudo-attribute room.center instead of room.center()
    def center(self):
        """
        Calculate the coordinates of a room's center tile and return them as a tuple.
        Tiles must be whole numbers, so I "//" instead "/". (Or, "int ( ... / 2 )").
        """

        return (
            self.x + self.width  // 2,
            self.y + self.height // 2
        )

    @property
    def area(self):
        """
        Calculate the area of the room.
        This is added simply because I can. I actually don't need it (at least not now).
        """

        return self.width * self.height

    def intersects(self, other, buffer=0):
        """
        Checks if this room (self) overlaps with another room (other), including a buffer zone.
        """

        return (
                self.x - buffer               < other.x + other.width  and
                self.x + self.width + buffer  > other.x                and
                self.y - buffer               < other.y + other.height and
                self.y + self.height + buffer > other.y
        )

    def contains(self, x, y):
        """
        Checks if a given position x,y is located inside the current (self) room.
        """

        return (
                self.x <= x < (self.x + self.width)  and
                self.y <= y < (self.y + self.height)
        )

    @staticmethod
    def generate_rooms():
        """
        Generates a list of non-overlapping rooms

        The function attempts to create a random number of rooms within the limit.
        The rooms are placed non-overlapping, keeping a buffer space around them.
        """

        target_room_count = random.randint(MIN_ROOMS, MAX_ROOMS)

        rooms        =   []
        attempts     =    0         # defining this here means MAX_ATTEMPTS attempts for the complete generation process
        room_id      =    0

        while len(rooms) < target_room_count and attempts <= MAX_ATTEMPTS:
            attempts += 1           # instead, "attempts = 0" defined here would give MAX_ATTEMPTS for each room generation

            # I first pick the size of the room and then find a preliminary position in the map.
            # Theoretically, this order could be reversed (find a position, then choose a suitable size).
            width  = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)   # first, pick room size
            height = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)

            x = random.randint(1, LEVEL_WIDTH  - width - 1)       # then, choose room position
            y = random.randint(1, LEVEL_HEIGHT - height - 1)

            # Now, create the room as an instance of the Room class and check for overlap.
            # If it fits, add the room to the level layout. If not, proceed with a new attempt.
            new_room = Room(x, y, width, height, room_id)
            if any(new_room.intersects(other, ROOM_BUFFER) for other in rooms):
                if DEBUG_MODE["room_generation"]:
                    print(f"Room {room_id} overlaps with another room.")
                continue
            if DEBUG_MODE["room_generation"]:
                print(f"Room {room_id} created at attempt {attempts}. {MAX_ATTEMPTS - attempts} attempts left.")
            rooms.append(new_room)
            room_id += 1

        return rooms

    @staticmethod
    def draw_room_on_map(room, dungeon_map):
        """
        "Draws" (stores as ASCII characters) a room on the dungeon level map.
        At this point, rooms consist of H_WALLs and V_WALLs plus FLOOR_TILEs, but no doors.
        """

        for x in range(room.x, room.x + room.width):                # draw H_WALLs in the first and last line
            dungeon_map[room.y][x] = H_WALL                         # as top and bottom boundaries
            dungeon_map[room.y + room.height - 1][x] = H_WALL

        for y in range(room.y + 1, room.y + room.height - 1):       # between the first and last line,
            dungeon_map[y][room.x] = V_WALL                         # draw V_WALLs as left and right boundaries
            dungeon_map[y][room.x + room.width - 1] = V_WALL

        for y in range(room.y + 1, room.y + room.height - 1):       # fill everything inbetween with FLOOR_TILEs
            for x in range(room.x + 1, room.x + room.width - 1):
                dungeon_map[y][x] = FLOOR_TILE


@namespace
class Door:
    """
    This is merely a stub. But doors could be visible or invisible, open or locked, and in that case, creating Door
    objects might be cool for future enhancements. Right now, this is not a class, but simply a namespace. Maybe not a
    good idea.
    """

    @staticmethod
    def choose_door(room, other_room):
        """
        Find a suitable position for a door on the wall of room, based on the location of other_room.

        Placement rules are:
        1. Doors may not be placed in the four corner tiles of a room's walls
           as such doors would not be reachable by the player character.
        2. If the other_room's center is predominantly to the left or right of room's center,
           the door will be placed on the corresponding vertical (left or right) side wall.
        3. If the other_room's center is predominantly above or below room's center,
           the door will be placed on the corresponding horizontal (top or bottom) wall.
        """

        rcx, rcy = room.center                    # find the room centers (via @property definition)
        ocx, ocy = other_room.center

        if abs(ocx - rcx) > abs(ocy - rcy):       # horizontal distance exceeds vertical distance
            if ocx > rcx:                         # -> create door within left wall
                door_x = room.x + room.width - 1
                door_y = random.randint(room.y + 1, room.y + room.height - 2)
            else:                                 # -> create door within right wall
                door_x = room.x
                door_y = random.randint(room.y + 1, room.y + room.height - 2)

        else:                                     # vertical distance exceeds horizontal distance
            if ocy > rcy:                         # -> create door within top wall
                door_y = room.y + room.height - 1
                door_x = random.randint(room.x + 1, room.x + room.width - 2)
            else:                                 # -> create door within bottom wall
                door_y = room.y
                door_x = random.randint(room.x + 1, room.x + room.width - 2)

        return door_x, door_y


@dataclass
class Corridor:
    """
    Represents a corridor connecting two rooms.

    room1, room2: two rooms to be connected
    door1, door2: coordinates of the doors in room1 and room2
    path        : path of the corridor: list of x,y tuples.
    """

    room1: "Room"           # temporary content: the correct Room classes will be filled in later
    room2: "Room"
    door1: Tuple[int, int]
    door2: Tuple[int, int]
    path : Tuple[Tuple[int, int]]

    @staticmethod
    def connect_rooms_by_mst(rooms):
        """
        Connect all rooms using a Minimum Spanning Tree (MST) algorithm.
        Some literature about the algorithm is mentioned at the beginning of this code, and I stole the basic
        implementation from there. ;)

        The function operates with a graph representation of the dungeon map.
        Rooms represent nodes, and
        edges represent possible connections.

        They are measured by Manhattan distances (https://en.wikipedia.org/wiki/Taxicab_geometry):
        dist = abs(x1 - x2) + abs(y1 - y2)

        Each end point of the corridor is connected to the room via a door in the wall.

        The algorithm proceeds iteratively by selecting the closest unconnected room to an already connected room
        in order to make sure that all rooms will finally belong to a connected system.
        """

        connected      = [rooms[0]]     # start with room 0,
        not_connected  = rooms[1:]      # mark all other rooms unconnected,
        corridor_edges = []             # and prepare an empty list for the corridors.

        while not_connected:
            best_distance, best_pair = None, None

            for room_a in connected:            # we are looking for short connections from rooms in the connected list
                for room_b in not_connected:    # to rooms in the not_connected list
                    dx = abs(room_a.center[0] - room_b.center[0])       # Manhattan distance (see below for explanation)
                    dy = abs(room_a.center[1] - room_b.center[1])
                    dist = dx + dy

                    if best_distance is None or dist < best_distance:   # if this is the best target room, remember it
                        best_distance = dist
                        best_pair = (room_a, room_b)

            room_a, room_b = best_pair                                  # unpack the result
            door_a = Door.choose_door(room_a, room_b)                   # find door coordinates
            door_b = Door.choose_door(room_b, room_a)

            corridor_edges.append((room_a, room_b, door_a, door_b))     # remember the corridor and
            connected.append(room_b)                                    # update the connected and not_connected lists
            not_connected.remove(room_b)

        return corridor_edges

    @staticmethod
    def get_corridor_candidate_path(door1, door2, order="hv"):
        """
        Build an L-shaped path between door1 and door2.

        The path consists of a horizontal and a vertical segments in principle,
        although either of them may have a length of 0.

        The order parameter switches between two modes:
        - "hv" mode goes horizontal first, then vertical,
        - "vh" mode (de facto, everything except "hv") goes vertical first, then horizontal.
        """

        corridor_path = []  # prepare the path and unpack start and target coordinates
        x1, y1 = door1
        x2, y2 = door2

        if order == "hv":                               # hv mode
            if x1 <= x2:                                # -> h part -> left to right
                for x in range(x1, x2 + 1):
                    corridor_path.append((x, y1))
            else:                                       # -> right to left
                for x in range(x1, x2 - 1, -1):
                    corridor_path.append((x, y1))

            if y1 <= y2:                                # -> v part -> down
                for y in range(y1 + 1, y2 + 1):
                    corridor_path.append((x2, y))
            else:                                       # -> up
                for y in range(y1 - 1, y2 - 1, -1):
                    corridor_path.append((x2, y))

        else:                                           # vh mode
            if y1 <= y2:                                # -> v part -> down
                for y in range(y1, y2 + 1):
                    corridor_path.append((x1, y))
            else:                                       # -> up
                for y in range(y1, y2 - 1, -1):
                    corridor_path.append((x1, y))

            if x1 <= x2:                                # -> h part -> left to right
                for x in range(x1 + 1, x2 + 1):
                    corridor_path.append((x, y2))
            else:                                       # -> right to left
                for x in range(x1 - 1, x2 - 1, -1):
                    corridor_path.append((x, y2))

        return corridor_path

    @staticmethod
    def is_valid_corridor(corridor_path, all_rooms):
        """
        Check if a corridor is valid: Corridors may not run through rooms (neither walls nor floor tiles),
        except at the two doors at the start and end points.

        Function iterates all coordinates in the path except the first and last (the doors)
        and checks for intersections with walls or floor tiles.
        """

        for index, (x, y) in enumerate(corridor_path):
            if index == 0 or index == len(corridor_path) - 1:   # skip the doors
                continue

            for room in all_rooms:              # a faster alternative would be looking at the map and excluding
                if room.contains(x, y):         # fields other than ROCK und CORRIDOR
                    return False

        return True

    @staticmethod
    def bfs_path(door1, door2, room1, room2, all_rooms):
        """
        This is the complicated part: The function uses a Breadth-First Search (BFS) algorithm
        to find a valid path between two doors while avoiding room interiors.

        If no valid L-shaped corridor can be created via Corridor.get_corridor_candidate_path,
        this function will be called instead to attempt to find an alternative path using BFS.

        I mixed an old C code I wrote with a clean implementation of the algorithm (reference see above).

        BFS implementation, cf. literature given above from which I have stolen the fundamentals ;) :
        - Collect all room interior coordinates as "obstacles", excluding the door positions of room1 and room2.
        - Uses a double-ended queue (or deque) to explore paths and find the shortest possible path.
        - Expand in all four directions while neither revisiting nodes nor entering obstacles.
        - Each node stores its full path history so it can be reconstructed when reaching door2.
          Maybe this high memory usage is the reason that the algorithm was not used in some 1980s rogue(like) games?
        - However, BFS guarantees that the first time door2 is reached, this is already the shortest possible route.

        The algorithm explores all possible paths. As above, paths that cross room interiors are considered invalid.
        """

        obstacles = set()

        for room in all_rooms:                      # collect all room positions in a set
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    # Allow door positions in room1 and room2
                    if (room == room1 or room == room2) and ((x, y) == door1 or (x, y) == door2):
                        continue
                    obstacles.add((x, y))

        queue = deque()                             # init BFS queue
        queue.append((door1, [door1]))              # start BFS from door1: push coordinates and list of path to queue
        visited = {door1}                           # initialize a set of visited nodes with door1 coordinates

        while queue:
            (x, y), path = queue.popleft()          # pop the next node to process from the queue's left side
            if (x, y) == door2:                     # check: target reached? if yes, return successfully
                return path

            # Investigate the four neighbors to the current position: left, right, down and up
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx, ny = x + dx, y + dy             # new x and y coordinates
                # Check if new coordinates are (1) within the level boundaries,
                #                              (2) have not yet been visited, and
                #                              (3) are no obstacle fields (eg, parts of any rooms)
                if (0 <= nx < LEVEL_WIDTH and 0 <= ny < LEVEL_HEIGHT and
                        (nx, ny) not in visited and (nx, ny) not in obstacles):
                    # If all this is true, then add the new field to the set of visited coordinates,
                    # then push new coordinates and the updated path to the queue
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))

        return None                                 # no chance building this path

    @staticmethod
    def get_corridor_path(door1, door2, room1, room2, all_rooms):
        """
        This is the path construction function. It does nothing by itself. :)

        First,         it tries to find a valid L-shaped corridor path between door1 and door2 via
                       get_corridor_candidate_path in "hv" mode. If this succeeds, the corridor is returned.
        Alternatively, it tries to find a valid L-shaped corridor path between door1 and door2 via the same function,
                       but in "vh" mode. If this succeeds, the corridor is returned.
        Finally,       it tries to find a corridor path between door1 and door2 via BFS. If this succeeds, the BFS corridor
                       is returned.

        If nothing works, None is returned. (I thought about returning the hv_corridor instead to have at least something,
        but returning a bad corridor makes no sense.)
        """

        hv_corridor = Corridor.get_corridor_candidate_path(door1, door2, order="hv")
        if Corridor.is_valid_corridor(hv_corridor, all_rooms):
            if DEBUG_MODE["corridor_generation"]:
                print(f"!! I just built a HV mode corridor between {door1} and {door2}!")
            return hv_corridor

        fallback = Corridor.get_corridor_candidate_path(door1, door2, order="vh")
        if Corridor.is_valid_corridor(fallback, all_rooms):
            if DEBUG_MODE["corridor_generation"]:
                print(f"!! I just built a VH mode corridor between {door1} and {door2}!")
            return fallback

        fallback = Corridor.bfs_path(door1, door2, room1, room2, all_rooms)
        if fallback:
            if DEBUG_MODE["corridor_generation"]:
                print(f"!! I just built a BFS corridor between {door1} and {door2}!")
            return fallback

        return None

    @staticmethod
    def add_extra_corridors(rooms, existing_connections, dungeon_map):
        """
        This is where I officially went nuts: This function tries to add even more corridors between nearby rooms
        in order to create more labyrinth-like dungeon maps. The probability of adding extra corridors is randomized,
        because why not? ;)

        How it works:
        - Iterate all possible room pairs.
        - Skip pairs that are already connected.
        - Skip pairs that are far apart (Manhattan distance > 25, see above).
        - With a probability of 25%, attempt to create an extra connection:
          - Determine door locations for both rooms.
          - Use Corridor.get_corridor_path() in hv mode to find a corridor.
          - If path is valid, update map, and store the corridor.
          - To be thorough, I try vh mode next, and finally BFS.
        """

        extra_corridors = []

        for i in range(len(rooms)):                                     # iterate all room pairs
            for j in range(i + 1, len(rooms)):
                room_a = rooms[i]
                room_b = rooms[j]
                # This is a frozenset instead of a set so I can add it to a set.
                # Otherwise, I get a "TypeError: unhashable type: 'set'". I had to look this up. :)
                connection_key = frozenset({room_a.id, room_b.id})
                if connection_key in existing_connections:              # are the rooms already connected?
                    continue

                dx = abs(room_a.center[0] - room_b.center[0])           # calculate Manhattan distance
                dy = abs(room_a.center[1] - room_b.center[1])
                if dx + dy > THRESHOLD_DISTANCE_FOR_EXTRA_CORRIDORS:    # too far apart?
                    continue

                # Randomly decide to create an extra connection with 25% probability
                if random.random() < PROBABILITY_FOR_EXTRA_CORRIDOR_CREATION:  # 25% probability
                    door_a = Door.choose_door(room_a, room_b)
                    door_b = Door.choose_door(room_b, room_a)

                    path = Corridor.get_corridor_candidate_path(door_a, door_b, order="hv")      # hv mode
                    mode_used = "hv"

                    if not Corridor.is_valid_corridor(path, rooms):
                        path = Corridor.get_corridor_candidate_path(door_a, door_b, order="vh")  # vh mode
                        mode_used = "vh"

                    if not Corridor.is_valid_corridor(path, rooms):
                        path = Corridor.bfs_path(door_a, door_b, room_a, room_b, rooms)         # BFS mode
                        mode_used = "BFS"

                    if path and Corridor.is_valid_corridor(path, rooms):
                        for (x, y) in path:
                            if (x, y) == door_a or (x, y) == door_b:
                                dungeon_map[y][x] = STANDARD_DOOR
                            else:
                                dungeon_map[y][x] = CORRIDOR_TILE

                        if DEBUG_MODE["extra_corridor_generation"]:
                            print(f"## Whoa, I just built an extra corridor in {mode_used} mode between {room_a} and {room_b}!")
                        extra_corridors.append(Corridor(room_a, room_b, door_a, door_b, path))
                        existing_connections.add(connection_key)

        return extra_corridors


class Dungeon:
    def __init__(self):
        """
        Initialize an empty dungeon.
        """

        self.map       = []
        self.rooms     = []
        self.corridors = []
        self.corridor_visibility = [
            [False for _ in range(LEVEL_WIDTH)] for _ in range(LEVEL_HEIGHT)
        ]
        self.exit = None

    def generate(self):
        """
        Generate a dungeon level:
        1. initialize the map by filling it with rock tiles
        2. generate rooms
        3. connect rooms with corridors
        4. add extra corridors

        The function returns all info about the dungeon, namely:
        1. 2D grid of the level layout
        2. [rooms]
        3. [corridors]
        """

        self.map = self.let_there_be_rock()                     # create the abyss using both AC & DC

        self.rooms = Room.generate_rooms()                      # carve rooms into the foundations of the earth
        for room in self.rooms:
            Room.draw_room_on_map(room, self.map)               # ask Elrond for a map

        exit_room = random.choice(self.rooms)
        exit_x = random.randint(exit_room.x + 1, exit_room.x + exit_room.width - 2)
        exit_y = random.randint(exit_room.y + 1, exit_room.y + exit_room.height - 2)

        self.exit = (exit_x, exit_y)
        self.map[exit_y][exit_x] = EXIT_TILE

        corridor_edges = Corridor.connect_rooms_by_mst(self.rooms)  # let the dwarves dig the corridors
        self.corridors = []
        existing_connections = set()

        for room_a, room_b, door_a, door_b in corridor_edges:
            path = Corridor.get_corridor_path(door_a, door_b, room_a, room_b, self.rooms)

            self.corridors.append(
                Corridor(room_a, room_b, door_a, door_b, path)
            )

            for (x, y) in path:
                self.map[y][x] = CORRIDOR_TILE                  # mark corridor on the map using moon runes

            self.map[door_a[1]][door_a[0]] = STANDARD_DOOR      # mark doors with Ithildin letters
            self.map[door_b[1]][door_b[0]] = STANDARD_DOOR

            existing_connections.add(
                frozenset({room_a.id, room_b.id})               # as above, avoid a "TypeError: unhashable type: 'set'"
            )

        # Add extra corridors, but don't dig to deep and beware of Balrogs!
        extra_corridors = Corridor.add_extra_corridors(self.rooms, existing_connections, self.map)
        self.corridors.extend(extra_corridors)

        self.corridor_visibility = [[False for _ in range(LEVEL_WIDTH)] for _ in range(LEVEL_HEIGHT)]

    @staticmethod
    def let_there_be_rock():
        """
        🪨🤘🎸. (Sorry.)
        """

        return [[ROCK_TILE for _ in range(LEVEL_WIDTH)] for _ in range(LEVEL_HEIGHT)]

    def get_room_at(self, x, y):
        """
        Finds the room at given coordinates (or returns None).
        """

        for room in self.rooms:
            if room.contains(x, y):
                return room

        return None

    def is_corridor(self, x, y):
        """
        Checks if the cell at any given coordinate is part of any corridor.
        A more complicated solution would be:
        return any((x, y) in corridor.path for corridor in self.corridors)
        This might be necessary if this check would be done during the generation process. No idea if this might
        happen, I just want to remember the line. :)
        """

        return self.map[y][x] == CORRIDOR_TILE

    def print(self):
        """
        Prints the dungeon in ASCII mode. Added this just to have a print function within the Dungeon class.
        """

        Utilities.print_map(self.map)

    def update_corridor_visibility(self, player_x, player_y):
        """
        Updates the corridor visibility based on the player's current position.
        The current player position plus eight neighbor cells are revealed.
        """

        directions = [(-1, -1), ( 0, -1), ( 1, -1),     # above left, above  , above right
                      (-1,  0), ( 0,  0), ( 1,  0),     # left      , current, right
                      (-1,  1), ( 0,  1), ( 1,  1)]     # below left, below  , below right

        for dx, dy in directions:                                       # reveal adjacent doors and corridors
            nx, ny = player_x + dx, player_y + dy                       # new x and y
            if 0 <= nx < LEVEL_WIDTH and 0 <= ny < LEVEL_HEIGHT:        # within boundaries?
                if self.map[ny][nx] in (CORRIDOR_TILE, STANDARD_DOOR):  # what kind of tile?
                    self.corridor_visibility[ny][nx] = True

        player_room = self.get_room_at(player_x, player_y)              # reveal all doors from current room
        # This checks every cell in the room, which is too much. I might skip the floor tiles, but I guess
        # this will work so fast that it's not really worth changing it.
        if player_room:
            for row in range(player_room.y, player_room.y + player_room.height):
                for column in range(player_room.x, player_room.x + player_room.width):
                    if self.map[row][column] == STANDARD_DOOR:
                        self.corridor_visibility[row][column] = True


class Utilities:
    @staticmethod
    def print_map(dungeon_map):
        """
        Actually print the ASCII map.
        """

        print("\n".join("".join(row) for row in dungeon_map))

    @staticmethod
    def test_mode():
        """
        This runs a large number of test levels to find out whether the code crashes or not.
        It also measures running time.
        """

        total_time = 0.0
        shortest, longest = float("inf"), 0.0  # float("inf") is infinite time

        print(f"Creating {TEST_NUM} test levels...\n")

        for i in range(TEST_NUM):
            start_time = time.time()
            dungeon = Dungeon()
            dungeon.generate()
            elapsed = (time.time() - start_time) * 1000

            total_time += elapsed
            shortest, longest = min(shortest, elapsed), max(longest, elapsed)

            print(f"Generated level {i + 1:4d} in {elapsed:6.2f} ms.")

        print("\nTest completed.")
        print(f"Average time per level  {total_time / TEST_NUM:6.2f} ms.")
        print(f"Shortest level creation {shortest:6.2f} ms.")
        print(f"Longest level creation  {longest:6.2f} ms.")

    @staticmethod
    def display_loop():
        """
        This is the test loop, generating and displaying levels.
        """

        while True:
            dungeon = Dungeon()
            dungeon.generate()

            if OUTPUT_MODE["ascii"]:
                dungeon.print()

            if OUTPUT_MODE["graphics"]:
                graphics = DungeonVisualizer(dungeon)
                graphics.generate()

            if AUTO_GEN:
                time.sleep(DELAY)
            else:
                if input("Press Enter to continue... "):
                    break

    @staticmethod
    def game_loop():
        """
        Actual gameplay. Woohoo.

        It was complicated coding the keyboard input (with key repeats), and I had to look up some strategies for that.
        """

        dungeon = Dungeon()
        dungeon.generate()
        player = Player.initialize(dungeon, "random")
        visualizer = DungeonVisualizer(dungeon, player)

        pygame.init()
        clock = pygame.time.Clock()

        rounds_counter = 0

        # This keeps track of the four directions (arrow keys and WASD)
        key_states = {
            "up"   : {"active": False, "first_press": 0, "last_move": 0},       # flag, timestamp, timestamp
            "down" : {"active": False, "first_press": 0, "last_move": 0},
            "left" : {"active": False, "first_press": 0, "last_move": 0},
            "right": {"active": False, "first_press": 0, "last_move": 0}
        }

        running = True

        caption = f"Dungeon Level -- Rounds: {rounds_counter:4} -- "
        caption += f"Current Position: {player.x:3}/{player.y:3}"
        pygame.display.set_caption(caption)

        while running:
            current_time = pygame.time.get_ticks()

            moved, waited = False, False

            for event in pygame.event.get():                # user closes window
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.unicode == ">" \
                        and dungeon.map[player.y][player.x] == EXIT_TILE:       # user stands on ladder and leaves
                    return

            keys = pygame.key.get_pressed()                 # get dict about currently pressed keys

            if keys[pygame.K_q] or keys[pygame.K_ESCAPE]:   # leave when q or ESC are pressed
                running = False

            # there's still an issue here; PERIOD should have a cooldown effect like arrow keys
            # too lazy to do this right now
            if keys[pygame.K_PERIOD]:
                waited = True

            for direction, key_list in KNOWN_KEYS.items():
                if any(keys[key] for key in key_list):  # check if any of the keys in key_list is pressed
                    if not key_states[direction]["active"]:                             # first press, move immediately
                        moved = player.move(direction, dungeon)                         # moved is a True/False flag

                        key_states[direction]["active"] = True                          # set key active
                        key_states[direction]["first_press"] = current_time             # remember timestamp

                    else:                                                               # key held down
                        elapsed = current_time - key_states[direction]["first_press"]   # check time
                        if elapsed > INITIAL_DELAY:                                     # waited long enough?
                            if (current_time - key_states[direction]["last_move"]) > REPEAT_INTERVAL:   # really?
                                moved = player.move(direction, dungeon)
                                key_states[direction]["last_move"] = current_time

                else:
                    key_states[direction]["active"] = False                             # clear flags


            visualizer.draw()
            pygame.display.flip()

            if moved or waited:
                rounds_counter += 1
                pygame.display.set_caption(f"Dungeon Level -- Rounds: {rounds_counter:4} -- Current Position: {player.x:3}/{player.y:3}")

            clock.tick(60)                                                              # cap at 60 FPS

        pygame.quit()


class DungeonVisualizer:
    """
    My first experiment with pygame :)
    """

    def __init__(self, dungeon, player=None):
        """
        Initialize data.
        """

        self.dungeon = dungeon
        self.player  = player
        self.width   = LEVEL_WIDTH  * TILE_SIZE     # width and height in pixels
        self.height  = LEVEL_HEIGHT * TILE_SIZE
        self.screen  = pygame.display.set_mode(
            (self.width, self.height),
            pygame.RESIZABLE                        # flags go here, eg. pygame.FULLSCREEN
        )

        pygame.init()
        pygame.display.set_caption("Dungeon Level") # window heading

    def draw(self):
        """
        Draws the dungeon using pygame, including a totally basic "fog of war"-like visibility system.
        """

        self.screen.fill(COLOR_BACKGROUND)

        for room in self.dungeon.rooms:                                 # 1., draw the room floors
            if room.visible:
                for row in range(room.y, room.y + room.height):
                    for column in range(room.x, room.x + room.width):
                        current_room = pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)   # x,y, w,h
                        pygame.draw.rect(self.screen, COLOR_FLOOR, current_room)    # screen/window, color, element

        for corridor in self.dungeon.corridors:                         # 2., draw the corridors
            for (x, y) in corridor.path:
                if self.dungeon.corridor_visibility[y][x]:              # draw only if visible, skip if not
                    rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, COLOR_CORRIDOR, rect)

        for room in self.dungeon.rooms:                                 # 3., draw the room walls
            if room.visible:
                pygame.draw.rect(self.screen, COLOR_WALL,               #     top wall
                                 pygame.Rect(room.x * TILE_SIZE, room.y * TILE_SIZE, room.width * TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, COLOR_WALL,               #     bottom wall
                                 pygame.Rect(room.x * TILE_SIZE, (room.y + room.height - 1) * TILE_SIZE,
                                             room.width * TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(self.screen, COLOR_WALL,               #     left wall
                                 pygame.Rect(room.x * TILE_SIZE, room.y * TILE_SIZE, TILE_SIZE, room.height * TILE_SIZE))
                pygame.draw.rect(self.screen, COLOR_WALL,               #     right wall
                                 pygame.Rect((room.x + room.width - 1) * TILE_SIZE, room.y * TILE_SIZE, TILE_SIZE,
                                             room.height * TILE_SIZE))

        for row in range(LEVEL_HEIGHT):                                 # 4., draw the doors
            for column in range(LEVEL_WIDTH):
                if self.dungeon.map[row][column] == STANDARD_DOOR and self.dungeon.corridor_visibility[row][column]:
                    rect = pygame.Rect(column * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, COLOR_DOOR, rect)

        if self.dungeon.exit:                                           # check if an exit has been generated
            x, y = self.dungeon.exit                                    # get coordinates
            exit_room = self.dungeon.get_room_at(x, y)                  # get room ID

            if exit_room and exit_room.visible:                         # draw if the room is visible
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.screen, EXIT_COLOR, rect)

        if self.player:                                                 # draw the player
            rect = pygame.Rect(self.player.x * TILE_SIZE, self.player.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, PLAYER_COLOR, rect)

    def generate(self):
        """
        Runs the pygame loop to display the dungeon.
        I found the main loop here: https://pygame.readthedocs.io/en/latest/1_intro/intro.html
        """

        running = True

        while running:
            for event in pygame.event.get():        # ask for events list
                if event.type == pygame.QUIT:       # window closed?
                    running = False
                    break

            self.draw()                             # calculate new map graphics
            pygame.display.flip()                   # display new map graphics

        pygame.quit()


class Player:
    """
    This section contains a simple logic for the Player character.
    """

    def __init__(self, x: int, y: int):
        """
        Right now, all the character has is a position. There might be XP, RPG values, states (hungry, weak, fainted),
        and inventory, and whatever-
        """

        self.x = x
        self.y = y

    @classmethod
    def initialize(cls, dungeon, mode="auto"):
        """
        Create a player and position them somewhere in the dungeon.
        """

        if not dungeon.rooms:               # this should never happen
            raise ValueError("Cannot place player. Dungeon has no rooms!")

        if mode == "auto":                  # place in the center of the first room
            room = dungeon.rooms[0]
            x, y = room.center

        elif mode == "random":              # place at a random position in a random room
            room = random.choice(dungeon.rooms)
            x = random.randint(room.x + 1, room.x + room.width - 2)
            y = random.randint(room.y + 1, room.y + room.height - 2)

        else:                               # this should never happen
            raise ValueError(f"Invalid placement mode: {mode}")

        player = cls(x, y)                  # place player in the room
        player.reveal_room(dungeon)         # mark room as visible
        dungeon.update_corridor_visibility(player.x, player.y)  # I need this to mark the doors visible as well

        return player

    def move(self, direction, dungeon):
        """
        Move the player in the specified direction if valid, keep track if movement was possible
        """

        if not direction:                   # should never happen
            return False

        new_x, new_y = self.x, self.y

        match direction[0].lower():
            case "u": new_y -= 1
            case "d": new_y += 1
            case "l": new_x -= 1
            case "r": new_x += 1

        if self.is_valid_position(new_x, new_y, dungeon):           # at this point, this should always be True
            self.x, self.y = new_x, new_y
            self.reveal_room(dungeon)                               # update room visibility
            dungeon.update_corridor_visibility(self.x, self.y)      # update corridor visibility
            return True

        else:
            return False

    def is_valid_position(self, x: int, y: int, dungeon) -> bool:
        """
        Check if position is within bounds and walkable
        """

        return (
                0 <= x < LEVEL_WIDTH  and
                0 <= y < LEVEL_HEIGHT and
                dungeon.map[y][x] in (FLOOR_TILE, CORRIDOR_TILE, STANDARD_DOOR, EXIT_TILE)
        )

    def reveal_room(self, dungeon):
        """
        Reveal room when the player has moved in
        """

        for room in dungeon.rooms:
            if room.contains(self.x, self.y):           # maybe not the most elegant way to check
                room.visible = True


def main():
    print("Welcome to the Dungeons of Doom!\n\n")

    if RUNNING_MODE["brute_force"]:
        Utilities.test_mode()
    elif RUNNING_MODE["level_gen"]:
        Utilities.display_loop()
    elif RUNNING_MODE["play"]:
        Utilities.game_loop()
        print("\n\nYou survived the bridge of Khazad-dûm and escaped the dungeon.")

if __name__ == "__main__":
    main()