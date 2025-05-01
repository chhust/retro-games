/**************************************************************************************************
 * T I N Y   T E X T   A D V E N T U R E                                                          *
 *                                                                                                *
 *        Available commands:                                                                     *
 * AC  0: QUIT      - Q, EXIT                                                                     *
 * AC  1: GO        - EXPLORE, HEAD, MOVE, NAVIGATE, PROCEED, RUN, STROLL, TRAVEL, WALK, WANDER;  *
 *                    [DIRECTIONS:] NORTH (N), WEST (W), SOUTH (S), EAST (E)                      *
 * AC  2: DANCE     - ENTERTAIN, SING                                                             *
 * AC  3: SAY       - TALK, UTTER                                                                 *
 * AC  4: WAIT                                                                                    *
 * AC  5: KILL      - DESTROY, KICK, PUNCH                                                        *
 * AC  6: GET       - ACQUIRE, ATTAIN, COLLECT, FETCH, GAIN, GRAB, OBTAIN, RECEIVE, TAKE          *
 * AC  7: INVENTORY - I                                                                           *
 * AC  8: DROP      - ABANDON, DISCARD, DISCHARGE, DITCH, LEAVE, RELEASE, RELINQUISH, THROW, TOSS *
 * AC  9: OPEN                                                                                    *
 * AC 10: CLOSE                                                                                   *
 * AC 11: UNLOCK    - UNBLOCK, UNBOLT, UNCHAIN, UNLATCH, UNSEAL                                   *
 * AC 12: LOCK      - BLOCK, BOLT, CHAIN, LATCH, SEAL, SECURE                                     *
 * AC 13: EXAMINE   - X                                                                           *
 * AC 14: BRIEF                                                                                   *
 * AC 15: VERBOSE                                                                                 *
 * AC 16: LOOK      - L                                                                           *
 *                                                                                                *
 *        What to include next:                                                                   *
 *      - more verbs and action functions: USE, GET ALL, EAT, DRINK, poisoned, HELP               *
 *      - handle "the" ("a", "an", "this", "that", "these", "those") in user input                *
 *      - "it" referring to only object or last object, "at" as in "look at something"            *
 *      - puzzles, NPCs, cut scenes                                                               *
 *      - dark rooms / light switches                                                             *
 *      - change synonyms and commands / verbs to arrays                                          *
 *      - split code into several files                                                           *
 *      - load room layout and items from file                                                    *
 *      - load and save // SCORE command // MOVES command                                         *
 **************************************************************************************************/

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>


// current scope: number of objects and number of rooms

#define NUMBER_OF_ITEMS      6
#define NUMBER_OF_ROOMS      8


// global constants

const int NONE           =   0;						// flags for door status
const int LOCKED         =   1;
const int CLOSED         =   2;
const int OPEN           =   3;

const int NORTH          =   0;						// flags for directions
const int WEST           =   1;
const int SOUTH          =   2;
const int EAST           =   3;

const int HALLWAY        =   0;						// room identifiers
const int LIVING_ROOM    =   1;
const int BATHROOM       =   2;
const int KITCHEN        =   3;
const int BEDROOM        =   4;
const int OUTSIDE        =   5;
const int PASSAGES       =   6;
const int GARDEN         =   7;

const int KEY            =   0;						// object types
const int FOOD           =   1;
const int DRINK          =   2;
const int LAMP           =   3;
const int OTHER          =   4;

const int INVENTORY      = 111;						// ID for your personal inventory


// global variables and structures

char* main_directions[4] = {"N", "W", "S", "E"};
char* exit_status[4]     = {"none", "locked", "closed", "open"};
int verbose              = 0;						// verbose flag

struct room_structure
{
	char* name;										// room name
	char* descriptor;								// one-sentence decription
	int   exits[4][2];								// exits to NWSE: [0] = status, [1] = destination
	int   visited;
} room[NUMBER_OF_ROOMS];

struct objects
{
	char*  name;									// object name
	char*  descriptor;								// one-sentence description
	int    type;									// what kind of objects (object type)
	int    location;								// current location of the object
	char   synonyms[5][20];							// item synonyms  CAN I DO THIS WITHOUT THE FIXED NUMBERS?
} item[NUMBER_OF_ITEMS];


// function prototypes

void close (char*, int);								// close something
void close_door (int);								// close door
void create_items ();								// create items
void create_map ();									// build apartment map from fixed data
void drop_item (char*, int);						// drop item
void examine_item (char*, int);						// examine item
void get_item (char*, int);							// pick up item
int  is_vowel (char);								// test if character is vowel or not
void lock (char*, int);								// lock something
void lock_door (int);								// lock a door
void move_player (char*, int*, int);					// move player from one room to another
void open (char*, int);								// open something
void open_door (int);								// open door
int  parse (char*, char*, char*);					// simple two-word parser
void prepare_input (char*);							// delete \n, make upper case
void say_something (char* text);					// say text
int  search_item (char*);							// search item in list
void show_exits (int, int);							// show exits for a specific room
void show_inventory ();								// show personal inventory
void show_items (int);								// show items in room
int  specify_door (int);							// ask player about door to be interacted with
int  twisty_little_passages ();						// random number generator for the maze
void unlock (char*, int);							// unlock something
void unlock_door (int);								// unlock door


int main ()
{
	char direction;									// where to go next
	char input[101];							    // user input string
	char verb[51];									// verb returned by parser
	char object[51];								// object returned by parser
	int action_class;								// action class returned by parser
	int current_room;								// current position
	int previous_room;
	int i;											// loop counter
	int maze         = 0;							// are you currently in the maze?
	int moves        = 0;							// moves counter
	int repeat_input = 1;							// input okay?
	int found_out	 = 0;							// user found the way out
	int look_around  = 0;							// flag to give full description next round
	int quit         = 0;							// user wants to quit?
	int score        = 0;							// score: how many items do you take with you?

	srand (time (NULL));
	create_map ();
	create_items ();
	
	current_room  = BEDROOM;							// position player in first room
	previous_room = -1;
	
	puts ("TINY TEXT ADVENTURE - VERSION 0.0000004");
	puts ("=======================================\n");
	printf ("Welcome! You just woke up and need to leave the apartment. ");
	
	do												// main gameplay loop
	{
		if (current_room != previous_room || look_around || maze || verbose)
			{
				if ((verbose == 1) || (room[current_room].visited == 0) || (look_around == 1) || (maze == 1))
					{
						puts (room[current_room].descriptor);		// show room description
						show_items (current_room);					// show items in this room
						show_exits (current_room, maze);				// show possible exits
					}
				else
					{
								printf ("You are in the %s. ", room[current_room].name);
								show_items (current_room);					// show items in this room
								show_exits (current_room, maze);				// show possible exits
					}
			}
		previous_room = current_room;
		look_around = 0;
		room[current_room].visited = 1;				// remember: been there
		moves++;									// increment counter
		
		do											// get input from user
		{
			printf ("> ");
			repeat_input = 0;
			fgets (input, 100, stdin);
			prepare_input (input);
			strcpy (verb, "");						// prepare variables for parser
			strcpy (object, "");
			action_class = parse (input, verb, object);
			if ((action_class == -1) && strcmp (verb, ""))
				puts ("I do not know how to do this.");
		} while (action_class == -1);
		
		switch (action_class)						// select what user wants to do
		{
			case 0:									// action_class  0: quit, exit, ...
				quit = 1;
				break;
			case 1:									// action_class  1: go, walk, ...
				move_player (object, &current_room, maze);
				break;
			case 2:									// action_class  2: dance, sing, ...
				puts ("Come on, don't be silly.");
				break;
			case 3:									// action_class  3: say, utter, ...
				say_something (object);
				break;
			case 4:									// action_class  4: wait
				puts ("Time passes.");
				break;
			case 5:									// action_class  5: kill, punch, ...
				puts ("Violence is never the answer!");
				break;
			case 6:									// action_class  6: get, take, ...
				get_item (object, current_room);	
				break;
			case 7:									// action_class  7: inventory, i
				show_inventory ();
				moves--;
				break;
			case 8:									// action_class  8: drop, throw, ...
				drop_item (object, current_room);
				break;
			case 9:									// action_class  9: open
				open (object, current_room);
				break;
			case 10:								// action_class 10: close
				close (object, current_room);
				break;
			case 11:								// action_class 11: unlock
				unlock (object, current_room);
				break;
			case 12:								// action_class 12: lock
				lock (object, current_room);
				break;
			case 13:								// action_class 13: examine, x
				examine_item (object, current_room);
				break;
			case 14:								// action_class 14: brief (verbose off)
				verbose = 0;
				moves--;
				break;
			case 15:								// action_class 15: verbose mode
				verbose = 1;
				moves--;
				break;
			case 16:								// action_class 16: look
				look_around = 1;
				break;
		}
		
		if (current_room == OUTSIDE)					// player is outside the apartment
			found_out = 1;
		
		if (current_room == PASSAGES)				// player is in maze
			maze = 1;
		
		if (maze == 1)								// if in maze: find out if you will stay for the next round
			{
				maze = twisty_little_passages();
				if (maze == 0)						// if no longer in maze: place player in bathroom
					{
						puts ("You miraculously escape the maze. Phew, close call!");
						current_room = BATHROOM;
					}
			}
		
	} while (!quit && !found_out);
	
	if (quit == 1)									// game was quit
		puts ("You spectacularly failed your quest to save the world. Actually, you did not even find out of your own apartment.");
	else											// game was won
		{
			puts (room[OUTSIDE].descriptor);
			puts ("You heroically found the way out of your apartment. I am so proud of you.");
			for (i = 0; i < NUMBER_OF_ITEMS; i++)
				{
					if (item[i].location == INVENTORY)
						score++;
				}
			printf ("You took %d of %d items with you.\n", score, NUMBER_OF_ITEMS);
		}
	printf ("Thank you for playing this useless game for %d moves.\n", moves - 1);
	return 0;
}


void close (char* object, int room_number)			// find out what to close
{
	if (!strcmp (object, "DOOR"))
		{
			close_door (room_number);
			return;
		}
	else if (!strcmp (object, ""))
		{
			puts ("You must tell me what to close.");
			return;
		}
	else
		{
			puts ("I do not know how to close that.");
		}
}


void close_door (int room_number)					// close a door
{
	int door;
	
	door = specify_door (room_number);				// ask which door to close
	switch (room[room_number].exits[door][0])
	{
		case OPEN:									// open doors will be closed
			puts ("You close the door.");
			room[room_number].exits[door][0] = CLOSED;
			room[room[room_number].exits[door][1]].exits[(door + 2) % 4][0] = CLOSED;
			break;
		case CLOSED:									// closed and locked doors are already closed
			puts ("This door is already closed.");
			break;
		case LOCKED:
			puts ("This door is closed and locked.");
			break;
	}
}


void create_items ()									// create and place the items
{
	item[0].name        = "key";
	item[0].descriptor  = "This is a plain metal key that unlocks every door in your apartment.";
	item[0].type        = KEY;
	item[0].location    = LIVING_ROOM;
	strcpy (item[0].synonyms[0], "");
	
	item[1].name        = "apple";
	item[1].descriptor  = "This apple looks healthy. Or is it poisoned?";
	item[1].type        = FOOD;
	item[1].location    = KITCHEN;
	strcpy (item[1].synonyms[0], "fruit");
	strcpy (item[2].synonyms[1], "vegetable");
	strcpy (item[2].synonyms[2], "");
	
	item[2].name        = "bottle";
	item[2].descriptor  = "The blueish-tinted bottle contains clear water. This has to taste boring.";
	item[2].type        = DRINK;
	item[2].location    = KITCHEN;
	strcpy (item[2].synonyms[0], "water");
	strcpy (item[2].synonyms[1], "flask");
	strcpy (item[2].synonyms[2], "jug");
	strcpy (item[2].synonyms[3], "");
	
	item[3].name        = "lamp";
	item[3].descriptor  = "This brass lantern looks like it comes from another game.";
	item[3].type        = LAMP;
	item[3].location    = HALLWAY;
	strcpy (item[3].synonyms[0], "light");
	strcpy (item[3].synonyms[1], "lantern");
	strcpy (item[3].synonyms[2], "");
	
	item[4].name        = "towel";
	item[4].descriptor  = "This is a large, soft towel. You feel well-prepared just looking at and admiring it.";
	item[4].type        = OTHER;
	item[4].location    = BATHROOM;
	strcpy (item[4].synonyms[0], "cloth");
	strcpy (item[4].synonyms[1], "washcloth");
	strcpy (item[4].synonyms[2], "");
	
	item[5].name        = "leaf-blower";
	item[5].descriptor  = "This is a state-of-the-art leaf-blower powered by the latest AI technology. It will automatically detect falling leaves, blowing them right into your least favorite neighbors' garden. Made of titanium-enforced aluminum, it looks as good as it was overprized. Pity it's broke.";
	item[5].type        = OTHER;
	item[5].location    = GARDEN;
	strcpy (item[5].synonyms[0], "blower");
	strcpy (item[5].synonyms[1], "device");
	strcpy (item[5].synonyms[2], "");
}


void create_map ()									// build the game world map
{
	room[HALLWAY].name            = "hallway";
	room[HALLWAY].descriptor      = "You are standing in the hallway. One door leads to the west to the other rooms, while the front door leads outside to the east. You can hear the sound of cars driving by. A door to the north leads to your garden.";
	room[HALLWAY].exits[NORTH][0] = CLOSED;			// NORTH - door status
	room[HALLWAY].exits[NORTH][1] = GARDEN;			//         destination
	room[HALLWAY].exits[WEST] [0] = CLOSED;			// WEST  - door status
	room[HALLWAY].exits[WEST] [1] = LIVING_ROOM;	//         destination
	room[HALLWAY].exits[SOUTH][0] = NONE;			// SOUTH - door status
	room[HALLWAY].exits[SOUTH][1] = -1;				//         destination
	room[HALLWAY].exits[EAST] [0] = LOCKED;			// EAST  - door status
	room[HALLWAY].exits[EAST] [1] = OUTSIDE; 	  	//         destination
	room[HALLWAY].visited         = 0;				// not visited before
	
	room[LIVING_ROOM].name            = "living room";
	room[LIVING_ROOM].descriptor      = "You are in the living room. The sun shines brightly through the skylights. There are doors leading in all directions.";
	room[LIVING_ROOM].exits[NORTH][0] = CLOSED;
	room[LIVING_ROOM].exits[NORTH][1] = BEDROOM;
	room[LIVING_ROOM].exits[WEST] [0] = CLOSED;
	room[LIVING_ROOM].exits[WEST] [1] = KITCHEN;
	room[LIVING_ROOM].exits[SOUTH][0] = CLOSED;
	room[LIVING_ROOM].exits[SOUTH][1] = BATHROOM;
	room[LIVING_ROOM].exits[EAST] [0] = CLOSED;
	room[LIVING_ROOM].exits[EAST] [1] = HALLWAY;
	room[LIVING_ROOM].visited         = 0;
	
	room[BATHROOM].name            = "bathroom";
	room[BATHROOM].descriptor      = "You are standing in a small, cramped bathroom. In the south, you can spot an ominous portal leading into a dark abyss. You can return to the safety of your living room by taking the north door.";
	room[BATHROOM].exits[NORTH][0] = CLOSED;
	room[BATHROOM].exits[NORTH][1] = LIVING_ROOM;
	room[BATHROOM].exits[WEST] [0] = NONE;
	room[BATHROOM].exits[WEST] [1] = -1;
	room[BATHROOM].exits[SOUTH][0] = OPEN;
	room[BATHROOM].exits[SOUTH][1] = PASSAGES;
	room[BATHROOM].exits[EAST] [0] = NONE;
	room[BATHROOM].exits[EAST] [1] = -1;
	room[BATHROOM].visited         = 0;
	
	room[KITCHEN].name             = "kitchen";
	room[KITCHEN].descriptor       = "The kitchen is surprisingly large, but very untidy. You can escape the mess by going back east into the living room.";
	room[KITCHEN].exits[NORTH][0]  = NONE;
	room[KITCHEN].exits[NORTH][1]  = -1;
	room[KITCHEN].exits[WEST] [0]  = NONE;
	room[KITCHEN].exits[WEST] [1]  = -1;
	room[KITCHEN].exits[SOUTH][0]  = NONE;
	room[KITCHEN].exits[SOUTH][1]  = -1;
	room[KITCHEN].exits[EAST] [0]  = CLOSED;
	room[KITCHEN].exits[EAST] [1]  = LIVING_ROOM;
	room[KITCHEN].visited          = 0;
	
	room[BEDROOM].name             = "bedroom";
	room[BEDROOM].descriptor       = "You are in your bedroom. Outside, you hear birds chirping.";
	room[BEDROOM].exits[NORTH][0]  = NONE;
	room[BEDROOM].exits[NORTH][1]  = -1;
	room[BEDROOM].exits[WEST] [0]  = NONE;
	room[BEDROOM].exits[WEST] [1]  = -1;
	room[BEDROOM].exits[SOUTH][0]  = CLOSED;
	room[BEDROOM].exits[SOUTH][1]  = LIVING_ROOM;
	room[BEDROOM].exits[EAST] [0]  = NONE;
	room[BEDROOM].exits[EAST] [1]  = -1;
	room[BEDROOM].visited          = 0;
	
	room[OUTSIDE].name             = "outside";
	room[OUTSIDE].descriptor       = "You have finally reached the outside.";
	room[OUTSIDE].exits[NORTH][0]  = NONE;
	room[OUTSIDE].exits[NORTH][1]  = -1;
	room[OUTSIDE].exits[WEST] [0]  = LOCKED;
	room[OUTSIDE].exits[WEST] [1]  = HALLWAY;
	room[OUTSIDE].exits[SOUTH][0]  = NONE;
	room[OUTSIDE].exits[SOUTH][1]  = -1;
	room[OUTSIDE].exits[EAST] [0]  = NONE;
	room[OUTSIDE].exits[EAST] [1]  = -1;
	room[OUTSIDE].visited          = 0;
	
	room[PASSAGES].name            = "labyrinth";
	room[PASSAGES].descriptor      = "You are in a maze of twisty little passages, all alike.";
	room[PASSAGES].exits[NORTH][0] = OPEN;
	room[PASSAGES].exits[NORTH][1] = BATHROOM;
	room[PASSAGES].exits[WEST] [0] = NONE;
	room[PASSAGES].exits[WEST] [1] = -1;
	room[PASSAGES].exits[SOUTH][0] = NONE;
	room[PASSAGES].exits[SOUTH][1] = -1;
	room[PASSAGES].exits[EAST] [0] = NONE;
	room[PASSAGES].exits[EAST] [1] = -1;
	room[PASSAGES].visited         = 0;
	
	room[GARDEN].name              = "garden";
	room[GARDEN].descriptor        = "You are in a small garden. A small white fence shields it from the street and the adjacent small gardens. Small white clouds are reflected in the water of your small pond surrounded by a small patch of lawn. Chirping with a small voice, a small bird sits on a small tree. A sense of idyllic bliss washes over you, producing a small smile on your small face.";
	room[GARDEN].exits[NORTH][0]   = NONE;
	room[GARDEN].exits[NORTH][1]   = -1;
	room[GARDEN].exits[WEST] [0]   = NONE;
	room[GARDEN].exits[WEST] [1]   = -1;
	room[GARDEN].exits[SOUTH][0]   = CLOSED;
	room[GARDEN].exits[SOUTH][1]   = HALLWAY;
	room[GARDEN].exits[EAST] [0]   = NONE;
	room[GARDEN].exits[EAST] [1]   = -1;
	room[GARDEN].visited           = 0;
}


void drop_item (char* which_item, int room_number)	// drop an item in a room
{
	char* temp_string;								// temporary ALLCAPS to enable comparing
	int i, j;
	int found = 0;
	int item_number;
	
	if (!(strcmp (which_item, "")))
		{
			puts ("You must tell me what you want to drop.");
		}
	else if (!(strcmp (which_item, "ALL")))			// DROP ALL will not be implemented
		{
			puts ("You cannot drop all your items at once.");
		}
	else if (room_number == PASSAGES)				// no dropping in the maze
		{
			puts ("You would never find this again in this labyrinth!");
		}
	else											// find out if item is in player inventory, move it to room inventory
		{
			for (i = 0; i < NUMBER_OF_ITEMS; i++)
				{
					for (i = 0; i < NUMBER_OF_ITEMS; i++)
						{
							item_number = search_item (which_item);
							if (item_number >= 0)
								{
									if (item[item_number].location == INVENTORY)
										{
											printf ("You drop the %s.\n", item[item_number].name);
											item[item_number].location = room_number;
											found = 1;
										}
								}
						}
				}
			if (!found)								// give feedback when you did not have the item
				{
					temp_string = malloc (strlen (which_item) + 1);
					strcpy (temp_string, which_item);
					for (j = 0; j < strlen (temp_string); j++)
						temp_string[j] = tolower (temp_string[j]);
					printf ("You do not have any %s.\n", temp_string);
					free (temp_string);
				}
		}
	
}


void examine_item (char* current_item, int current_room)
{
	int item_number = search_item(current_item);
	
	if (item_number == -1)
		{
			char* output;
			output = malloc ((strlen (current_item) + 1) * sizeof (char));
			for (int i = 0; i < strlen (current_item); i++)
				output[i] = tolower (current_item[i]);
			if (is_vowel (output[0]))
				printf ("I do not know what an %s is.\n", output);
			else
				printf ("I do not know what a %s is.\n", output);
			free (output);
		}
	else
		{
			if (item[item_number].location == current_room || item[item_number].location == INVENTORY)
				puts (item[item_number].descriptor);
			else
				{
					char* output;
					output = malloc ((strlen (current_item) + 1) * sizeof (char));
					for (int i = 0; i < strlen (current_item); i++)
						output[i] = tolower (current_item[i]);
					printf ("There is no %s here.\n", output);
					free (output);
				}
		}
}


void get_item (char* which_item, int room_number)	// take something: determine what
{
	char* temp_string;
	int i, j;
	int found = 0;
	int item_number;
	
	if (!(strcmp (which_item, "")))
		puts ("You must tell me what you want to take with you.");
	else if (!(strcmp (which_item, "ALL")))			// TAKE ALL should be implemented in the future
		puts ("Don't be greedy.");
	else if (!(strcmp (which_item, "UP")))			// GET UP
		puts ("You are already on your feet.");
	else											// find out if item is in room inventory, move it to player inventory
		{
			for (i = 0; i < NUMBER_OF_ITEMS; i++)
				{
					item_number = search_item (which_item);
					if (item_number >= 0)
						{
							if (item[item_number].location == room_number)
								{
									printf ("You pick up the %s.\n", item[item_number].name);
									item[item_number].location = INVENTORY;
									found = 1;
								}
						}
				}
			if (!found)								// give feedback when item was not there
				{
					temp_string = malloc (strlen (which_item) + 1);
					strcpy (temp_string, which_item);
					for (j = 0; j < strlen (temp_string); j++)
						temp_string[j] = tolower (temp_string[j]);
					printf ("There is no %s here.\n", temp_string);
					free (temp_string);
				}
		}
}


int is_vowel (char test)							// vowel or not? will be needed to distinguish "AN apple" and "A banana"
{
	test = toupper (test);
	
	if (test == 'A' || test == 'E' || test == 'I' || test == 'O' || test == 'U')
		return 1;
	else
		return 0;
}


void lock (char* object, int room_number)			// lock something: find out what to lock
{
	if (!(strcmp (object, "")))
		puts ("Please tell me what to lock.");
	else if (!(strcmp (object, "DOOR")))
		lock_door (room_number);
	else
		puts ("I do not know how to lock this.");
}


void lock_door (int room_number)					// lock a door
{
	int door = specify_door(room_number);			// ask player which door to lock
	if (room[room_number].exits[door][0] == LOCKED)	// is it already locked?
		puts ("This door is already locked.");
	else
		{
			if (item[KEY].location != INVENTORY)		// do you have the key?
				puts ("You do not have the key with you.");
			else
				{
					if (room[room_number].exits[door][0] == CLOSED)
						{							// lock both sides of the door
							puts ("You lock the door.");
							room[room_number].exits[door][0] = LOCKED;
							room[room[room_number].exits[door][1]].exits[(door + 2) % 4][0] = LOCKED;
						}
					else								// close door, then lock both sides
						{
							puts ("You lock the door, closing it first.");
							room[room_number].exits[door][0] = LOCKED;
							room[room[room_number].exits[door][1]].exits[(door + 2) % 4][0] = LOCKED;
						}
				}
		}
}


void move_player (char* destination, int* current_room, int maze)	// move player around
{
	if (maze == 1)									// don't move when player is in maze
		return;
	
	int direction = -1;
	int door_status;
	
	switch(destination[0])							// where to move
	{
		case('N'):
			direction = NORTH;
			break;
		case ('W'):
			direction = WEST;
			break;
		case ('S'):
			direction = SOUTH;
			break;
		case ('E'):
			direction = EAST;
			break;
	}
	
	if (direction != -1)							// valid direction was given
		{
			door_status = room[*current_room].exits[direction][0];
			switch (door_status)
				{
					case 0:
						puts ("There is no exit in this direction.");				// no door
						break;
					case 1:
						puts ("The door is locked.");								// locked
						break;
					case 2:
						if ((*current_room == HALLWAY) && (direction == EAST) && (room[HALLWAY].exits[NORTH][0] != LOCKED))
							{
								puts ("Better lock the garden door before you leave.");		// don't leave until garden door is locked
								break;
							}
						else
							{
								puts ("You go through the door, opening it first.");
								room[*current_room].exits[direction][0] = OPEN;				// closed door -> automatically open it
								*current_room = room[*current_room].exits[direction][1];	// change room
								room[*current_room].exits[(direction + 2) % 4][0] = OPEN;	// open door in opposite direction
								break;
							}
					case 3:
						if ((*current_room == HALLWAY) && (direction == EAST) && (room[HALLWAY].exits[NORTH][0] != LOCKED))
							{
								puts ("You worry about the unlocked garden door.");			// don't leave until garden door is locked
								break;
							}
						else
							{
								if (verbose != 0)
									puts ("You go through the open door.");
								*current_room = room[*current_room].exits[direction][1];		// change room
								break;
							}
				}
		}
	else
		puts ("I do not know this direction.");
}


void open (char* object, int room_number)				// open something: what?
{
	if (!strcmp (object, "DOOR"))
		{
			open_door (room_number);
			return;
		}
	else if (!strcmp (object, ""))
		{
			puts ("You must tell me what to open.");
			return;
		}
	else
		{
			puts ("I do not know how to open that.");
		}
}


void open_door (int room_number)						// open a door
{
	int door;
	
	door = specify_door(room_number);					// ask player what door to open
	
	switch (room[room_number].exits[door][0])
	{
		case CLOSED:
			puts ("You open the door.");
			room[room_number].exits[door][0] = OPEN;
			room[room[room_number].exits[door][1]].exits[(door + 2) % 4][0] = OPEN;
			break;
		case OPEN:
			puts ("This door is already open.");
			break;
		case LOCKED:
			puts ("This door is locked.");
			break;
	}
	
}


int parse (char* input, char* verb, char* object)		// parser
{
	int action_class = -1;								// action_class is the return value and gives the category of the verb
	int i;
	
	sscanf (input, "%s %s", verb, object);
	
	// This is not elegant. I need to create a 2D array that stores synonyms for all action classes.
	// Problem is how to handle one- and two-word inputs: "exit room" may not result in quitting the game.
	
	if ((!(strcmp (verb, "QUIT")) || !(strcmp (verb, "Q")) || !(strcmp (verb, "EXIT"))) && !strcmp (object, ""))
		action_class =  0;
	else if (!(strcmp (verb, "GO")) || !(strcmp (verb, "WALK")) || !(strcmp (verb, "MOVE")) || !(strcmp (verb, "PROCEED")) || !(strcmp (verb, "HEAD")) || !(strcmp (verb, "TRAVEL")) || !(strcmp (verb, "EXPLORE")) || !(strcmp (verb, "NAVIGATE")) || !(strcmp (verb, "RUN")) || !(strcmp (verb, "WANDER")) || !strcmp (verb, "STROLL"))
		action_class =  1;
	else if ((!(strcmp (verb, "NORTH")) || !(strcmp (verb, "N")) || !(strcmp (verb, "WEST")) || !(strcmp (verb, "W")) || !(strcmp (verb, "SOUTH")) || !(strcmp (verb, "S")) || !(strcmp (verb, "EAST")) || !strcmp (verb, "E")) && !(strcmp (object, "")))
		{
			strcpy (object, verb);						// "object" is direction, so the "verb" will be copied there
			action_class = 1;
		}
	else if (!(strcmp (verb, "DANCE")) || !(strcmp (verb, "SING")) || !(strcmp (verb, "ENTERTAIN")))
		action_class =  2;
	else if (!(strcmp (verb, "SAY")) || !strcmp (verb, "TALK") || !(strcmp (verb, "UTTER")))
		action_class =  3;
	else if (!(strcmp (verb, "WAIT")))
		action_class =  4;
	else if (!(strcmp (verb, "KILL")) || !strcmp (verb, "PUNCH") || !(strcmp (verb, "KICK")) || !(strcmp (verb, "HIT")) || !(strcmp (verb, "DESTROY")))
		action_class =  5;
	else if (!(strcmp (verb, "GET")) || !(strcmp (verb, "TAKE")) || !(strcmp (verb, "OBTAIN")) || !(strcmp (verb, "FETCH")) || !(strcmp (verb, "COLLECT")) || !(strcmp (verb, "RECEIVE")) || !(strcmp (verb, "GRAB")) || !(strcmp (verb, "ACQUIRE")) || !(strcmp (verb, "ATTAIN")) || !(strcmp (verb, "GAIN")))
		action_class =  6;
	else if (!(strcmp (verb, "I")) || !(strcmp (verb, "INVENTORY")))
		action_class =  7;
	else if (!(strcmp (verb, "DROP")) || !(strcmp (verb, "DITCH")) || !(strcmp (verb, "THROW")) || !(strcmp (verb, "TOSS")) || !(strcmp (verb, "RELEASE")) || !(strcmp (verb, "LEAVE")) || !(strcmp (verb, "DISCHARGE")) || !(strcmp (verb, "RELINQUISH")) || !(strcmp (verb, "DISCARD")) || !(strcmp (verb, "ABANDON")))
		action_class =  8;
	else if (!(strcmp (verb, "OPEN")))
		action_class =  9;
	else if (!(strcmp (verb, "CLOSE")))
		action_class = 10;
	else if (!(strcmp (verb, "UNLOCK")) || !(strcmp (verb, "UNSEAL")) || !(strcmp (verb, "UNBOLT")) || !(strcmp (verb, "UNLATCH")) || !(strcmp (verb, "UNBLOCK")) || !(strcmp (verb, "UNCHAIN")))
		action_class = 11;
	else if (!(strcmp (verb, "LOCK")) || !(strcmp (verb, "SECURE")) || !(strcmp (verb, "SEAL")) || !(strcmp (verb, "BOLT")) || !(strcmp (verb, "LATCH")) || !(strcmp (verb, "BLOCK")) || !(strcmp (verb, "CHAIN")))
		action_class = 12;
	else if (!(strcmp (verb, "EXAMINE")) || !(strcmp (verb, "X")))
		action_class = 13;
	else if (!(strcmp (verb, "BRIEF")))
		action_class = 14;
	else if (!(strcmp (verb, "VERBOSE")))
		action_class = 15;
	else if (!(strcmp (verb, "LOOK")) || !(strcmp (verb, "L")))
		action_class = 16;

	return action_class;
}


void prepare_input (char* input)							// formalize input strings
{
	int i;
	
	if (input[strlen (input) - 1] == '\n')				// delete final '\n'
		input[strlen (input) - 1] = '\0';
	for (i = 0; i <= strlen (input); i++)				// switch to upper case
		input[i] = toupper (input[i]);
}


void say_something (char* text)							// say text or crack cheap joke
{
	if (!strcmp (text, "XYZZY"))
		puts ("A hollow voice says \'FOOL.\'");
	else
		printf ("\'%s.\' -- Nothing happens.\n", text);
}


int search_item (char* object)
{
	int found = 0;
	int i, j;
	char* temp_string;
	temp_string = malloc ((strlen (object) + 1) * sizeof (char));
	strcpy (temp_string, object);

	for (i = 0; i < strlen (temp_string); i++)
		temp_string[i] = tolower (temp_string[i]);

	for (i = 0; i < NUMBER_OF_ITEMS; i++)
		{
			if (!strcmp (item[i].name, temp_string))
				{
					found = 1;
					break;
				}
		}

	if (!found)
		{
			for (i = 0; i < NUMBER_OF_ITEMS; i++)
				{
					for (j = 0; strlen (item[i].synonyms[j]) > 0; j++)
						{
							if (! (strcmp (item[i].synonyms[j], temp_string)))
								{
									found = 1;
									break;
								}
						}
					if (found)
						break;
				}
		}
	free (temp_string);
	
	if (found)
		return i;
	else
		return -1;
}


void show_exits (int room_number, int maze)				// show a room's exits
{
	if (maze == 1)										// ...but not when you are in the maze
		return;
	
	int i;
	int status;
	
	printf ("Exits: ");
	for (i = 0; i < 4; i++)
		{
			if (room[room_number].exits[i][0] != NONE)
				printf ("%s (%s). ", main_directions[i], exit_status[room[room_number].exits[i][0]]);
		}
	puts ("");
}


void show_inventory ()									// show items in the player inventory
{
	int i;
	int flag = 0;
	
	printf ("Contents of your personal inventory: ");
	for (i = 0; i < NUMBER_OF_ITEMS; i++)
		{
			if (item[i].location == INVENTORY)
				{
					if (is_vowel (item[i].name[0]))
						printf ("An %s. ", item[i].name);
					else
						printf ("A %s. ", item[i].name);
					flag = 1;
				}
		}
	if (!flag)
		puts ("(none)");
	else
		puts ("");
}


void show_items (int room_number)						// show items in the room inventory
{
	int i;
	int flag = 0;
	
	for (i = 0; i < NUMBER_OF_ITEMS; i++)
		{
			if (item[i].location == room_number)
				{
					if (is_vowel (item[i].name[0]))
						printf ("There is an ");
					else
						printf ("There is a ");
					printf ("%s here. ", item[i].name);
					flag = 1;
				}
		}
	if (flag)
		puts ("");
}


int specify_door (int current_room)						// list doors, ask player which one is meant
{
	int i;
	int flag = 0;
	char input[10];
	char existing_doors[5] = "";
	
	printf ("You can see doors leading to ");
	for (i = 0; i < 4; i++)
		{
			if (*(room[current_room].exits[i]) != NONE)
				{
					printf ("%s. ", main_directions[i]);
					strcat (existing_doors, main_directions[i]);
				}
		}
	
	do
		{
			printf ("Which door do you mean? ");
			fgets (input, 8, stdin);
			input[0] = toupper (input[0]);
			if (strchr (existing_doors, input[0]) || input[0] == 'Q')
				flag = 1;
		}
	while (!flag);
	
	switch (input[0])
	{
		case 'N':
			return NORTH;
		case 'W':
			return WEST;
		case 'S':
			return SOUTH;
		case 'E':
			return EAST;
		default:
			return -1;
	}
}


int twisty_little_passages ()							// some stuff for the maze
{
	int random = rand () % 100;
	if (random >= 90)									// random remarks with 10 % chance each and 10 % chance that no remark is generated
		printf ("You see the skeleton of an unlucky adventurer in the distance. ");
	if (random >= 80 && random < 90)
		printf ("You hear eerie sounds from far away. ");
	if (random >= 70 && random < 80)
		printf ("A sullen werewolf passes. ");
	if (random >= 60 && random < 70)
		printf ("You have a bad feeling about this. ");
	if (random >= 50 && random < 60)
		printf ("A hungry grue salutes you. ");
	if (random >= 40 && random < 50)
		printf ("The walls seem to close in on you. ");
	if (random >= 30 && random < 40)
		printf ("The ground shakes slightly. ");
	if (random >= 20 && random < 30)
		printf ("Your senses fail you. ");
	if (random >= 10 && random < 20)
		printf ("A passing ghoul politely greets you but ushers on. ");
	if (random >=  0 && random < 10)
		printf ("It's getting uncomfortably hot. ");
	
	if (random < 20)									// 20 % chance to exit the maze
		return 0;
	else
		return 1;
}


void unlock (char* object, int room_number)				// unlock something
{
	if (!(strcmp (object, "")))
		puts ("Please tell me what to unlock.");
	else if (!(strcmp (object, "DOOR")))
		unlock_door (room_number);
	else
		puts ("I do not know how to unlock this.");
}


void unlock_door (int room_number)						// unlock a door
{
	int door = specify_door(room_number);				// which one?
	if (room[room_number].exits[door][0] != LOCKED)
		puts ("This door is not locked.");
	else
		{
			if (item[KEY].location != INVENTORY)
				puts ("You do not have the key with you.");
			else
				{
					puts ("You unlock the door.");		// unlock both sides
					room[room_number].exits[door][0] = CLOSED;
					room[room[room_number].exits[door][1]].exits[(door + 2) % 4][0] = CLOSED;
				}
		}
}