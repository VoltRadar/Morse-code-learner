# Morse-code-learner
Pygame module to help teach you morse code

## Summary

This is a small program, made using the pygame
module, that is designed to teach you what each
morse code character sounds like.

It's a project
I've thought about for a while, as I found
recourses to learn morse code not great when it
comes to being able to 'decode' it at speed.

## Setup

Install Python 3 if you haven't already. This was
developed using 3.10, but versions greater than
3.2 should be fine.

Install pygame using by running `pip install -r 
requirements.txt` from the command line. This can
be done inside a virtual environment

Then you can use `python main.py` and a window
with a square with a white border on a black
background should appear.

## Gameplay

I'm stretching the definition of game in this
document.

A series of tones will play, which will be either
short or long tones. These are dots and dashes
that make up morse code.

You have a limited amount of time to press the
letter or number on the keyboard that the
series of tones represents. So if the tones are
a short sound, then a long sound, you have to
press the A key.

If you press the key in time, then the square
boarder will flash green. If you're too slow then
it'll turn orange and repeat what it should sound
like. A similar thing happens when you get it
wrong

If you get the character correct enough times in
a row then you'll have learned that character and
the program will show you new ones

This repeats until you've learned all the
characters

## Tone credit

This project contains a sound that was generated
with
[this online tool](https://onlinetonegenerator.com/).
I've found it very useful. Check it out!

## License note

`main.py` and this README are both licenced
under the MIT licence in this project. Pygame is
licenced under LGPL, and no modifications have
been made to it.

The license for the `tone.wav` is slightly
unclear to me. I'm assuming that the creators of
onlinetonegenerator.com would be fine with you
using and distributing with your projects,
especially with credit. Although I would contact
them to make sure if it really matters to you.