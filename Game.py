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
            ser.write(3)
            scoreEndgame()
            DeclareVictor()
    else: #If not running currently, check back in 200ms
        root.after(200, update_clock)

def update_auton_clock():
    global run
    global currTime
    global startTime

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
            clock.configure(text="2:00")
            currTime = 0
            startTime = time.time()
            ser.write(2)
            update_clock()
           # DeclareVictor()
    else: #If not running currently, check back in 200ms
        root.after(200, update_auton_clock)



"""
Runs a routine to update the scores of each team.
"""
def scorePylons(pylon, captor):
    if(run):
        global sithPoints
        global jediPoints

        if(captor == 'B' and pylon != 'B'): #49 is '1' in ascii(python reads unicode by default)
            jediPoints += 20
        elif(captor == 'R' and pylon != 'R'): #49 is '1' in ascii(python reads unicode by default)
            sithPoints += 20
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
        #musicOn = True
        startButton.configure(text="Stop", bg="red")
        startTime = time.time() #Set a new start time
        ser.write(4)
        if(currTime == 0):
            ser.write(1)
    else:
        run = False
       # musicOn = False
        startButton.configure(text="Start",bg="green")
        currTime = int((time.time() - startTime) + currTime)
        #Saves the elapsed time, so that the timer can still work
        # even after being stopped for awhile.
        ser.write(5)

"""
|Work in progress|
"""
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
            #pygame.mixer.pause
    else:
        pygame.mixer.pause
        root.after(1000, SoundManager)




def DeclareVictor():
    global jediPoints
    global sithPoints
    global winner
    if(jediPoints > sithPoints):
        clock.configure(text="JEDI WIN!", fg="blue")
        winner = "Jedi"
        FlashText()

    elif(jediPoints < sithPoints):
        clock.configure(text="SITH WIN!", fg = "red")
        winner = "Sith"
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
        if(len(command) == 1):
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
            elif(command[1] == 6): #Scoring the pylons at the end
                pass
            else:
                pass
        elif(len(command) == 2):
            if(command[1] == 7): #Control of Pylon1 has changed
                global pylon1
                makeSound()
                scorePylons(pylon1,command[0])
                pylon1 = command[0]
            elif(command[1] == 8): #Control of Pylon2 has changed
                global pylon2
                makeSound()
                scorePylons(pylon2,command[0])
                pylon2 = command[0]
            elif(command[1] == 9): #Control of Pylon3 has changed
                global pylon3
                makeSound()
                scorePylons(pylon3,command[0])
                pylon3 = command[0]
            elif(command[1] == 10): #Control of Pylon4 has changed
                global pylon4
                makeSound()
                scorePylons(pylon4,command[0])
                pylon4 = command[0]
            elif(command[1] == 11): #Control of Pylon5 has changed
                global pylon5
                makeSound()
                scorePylons(pylon5,command[0])
                pylon5 = command[0]
        root.after(1000, ReadInSerial)
    else:
        root.after(1000, ReadInSerial)

def scoreEndgame():
    i = 1
    pylonChar = 'N'
    while(i <= 5):
        exec("pylonChar = pylon" + i)
        if(pylonChar == 'B'):
            jediPoints += 100
        elif(pylonChar == 'R'):
            sithPoints += 100
        i += 1
    updatePoints()

def updatePoints():
    SithText.configure(text="SITH\n" + str(sithPoints))
    JediText.configure(text="JEDI\n" + str(jediPoints))

def makeSound():
    randNum = random.randrange(0,31)
    f = open('/soundboard_game/soundshot', 'a')
    f.write(randNum)
    f.close()


#Define a tkinter GUI frame, get the screen resolution, then use it to set the size of the GUI.
root = tkinter.Tk()

subprocess.call(['/soundboard_game/turreted.sh'])

#Read in data from the serial port- '/dev/tty should be changed to whatever
#  COM port you plan on using
ser = serial.Serial('/dev/ttyUSB0', 9600)

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
SoundManager()
root.mainloop()