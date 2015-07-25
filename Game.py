__author__ = 'bowald'

from tkinter import *
import tkinter
from PIL import Image, ImageTk
import time
import serial
import random
import pygame
import os

import sys

"""
Create and initialize all the variables that are used globally within the
program, for timing, scoring, and musical purposes.

startTime: Time when the program begins, used to see how much time has passed.
currTime: How much time has elapsed on the clock (2:00 - curr time gives the clock time)
sithPoints: Total points the sith currently have
jediPoints: Total points the jedi currently have
musicOn: Defines whether or not music should be currently playing.
"""
global startTime
startTime = time.time()
global run
run = False
global currTime
currTime = 0
global sithPoints
sithPoints = 0
global jediPoints
jediPoints = 0
global musicOn
musicOn = False

global pylon1
pylon1 = 0

class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("IN A GALAXY (NOT SO) FAR, FAR AWAY...")
        self.pack(fill=BOTH, expand=1)

    def onclick(self):
        pass

def update_clock():
    global run
    global currTime
    global startTime

    if(run):
        now = 120 - ((time.time() - startTime) + currTime)
        now = int(now)
        if (now != 0):
            minutes = int(now/60)
            seconds = now - (minutes*60)
            clock.configure(text=str(minutes) + " : " + str(seconds).zfill(2))
            root.after(1000, update_clock)
        else:
            clock.configure(text="GAME OVER")
            run = False
    else:
        root.after(200, update_clock)

def updatePoints():
    if(run):
        global pylon1
        global sithPoints
        global jediPoints
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        val = ser.readline()
        print(val)
        print(chr(val[0]))
        if(val[0] == 49 and pylon1 == 0):
            pylon1 = 1
        elif(val[0] == 48 and pylon1 == 1):
            pylon1 = 0
            sithPoints += 20

        #val = random.randrange(0,11)
        #jediPoints += val
        #JediText.configure(text="JEDI\n" + str(jediPoints))
        #val = random.randrange(0,11)
        #sithPoints += val
        SithText.configure(text="SITH\n" + str(sithPoints))
        root.after(1000, updatePoints)
    else:
        root.after(1000, updatePoints)

def StartStop():
    global run
    global startTime
    global currTime

    if(startButton["text"] == "Start"):
        run = True
        startButton.configure(text="Stop", bg="red")
        startTime = time.time()
    else:
        run = False
        startButton.configure(text="Start",bg="green")
        currTime = int((time.time() - startTime) + currTime)

def SoundManager():
    global run
    if(run):
        global musicOn
        if(not musicOn):
            file = 'Cantina.mp3'
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            root.after(1000, SoundManager)
            musicOn = True
        else:
            pass
    else:
        pygame.mixer.pause
        root.after(1000, SoundManager)


root = tkinter.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(str (screen_width) + "x" + str (screen_height))

app = Example(root)

im = Image.open('star_wars_img.jpg')
im = im.resize((screen_width, screen_height), Image.ANTIALIAS)
tkimage = ImageTk.PhotoImage(im)
pic=tkinter.Label(root,image = tkimage)
pic.place(x=0, y=0, relwidth=1, relheight=1)

ratio = (screen_height*screen_width)/(768*1366)

clock = Label(root, text="2:00", bg = "black", fg = "purple", font ="FranklinGothic " + str(int(50*ratio)) + " bold")
clock.pack()
clock.place(y = 1.2*screen_height/4, x = .8*screen_width/2)

startButton = Button(root, text="Start", command=StartStop, bg = "green", highlightthickness=0, font = "Times " + str(int(20*ratio)))
startButton.pack
startButton.place(x=screen_width/2, y=.9*screen_height/2)

SithText = Label(root, text="SITH\n0", bg = "black", fg = "red", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
SithText.pack()
SithText.place(y = screen_height/8, x = screen_width/8)

JediText = Label(root, text="JEDI\n0", bg = "black", fg = "BLUE", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
JediText.pack()
JediText.place(y = screen_height/8, x = 6*screen_width/8)

update_clock()
updatePoints()
SoundManager()

root.mainloop()