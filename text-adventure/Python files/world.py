import random


class World:
    """
    This class handles some status effects of the overall game world.
    """

    def __init__(self):
        """
        Initialize the "quit" flag and set a weather condition.
        """

        self.quit_game = False
        self.weather   = "sunny"

    def commands(self, verb_dictionary):
        """
        Display list of available commands.
        """

        print("Available commands:", ", ".join(c for c in sorted(list(verb_dictionary.keys()))) + ".")

    def enable_brief_mode(self, flag):
        """
        Switch on the brief mode.
        """

        if flag == False:
            print("The game is already in brief mode.")
        else:
            print("The game is now in brief mode.")
        return False

    def enable_verbose_mode(self, flag):
        """
        Switch on the verbose mode.
        """

        if flag == True:
            print("The game is already in verbose mode.")
        else:
            print("The game is now in verbose mode.")
        return True

    def look_around(self):
        """
        Set flag to show complete room descriptions at next round.
        """

        return True

    def update_weather(self):
        """
        Change the weather condition.
        """

        conditions = {
            "clear" : "You notice the sun is shining brightly outside.",
            "cloudy": "You notice it is cloudy outside.",
            "foggy" : "The light coming in has developed a foggy blur.",
            "snowy" : "Miraculously, snow has started falling outside.",
            "stormy": "You hear a storm howling outside."
        }

        self.weather = random.choice(list(conditions.keys()))
        print(conditions[self.weather])

    def quit(self):
        """
        Set the flag to quit the game after this round.
        """

        self.quit_game = True
        return self.quit_game

    def wait(self):
        """
        Do nothing.
        """

        print("Time passes.")