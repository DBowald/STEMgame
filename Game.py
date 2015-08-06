"""
Program to provide a front end for the Canfield 2015 STEM camp game.

Notes on using this code:
- In the Serial.serial() command, you must change the COM port to match
whichever port the arduino is connected to
- Make sure you have all the extra python modules downloaded, including
    pySerial
    PIL
    pygame
    tkinter
- Make sure the rate at which the arduino sends data doesn't outpace the rate
at which the updatePoints() function recursively calls itself, or else the
serial data buffer will get backed up and the program will not work correctly.
"""

__author__ = 'bowald'

from tkinter import *
import tkinter
from PIL import Image, ImageTk
import time
import serial
import functools
import random
import pygame

import os
import sys
import subprocess

"""
Create and initialize all the variables that are used globally within the
program, for timing, scoring, and musical purposes.

startTime: Time when the program begins, used to see how much time has passed.
currTime: How much time has elapsed on the clock (2:00 - curr time gives the clock time)
sithPoints: Total points the sith currently have
jediPoints: Total points the jedi currently have
musicOn: Defines whether or not music should be currently playing.
pylon#- Stores whether the pylon is currently on or off
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
global flash
flash = 0
global winner

global pylon1
pylon1 = 'N'
global pylon2
pylon2 = 'N'
global pylon3
pylon3 = 'N'
global pylon4
pylon4 = 'N'
global pylon5
pylon5 = 'N'
global blueTotalPylons
blueTotalPylons = 0
global redTotalPylons
redTotalPylons = 0

global blueLaser1
blueLaser1 = False
global blueLaser2
blueLaser2 = False
global redLaser1
redLaser1 = False
global redLaser2
redLaser2 = False

global redGarage
redGarage = False
global blueGarage
blueGarage = False

global auton
auton = False

musicLibrary = {1:"Cantina.mp3", 2: "DuelOfTheFates.mp3", 3: "ImperialAttack.mp3",
                4:"MainTheme.mp3", 5:"MoistureFarm.mp3"}

soundLibrary = {0:"airhorn.wav", 1: "alerted.wav", 2:"chewy_roar.wav", 3: "disturbence.wav", 4:"dontlike.wav", 5:"your_father.wav",
                6: "fly1.wav", 7:"fly2.wav", 8: "fly3.wav", 9:"force.wav", 10:"forceisstrong.wav",
                11: "forcestrong.wav", 12:"hansolo_badfeeling.wav", 13: "hansolo_situation.wav", 14:"learn.wav", 15:"luke_junk.wav",
                16: "r2-d2.wav", 17:"R2d2.wav", 18: "R2D2-do.wav", 19:"R2D2-hey-you.wav", 20:"R2D2-yeah.wav",
                21: "r2d2_01.wav", 22:"saberon.wav", 23: "swclear.wav", 24:"swfaith.wav", 25:"swluke01.wav",
                26: "swnotry.wav", 27:"swvader01.wav", 28: "swvader02.wav", 29:"technical.wav", 30:"your_father.wav", 31:"yodalaughing.wav"}
"""
Class to initialize and create the GUI
"""
class Game(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("IN A GALAXY (NOT SO) FAR, FAR AWAY...")
        self.pack(fill=BOTH, expand=1)

    def onclick(self):
        pass

"""
Computes the time to display on the clock, and stops/starts the clock
depending on whether the run flag is set.
"""
def update_clock():
    global run
    global currTime
    global startTime

    if(run):
        """now is how many seconds are left on the clock
        time.time() is current ticks, subtracted from the last time
        the start button was pressed, plus whatever time we are at
         on the clock"""
        now = int(121 - ((time.time() - startTime) + currTime))
        if (now != 0):
            minutes = int(now/60)
            seconds = now - (minutes*60)
            clock.configure(text=str(minutes) + " : " + str(seconds).zfill(2))
            root.after(1000, update_clock)
            #After updating the clock, make a recursive call 1000ms later to update again.
        else:
            clock.configure(text="GAME OVER")
            run = False
            ser.write(b'3')
            makeSound(3)
            scoreEndgame()
            DeclareVictor()
    else: #If not running currently, check back in 200ms
        root.after(200, update_clock)

def update_auton_clock():
    global run
    global currTime
    global startTime
    global auton
    auton = True

    if(run):
        """now is how many seconds are left on the clock
        time.time() is current ticks, subtracted from the last time
        the start button was pressed, plus whatever time we are at
         on the clock"""
        now = int(20 - ((time.time() - startTime) + currTime))
        if (now != 0):
            minutes = int(now/60)
            seconds = now - (minutes*60)
            clock.configure(text=str(minutes) + " : " + str(seconds).zfill(2))
            root.after(1000, update_auton_clock)
            #After updating the clock, make a recursive call 1000ms later to update again.
        else:
            global blueLaser1
            global blueLaser2
            global redLaser1
            global redLaser2
            blueLaser1 = False
            blueLaser2 = False
            redLaser1 = False
            redLaser2 = False
            clock.configure(text="2:00")
            currTime = 0
            startTime = time.time()
            ser.write(b'2')
            makeSound(2)
            auton = False

            update_clock()
    else: #If not running currently, check back in 200ms
        root.after(200, update_auton_clock)



"""
Runs a routine to update the scores of each team.
"""
def scorePylons(pylon, captor):
    if(run):
        global sithPoints
        global jediPoints
        global redTotalPylons
        global blueTotalPylons
        if(captor == 'B' and pylon != 'B'):
            jediPoints += 20
            blueTotalPylons += 1
            if(pylon == 'R'):
                redTotalPylons -= 1
        elif(captor == 'R' and pylon != 'R'):
            sithPoints += 20
            redTotalPylons += 1
            if(pylon == 'B'):
                blueTotalPylons -= 1
        else:
            pass

        updatePoints()


"""
Sets the run flag to True (start) or False(stop), and changes the button text
and background to match. Also helps keep track of time.
"""
def StartStop():
    global run
    global startTime
    global currTime
    global musicOn

    if(startButton["text"] == "Start"):
        run = True
        if(musicOn):
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.play()
        startButton.configure(text="Stop", bg="red")
        startTime = time.time() #Set a new start time
        ser.write(b'4')
        if(currTime == 0):
            ser.write(b'1')
        musicOn = True

    else:
        run = False
        pygame.mixer.music.pause()
        startButton.configure(text="Start",bg="green")
        currTime = int((time.time() - startTime) + currTime)
        #Saves the elapsed time, so that the timer can still work
        # even after being stopped for awhile.
        ser.write(b'5')




def DeclareVictor():
    global jediPoints
    global sithPoints
    global winner
    if(jediPoints > sithPoints):
        clock.configure(text="JEDI WIN!", fg="blue")
        winner = "Jedi"
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.load("JediVictory.mp3")
        pygame.mixer.music.play()
        FlashText()

    elif(jediPoints < sithPoints):
        clock.configure(text="SITH WIN!", fg = "red")
        winner = "Sith"
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.load("ImperialMarch.mp3")
        pygame.mixer.music.play()
        FlashText()
    else:
        clock.configure(text="TIE!")

def FlashText():
    global flash
    global winner
    if(flash):
        if(winner == "Jedi"):
            JediText.configure(fg = "black")
            flash = 0
            root.after(700,FlashText)
        else:
            SithText.configure(fg = "black")
            flash = 0
            root.after(700,FlashText)
    else:
        if(winner == "Jedi"):
            JediText.configure(fg = "blue")
            flash = 1
            root.after(700, FlashText)
        else:
            SithText.configure(fg = "red")
            flash = 1
            root.after(700, FlashText)

def ReadInSerial():
    if(run):
        command = ser.readline()
        if(len(command) == 3):
            if(command[0]) == 0: #Open doors (written TO arduino)
                pass
            if(command[0] == 1): #Begin auton/match(written TO arduino as soon as start button is first pressed)
                pass
            elif(command[0] == 2): #Begin manual(written TO arduino right after auton ends)
                pass
            elif(command[0] == 3): #End of game(written TO arduino right before the victor is declared)
                pass
            elif(command[0] == 4): #Start(written TO arduino whenever GUI button is pressed)
                pass
            elif(command[0] == 5): #Stop(written TO arduino whenever GUI button is pressed)
                pass
            elif(command[0] == 6): #Scoring the pylons at the end
                pass
            elif(command[0] == 14): #write open blue doors
                pass
            elif(command[0] == 15): #write red doors open
                pass
            else:
                pass
        elif(len(command) == 4):
            if(command[1] == 7): #Control of Pylon1 has changed
                global pylon1
                makeSound(7)
                scorePylons(pylon1,chr(command[0]))
                pylon1 = chr(command[0])
            elif(command[1] == 8): #Control of Pylon2 has changed
                global pylon2
                makeSound(8)
                scorePylons(pylon2,chr(command[0]))
                pylon2 = chr(command[0])
            elif(command[1] == 9): #Control of Pylon3 has changed
                global pylon3
                makeSound(9)
                scorePylons(pylon3,chr(command[0]))
                pylon3 = chr(command[0])
            elif(command[1] == 10): #Control of Pylon4 has changed
                global pylon4
                makeSound(10)
                scorePylons(pylon4,chr(command[0]))
                pylon4 = chr(command[0])
            elif(command[1] == 11): #Control of Pylon5 has changed
                global pylon5
                makeSound(11)
                scorePylons(pylon5,chr(command[0]))
                pylon5 = chr(command[0])
            elif(command[1] == 12):
                makeSound(12)
                scoreLaser1(chr(command[0]))
            elif(command[1] == 13):
                makeSound(13)
                scoreLaser2(chr(command[0]))
        root.after(1000, ReadInSerial)
    else:
        root.after(1000, ReadInSerial)

def garagePoints(team):


def updateGarage():
    if(run):
        if(blueTotalPylons >= 3):
            garagePoints('B')
            blueGarage
        else:
            pass
        elif(redTotalPylons >= 3):
            garagePoints('R')

def scoreEndgame():
    global jediPoints
    global sithPoints
    POINTS = 40
    if(pylon1 == 'B'):
        jediPoints += POINTS
    elif(pylon1 == 'R'):
        sithPoints += POINTS
    if(pylon2 == 'B'):
        jediPoints += POINTS
    elif(pylon2 == 'R'):
        sithPoints += POINTS
    if(pylon3 == 'B'):
        jediPoints += POINTS
    elif(pylon3 == 'R'):
        sithPoints += POINTS
    if(pylon4 == 'B'):
        jediPoints += POINTS
    elif(pylon4 == 'R'):
        sithPoints += POINTS
    if(pylon5 == 'B'):
        jediPoints += POINTS
    elif(pylon5 == 'R'):
        sithPoints += POINTS
    updatePoints()

def updatePoints():
    SithText.configure(text="SITH\n" + str(sithPoints))
    JediText.configure(text="JEDI\n" + str(jediPoints))

def makeSound(event):
    if(event >= 7 and event <= 11):
        randNum = random.randrange(1,12)
        file = "soundboard_game/" + soundLibrary.get(randNum)
        sound = pygame.mixer.Sound(file)
        sound.play()
    elif(event >= 1 and event <= 3):
        file = "soundboard_game/" + soundLibrary.get(0)
        sound = pygame.mixer.Sound(file)
        sound.play()
    elif(event == 12 or event == 13):
        sound = pygame.mixer.Sound("LaserInterrupt.wav")
        sound.play()

def initSound():
    randNum = random.randrange(1,6)
    file = musicLibrary.get(randNum)
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(file)

def scoreLaser1(team):
    global auton
    global blueLaser1
    global redLaser1

    global jediPoints
    global sithPoints

    if(auton):
        if(team == 'B'):
           if(blueLaser1 == False):
                jediPoints += 20
                blueLaser1 = True
                ser.write(b'14')

        elif(team == 'R'):
            if(redLaser1 == False):
                sithPoints += 20
                redLaser1 = True
                ser.write(b'15')
    else:
        if(team == 'B'):
            if(blueLaser1 == False):
                jediPoints += 200
                blueLaser1 = True
        elif(team == 'R'):
            if(redLaser1 == False):
                sithPoints += 200
                redLaser1 = True

def scoreLaser2(team):
    global auton
    global blueLaser2
    global redLaser2

    if(auton):
        if(team == 'B'):
           if(blueLaser2 == False):
                jediPoints += 100
                blueLaser2 = True
        elif(team == 'R'):
            if(redLaser2 == False):
                sithPoints += 100
                redLaser2 = True

#Define a tkinter GUI frame, get the screen resolution, then use it to set the size of the GUI.
root = tkinter.Tk()

#subprocess.call(['soundboard_game/turretted.sh'])

#Read in data from the serial port- '/dev/tty should be changed to whatever
#  COM port you plan on using
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(str (screen_width) + "x" + str (screen_height))

#Set the GUI frame
app = Game(root)

#Open and set the background image
im = Image.open('star_wars_img.jpg')
im = im.resize((screen_width, screen_height), Image.ANTIALIAS)
tkimage = ImageTk.PhotoImage(im)
pic=tkinter.Label(root,image = tkimage)
pic.place(x=0, y=0, relwidth=1, relheight=1)

#Ratio to help resize the GUI parts to fit the screen size
ratio = (screen_height*screen_width)/(768*1366)

#Initialize the clock
clock = Label(root, text="0 : 20", bg = "black", fg = "purple", font ="FranklinGothic " + str(int(50*ratio)) + " bold")
clock.pack()
clock.place(y = 1.2*screen_height/4, x = .8*screen_width/2)

#Initialize the start/stop button
startButton = Button(root, text="Start", command=StartStop, bg = "green", highlightthickness=0, font = "Times " + str(int(20*ratio)))
startButton.pack
startButton.place(x=screen_width/2, y=.9*screen_height/2)

#Initialize the Sith point counter
SithText = Label(root, text="SITH\n0", bg = "black", fg = "red", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
SithText.pack()
SithText.place(y = screen_height/8, x = screen_width/8)

#Initialize the Jedi point counter
JediText = Label(root, text="JEDI\n0", bg = "black", fg = "BLUE", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
JediText.pack()
JediText.place(y = screen_height/8, x = 6*screen_width/8)

#Start all the routines
update_auton_clock()
initSound()
ReadInSerial()
root.mainloop()