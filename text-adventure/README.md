# Tiny Text Adventure

## Modular Text Adventure Framework

------

This is a Python-based text adventure engine with an additional preservation of its original C concept. In addition to a small apartment, the Python version has a dynamic NPC wandering around, a second static NPC, and some more complex interactions. The architecture seems flexible enough to support much bigger ideas ... if I ever had written them. :)

It was written as a personal project to explore both modular design and object-oriented programming, and adventure game architecture to get deeper insight into game design for my game studies hobby. It's basically a huge playground for ideas about how to structure a text-based world, and how to make it both flexible and moderately silly.

------

## Features

- Modular structure with a `main.py` starting point and additional modules:
  - `world.py` -- world state and weather
  - `room.py` -- room management
  - `item.py` -- item handling and item manager
  - `player.py` -- player character
  - `npc.py` -- static and dynamic NPCs
  - `definitions.py` -- global constants
  - `utilities.py` -- helper functions
- Flexible parser with synonyms, "it" replacing the last substantive ("drop it"), "about", "and", "with" for multi-token input
- Dynamic NPC class for characters that move randomly around
- Basic stats system (health, level, experience points), although inconsequential
- Food and drink, poison and medicine
- Inventory management and item combination for a crafting system
- Labyrinth (twisty passages) with random events and escape chance
- Different types of objects: weapons, furniture, food, drink, etc.; immovable objects, invisible objects
- Room descriptions adapt based on whether you've visited before
- Optional verbose mode for full or brief room descriptions
- Weather changes randomly over time (purely for flavor)
- It's peppered with easter eggs and in-jokes, and with mechanics like opening/closing doors, and even locking doors, that show emergent gameplay mechanics: Try to lock Anne in a room, and she'll never get out. Try crafting a red flag. Try escaping the dungeon before getting eaten by a Grue. (Just kidding. (Am I?))

------

## Limitations

- No real quest or victory condition beyond "escape apartment"
- No saving or loading games
- No combat system (despite "weapons" being there)
- No complex dialogue trees: talking is keyword-based
- You can get poisoned, but you won't die (how disappointing!)

---

## Possible Extensions (aka "what I thought about, but didn't have the nerve and competence to actually code")

- Quest system (multi-stage)
- Proper saving/loading
- Complex item crafting system
- Multi-room NPC patrol routes
- Dynamic world state events (e.g., night/day cycle)
- And so much more!

------

## C Version

This was written mostly as a learning playground for basic string handling, structs, and gameplay loops in C. Everything is experimental at best. The most surprising feature is that it actually works!

------

christoph.hust@hmt-leipzig.de