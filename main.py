"""
Author  : VoltRadar
Date    : 2023
Licence : MIT
"""


import threading
import time
import random

from threading import Thread

import pygame
from pygame import locals

morse = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
}

font_name = 'consolas'


def morse_length(character) -> int:
    """
    Gets the amount of time that it takes to key a character in morse

    :return: number of 'dit' lengths it takes to key a character in morse
    :raises KeyError: If character doesn't have morse code
    """
    morse_sequence = morse[character]

    length = 0

    # Length of the dits and dahs
    for morse_character in morse_sequence:
        assert morse_character in ".-" and len(morse_character) == 1

        if morse_character == ".":
            length += 1
        else:
            length += 3

    # Add length between dits and dahs
    length += len(morse_sequence) - 1

    return length


class Box(pygame.sprite.Sprite):
    """
    Class for the box in the game that flashes
    """
    dit_length = 0.08
    box_width = 200
    box_height = 200
    border_width = 10

    inner_colour_normal = (0, 0, 0)
    # Colour of the inner box when flashing morse
    inner_colour_morse = (255, 255, 255)

    outer_colour_normal = (255, 255, 255)
    outer_colour_error = (255, 0, 0)
    outer_colour_too_slow = (255, 128, 0)
    outer_colour_correct = (0, 255, 0)

    font_colour_normal = (255, 255, 255)

    def __init__(self, ):
        """
        Creates a surface self.surf that may be drawn onto the screen
        The surface is a fill colour, and contains a slightly smaller rectangle
        at the center, making an outer boarder.
        Starts with outer colour being white, and the inner colour being black.
        """
        super(Box, self).__init__()

        self.tone = pygame.mixer.Sound("Files/tone.wav")

        # Flag to communicate when game is paused
        self.paused: threading.Event = threading.Event()

        self.surf = pygame.Surface((self.box_width, self.box_width))
        self.surf.fill(self.outer_colour_normal)

        self.inner_box = pygame.Rect(self.border_width,
                                     self.border_width,
                                     self.box_width - self.border_width * 2,
                                     self.box_height - self.border_width * 2
                                     )
        self.inner_box_colour = self.inner_colour_normal

        self.font = pygame.font.SysFont(font_name, 40, True)
        self.font_colour = self.font_colour_normal
        self.font_img: pygame.Surface | None = None
        self.set_font("")  # Set font to blank text

        self.draw_inner_box()

    def set_font(self, text):
        """
        Sets the font on the inner box. Also draws it, drawing over any text
        that already exists
        """
        # Draw over any text that exists already
        self.draw_inner_box()

        # Create the font image
        self.font_img = self.font.render(text, False, self.font_colour)

        self.draw_font()

    def draw_font(self):
        """
        Draws the font in the center of the inner box
        """
        if self.font_img and not self.paused.is_set():
            font_img_rect = self.font_img.get_rect()
            font_img_rect.center = (self.box_width / 2, self.box_height / 2)

            self.surf.blit(self.font_img, font_img_rect)

    def draw_inner_box(self):
        """
        Redraws the inner box. Required if either colour changes
        """
        if self.paused.is_set():
            self.inner_box_colour = self.inner_colour_normal

        pygame.draw.rect(self.surf, self.inner_box_colour, self.inner_box)

    def set_outer_colour(self, colour: tuple[int, int, int]):
        """
        Sets the boarder colour of the box
        :param colour: RGB tuple
        """
        if self.paused.is_set():
            colour = self.outer_colour_normal

        self.surf.fill(colour)
        self.draw_inner_box()
        self.draw_font()

    def set_inner_colour(self, colour):
        """
        Sets the inner colour of the box
        :param colour: RGB tuple
        """
        self.inner_box_colour = colour
        self.draw_inner_box()
        self.draw_font()

    def set_font_colour(self, colour: tuple[int, int, int]):
        """
        Sets the colour of the font in the inner box
        :param colour: RGB tuple
        """
        self.font_colour = colour
        self.draw_font()

    def play_error(self, correct_character, too_slow: bool):
        """
        Flashes the outer ring red and displays the correct character that the
        user should have entered. Waits a bit then plays what the character in
        morse again before another pause.

        If too_slow is set to True, then the box flashes orange to indicate
        that the character selected was correct, but was too slow

        You can play the next character immediately after this function finishes
        """
        if too_slow:
            colour = self.outer_colour_too_slow
        else:
            colour = self.outer_colour_error

        self.set_outer_colour(colour)
        self.set_font_colour(colour)

        self.set_font(correct_character)

        time.sleep(2)

        # Replay the correct character morse
        self.play_morse(correct_character)

        time.sleep(1)

        self.set_outer_colour(self.outer_colour_normal)
        self.set_font("")

        time.sleep(1)

    def play_correct(self):
        """
        Flashes the background green to indicate a successful decode.

        You can play the next character immediately after this function finishes
        """
        self.set_outer_colour(self.outer_colour_correct)
        time.sleep(0.5)

        self.set_outer_colour(self.outer_colour_normal)
        time.sleep(1)

    def dit(self):
        """
        Plays a 'dit'
        Plays sound and flashes the inner box

        Does nothing when the game is paused
        """
        if self.paused.is_set():
            return

        self.tone.play()
        self.set_inner_colour(self.inner_colour_morse)

        time.sleep(self.dit_length)

        self.tone.stop()
        self.set_inner_colour(self.inner_colour_normal)

    def dah(self):
        """
        Plays a 'dah'
        Plays sound and flashes the inner box. Does this for 3 times as long
        as Box.dit

        Does nothing when the game is paused
        """
        if self.paused.is_set():
            return

        self.tone.play()
        self.set_inner_colour(self.inner_colour_morse)

        time.sleep(self.dit_length * 3)

        self.tone.stop()
        self.set_inner_colour(self.inner_colour_normal)

    def play_morse(self, character: str):
        """
        Takes input as a character and plays its morse code. Flashes the box
        and plays a tone

        Waits a length of a dot between dots and dashes. Doesn't wait after
        character is done

        Must be run in a thread

        :param character: Letter or number
        """
        character_morse = morse[character]

        for i in character_morse:

            if self.paused.is_set():
                return

            if i == ".":
                self.dit()
            elif i == "-":
                self.dah()

            time.sleep(self.dit_length)

    def reset_box(self):
        """
        Draws the box in the normal state. White outline with a black inner
        colour, and no fonts
        """
        self.inner_box_colour = self.inner_colour_normal
        self.set_font("")

        self.set_outer_colour(self.outer_colour_normal)


class LettersLearned(pygame.sprite.Sprite):
    """
    Scorecard at the top of the game

    count is the top item at the top of the screen containing a count of the
    letters learned

    lines one and two are the lines of letters learned
    """

    # Size of scorecard
    height = 100

    # Number of pixels between text
    spacing = 5

    letters_per_line = 20
    font_size = 10

    font_colour_normal = (255, 255, 255)
    font_colour_new_letter = (0, 255, 0)

    def __init__(self, window_width):
        """
        Sets up the font object that will be used to render the text
        """
        super().__init__()

        self.width = window_width
        self.surf = pygame.Surface((window_width, self.height))

        self.font_size = 20
        self.font = pygame.font.SysFont(font_name, self.font_size, bold=True)

        self.font_colour_count = self.font_colour_normal
        self.font_colour_lines = self.font_colour_normal

        self.learned_letters: list[str] = []

        # Number on characters to learn
        self.letters_to_learn_count = len(morse)

        self.top_text_center = self.spacing + int(round(self.font_size / 2))
        self.bottom_text_center = self.height - int(self.spacing + round(self.font_size) / 2)

        # Image of rendered text
        self.font_img_count: pygame.Surface | None = None
        self.font_img_letter_line_one: pygame.Surface | None = None
        self.font_img_letter_line_two: pygame.Surface | None = None

        # Locations to draw the font images
        self.font_img_count_rect: pygame.rect.Rect | None = None
        self.font_img_letter_line_one_rect: pygame.rect.Rect | None = None
        self.font_img_letter_line_two_rect: pygame.rect.Rect | None = None

        self.update()

    def font_images(self):
        """
        Gets the font images
        """
        return [self.font_img_count,
                self.font_img_letter_line_one,
                self.font_img_letter_line_two]

    def font_rects(self):
        """
        Gets the location where the fonts will be drawn
        """
        return [self.font_img_count_rect,
                self.font_img_letter_line_one_rect,
                self.font_img_letter_line_two_rect]

    def render_on_surface(self):
        """
        Renders the font images onto the surface, according to their locations
        """

        self.surf.fill(color=(0, 0, 0))

        for image, rect in zip(self.font_images(), self.font_rects()):
            if image and rect:
                self.surf.blit(source=image, dest=rect)

    def create_font_images(self):
        """
        Sets the font images and font images rect objects bases on the current
        letters learned list

        :return: None
        """

        text_count = f"Letters learned {len(self.learned_letters)}/{len(morse.keys())}"
        text_line_one = " ".join(self.learned_letters[:self.letters_per_line])
        text_line_two = " ".join(self.learned_letters[self.letters_per_line:])

        img0 = self.font.render(text_count, False, self.font_colour_count)
        img1 = self.font.render(text_line_one, False, self.font_colour_lines)
        img2 = self.font.render(text_line_two, False, self.font_colour_lines)

        self.font_img_count = img0
        self.font_img_letter_line_one = img1
        self.font_img_letter_line_two = img2

        self.font_img_count_rect = img0.get_rect()
        self.font_img_letter_line_one_rect = img1.get_rect()
        self.font_img_letter_line_two_rect = img2.get_rect()

        # Center each Rect
        center_x = int(round(self.width / 2))
        for rect in self.font_rects():
            if rect:
                rect.centerx = center_x

        # Move to correct y
        for rect_index, rect in enumerate(self.font_rects()):
            if rect:
                if rect_index == 0:
                    y_value = self.spacing
                else:
                    # y_value just below the bottom of the last object
                    y_value = self.font_rects()[rect_index - 1].bottom + self.spacing

                rect.top = y_value

    def update(self, new_learned_character: str = ""):
        """
        Updates the letters learned list

        If no new learned character is provided, then the fonts images are
        simply redrawn.

        This is designed to run in thread

        :param new_learned_character: str of the character learned
        :return: None
        :raises ValueError: if letter already in learned letters list
        """
        if new_learned_character in self.learned_letters:
            raise ValueError("Letter already in learned letters list")

        if new_learned_character:
            self.learned_letters.append(new_learned_character)

            self.font_colour_count = self.font_colour_new_letter
            self.create_font_images()
            self.render_on_surface()

            time.sleep(0.5)

            self.font_colour_count = self.font_colour_normal
            self.create_font_images()
            self.render_on_surface()

        else:
            self.create_font_images()
            self.render_on_surface()


class MorseTrainer:
    """
    Main class for morse code trainer game
    """
    window_width = 500
    window_height = 500

    # Amount of time to input the character before it's an error
    time_to_guess_character = 1

    # The index of the character based on the number of times the player had
    # got it right consecutively.
    new_indices = [3, 4, 6, 8]

    # Ideal length of the main queue
    main_queue_length = 8

    paused_text_distance_from_bottom = 30

    def __init__(self):
        # Pygame initialisation
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode(size=(self.window_width, self.window_height))
        self.box = Box()
        self.box_thread: Thread | None = None
        self.letters_learned = LettersLearned(self.window_width)

        self.need_new_character = False
        self.correct_char = ""

        # Queues for what characters to add
        self.back_character_queue: list[str] = []
        self.main_character_queue: list[tuple[str, int]] = []

        # Work out location to draw the middle box
        mid_point = (self.window_width / 2, self.window_height / 2)
        offset = self.box.box_width / 2
        self.box_location = (mid_point[0] - offset, mid_point[1] - offset)

        self.paused_font = pygame.font.SysFont(font_name, size=30)

        self.paused_text = self.get_paused_text("")

    def get_paused_text(self, text) -> pygame.Surface:
        """
        Render some text onto a surface
        """
        return self.paused_font.render(text,
                                       True,
                                       (255, 255, 255),
                                       (0, 0, 0))

    def generate_character_queue(self):
        """
        Generates the character queue that will be used to train the player.

        Sets this value to self.back_character_queue

        Back queue is a list of character ordered by how long it takes to key
        them.

        Also set's up the main character queue
        """
        characters = list(morse.keys())
        self.back_character_queue = []

        letters = [c for c in characters if c.isalpha()]
        numbers = [c for c in characters if c.isdigit()]

        for character_set in (letters, numbers):
            lengths_dict: dict[int, list[str]] = {}
            for char in character_set:
                char_morse_length = morse_length(char)

                if char_morse_length in lengths_dict:
                    lengths_dict[char_morse_length].append(char)
                else:
                    lengths_dict[char_morse_length] = [char]

            lengths_list = list(lengths_dict.items())
            lengths_list.sort(key=lambda x: x[0])

            to_add_to_queue = []
            for length, letters in lengths_list:
                random.shuffle(letters)
                to_add_to_queue.extend(letters)

            self.back_character_queue.extend(to_add_to_queue)

        self.get_next_char()

    def is_playing(self) -> bool:
        """
        Return if there is something that is playing right now. Either morse,
        or flashes correct or error. Player input shouldn't be recorded while
        is_playing is True
        """
        return self.box_thread and self.box_thread.is_alive()

    def set_box_thread(self, target, args: tuple = None):
        """
        Set's the box thread up and starts it.

        Use this function to call the play functions from self.box
        """
        if args:
            self.box_thread = Thread(target=target, args=args)
        else:
            self.box_thread = Thread(target=target)

        self.box_thread.start()

    def add_character_to_main_queue(self):
        """
        Adds a character from the back queue to the back of the main queue.

        Adds a random character from the first 3 of the back queue

        :raises ValueError: if self.back_character_queue is empty
        """
        if len(self.back_character_queue) == 0:
            raise ValueError("Back character queue is empty")

        to_add = random.choice(self.back_character_queue[:3])
        self.main_character_queue.append((to_add, 0))
        self.back_character_queue.remove(to_add)

    def get_next_char(self):
        """
        Gets the next character to play.

        Adjusts the main queue by adding characters to it if necessary or
        possible to make the main queue the ideal length

        :raises ValueError: if queue is empty
        """

        while len(self.main_character_queue) < self.main_queue_length and self.back_character_queue:
            self.add_character_to_main_queue()

        if self.main_character_queue:
            return self.main_character_queue[0][0]
        else:
            raise ValueError("Queue empty")

    def is_queue_empty(self):
        """
        Returns if there are no more letters to select, and the game can end
        """
        return len(self.back_character_queue) + len(self.main_character_queue) == 0

    def update_queue(self, correct: bool):
        """
        Updates the queue if the character was correct

        If the new index is larger than the length of the queue, character
        gets appended onto the end.

        If the number of correct guesses in a row is too large for a new index,
        then pops the element off queue

        :raises ValueError: if queue is empty
        """
        item = self.main_character_queue[0]
        if correct:
            new_item = (item[0], item[1] + 1)
        else:
            new_item = (item[0], 0)

        self.main_character_queue.pop(0)

        if new_item[1] < len(self.new_indices):
            new_item_index = self.new_indices[new_item[1]]
            self.main_character_queue.insert(new_item_index, new_item)
        else:
            Thread(target=self.letters_learned.update, args=(item[0],)).start()

    def pause(self):
        """
        Pauses the game
        """
        print("Paused")
        self.need_new_character = True
        self.box.paused.set()

        self.box.reset_box()

        self.paused_text = self.get_paused_text("Paused")

        self.draw_elements()

        while True:
            for event in pygame.event.get():
                if event.type == locals.KEYDOWN:
                    if event.key == locals.K_ESCAPE:
                        print("Unpause")

                        self.box.paused.clear()
                        self.paused_text = self.get_paused_text("")
                        self.draw_elements()

                        return

                if event.type == locals.QUIT:
                    pygame.quit()
                    print("Quit")
                    quit(0)

            self.draw_elements()

    def draw_elements(self):
        """
        Draws the elements on the screen and updates the display
        """
        self.screen.fill((0, 0, 0))

        # Draw the box in the middle of the screen
        self.screen.blit(source=self.box.surf, dest=self.box_location)

        # Draw the letters learned at the top
        self.screen.blit(source=self.letters_learned.surf, dest=(0, 0))

        # Draw the paused text
        paused_location = self.paused_text.get_rect()

        paused_location.centerx = self.screen.get_rect().centerx
        paused_location.bottom = self.window_height - self.paused_text_distance_from_bottom

        self.screen.blit(source=self.paused_text, dest=paused_location)

        pygame.display.flip()

    def start(self):
        """
        Main game loop
        """

        time.sleep(0.5)

        self.need_new_character = True

        self.generate_character_queue()

        # Time when the box stopped playing the morse character
        stopped_playing_time = None

        while True:

            # Play the next character to guess
            if self.need_new_character and not self.is_playing():
                if self.main_character_queue:
                    self.correct_char = self.get_next_char()

                    # Play the morse code in a thread
                    self.set_box_thread(self.box.play_morse, (self.correct_char,))

                    self.need_new_character = False

                else:
                    pygame.quit()
                    quit(0)

            if stopped_playing_time is None and not self.is_playing():
                # The box has just stopped playing

                stopped_playing_time = time.time()

            self.draw_elements()

            # Handle events:  key presses and others
            for event in pygame.event.get():

                if not self.is_playing() and event.type == locals.KEYDOWN:
                    char_of_key: str = event.unicode
                    if char_of_key.isalnum():
                        # Key pressed is an alphanumeric key (0-9, a-z)

                        time_taken = time.time() - stopped_playing_time
                        stopped_playing_time = None

                        character_correct = char_of_key.upper() == self.correct_char
                        too_slow = self.time_to_guess_character < time_taken

                        # Player got it wrong
                        if not character_correct:
                            self.set_box_thread(self.box.play_error, args=(self.correct_char, False))

                        # Player got it right, but was too slow
                        elif too_slow:
                            self.set_box_thread(self.box.play_error, args=(self.correct_char, True))

                        # Player got it right
                        else:
                            self.set_box_thread(self.box.play_correct)

                        self.update_queue(character_correct and not too_slow)
                        self.need_new_character = True

                if event.type == locals.KEYDOWN and event.key == locals.K_ESCAPE:
                    # Esc key pressed after the thing has played. Pause the game.
                    self.update_queue(correct=False)
                    stopped_playing_time = None

                    # Function returns when user unpauses
                    self.pause()

                    time.sleep(1)

                if event.type == locals.QUIT:
                    pygame.quit()
                    print("Quit")
                    return

    def debug(self):
        """
        Testing function
        """
        pass


if __name__ == "__main__":
    debug = False

    if debug:
        print("*" * 50 + " DEBUG! " + "*" * 50)

        t = MorseTrainer()
        t.debug()

    else:
        t = MorseTrainer()
        t.start()
