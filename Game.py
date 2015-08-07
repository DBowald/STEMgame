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

global pylon1CD
pylon1CD = False
global python2CD
pylon2CD = False
global python3CD
pylon3CD = False
global python4CD
pylon4CD = False
global python5CD
pylon5CD = False

global redGarage
redGarage = False
global blueGarage
blueGarage = False

global auton
auton = False

global bluePenalty
bluePenalty = 0

global redPenalty
redPenalty = 0

global redLaserCount
redLaserCount = 0
global blueLaserCount
blueLaserCount = 0

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
            global blueLaserCount
            global redLaserCount
            blueLaserCount = 0
            redLaserCount = 0
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
def scorePylons(pylon, pylonNum, captor):
    if(run):
        global sithPoints
        global jediPoints
        global redTotalPylons
        global blueTotalPylons
        if(captor == 'B' and pylon != 'B'):
            if(pylonNum == 1):
                jediPoints += 3
            if(pylonNum == 2):
                jediPoints += 5
            if(pylonNum == 3):
                jediPoints += 4
            if(pylonNum == 4):
                jediPoints += 7
            if(pylonNum == 5):
                jediPoints += 7

            blueTotalPylons += 1
            if(pylon == 'R'):
                redTotalPylons -= 1
        elif(captor == 'R' and pylon != 'R'):
            if(pylonNum == 1):
                sithPoints += 3
            if(pylonNum == 2):
                sithPoints += 5
            if(pylonNum == 3):
                sithPoints += 4
            if(pylonNum == 4):
                sithPoints += 7
            if(pylonNum == 5):
                sithPoints += 7

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
        print(command)
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
            elif(command[0] == 14): #write open blue doors start
                pass
            elif(command[0] == 15): #write red doors open start
                pass
            elif(command[0] == 16): #write open blue doors end
                pass
            elif(command[0] == 17): #write red doors open end
                pass
            elif(command[0] == 18): #write open blue doors start
                pass
            elif(command[0] == 19): #write red doors open start
                pass
            elif(command[0] == 20): #write open blue doors end
                pass
            elif(command[0] == 21): #write red doors open end
                pass
            elif(command[0] == 22):
                pass
            elif(command[0] == 23):
                pass
            elif(command[0] == 24):
                pass
            elif(command[0] == 25):
                pass
            elif(command[0] == 26):
                pass
            else:
                pass
        elif(len(command) == 4):
            if(command[1] == 7): #Control of Pylon1 has changed
                global pylon1CD
                if(not pylon1CD):
                    global pylon1
                    makeSound(7)
                    scorePylons(pylon1,1,chr(command[0]))
                    pylon1 = chr(command[0])
                    pylon1CD = True
                    CDPylon1()
                    root.after(10000, resetPylon1CD)

            elif(command[1] == 8): #Control of Pylon2 has changed
                print("made it here")
                global pylon2CD
                if(not pylon2CD):
                    global pylon2
                    makeSound(8)
                    scorePylons(pylon2,2,chr(command[0]))
                    pylon2 = chr(command[0])
                    pylon2CD = True
                    CDPylon2()
                    root.after(10000, resetPylon2CD)
            elif(command[1] == 9): #Control of Pylon3 has changed
                global pylon3CD
                if(not pylon3CD):
                    global pylon3
                    makeSound(9)
                    scorePylons(pylon3,3,chr(command[0]))
                    pylon3 = chr(command[0])
                    pylon3CD = True
                    CDPylon3()
                    root.after(10000, resetPylon3CD)
            elif(command[1] == 10): #Control of Pylon4 has changed
                global pylon4CD
                if(not pylon4CD):
                    global pylon4
                    makeSound(10)
                    scorePylons(pylon4,4,chr(command[0]))
                    pylon4 = chr(command[0])
                    pylon4CD = True
                    root.after(10000, resetPylon4CD)
                    CDPylon4()
            elif(command[1] == 11): #Control of Pylon5 has changed
                global pylon5CD
                if(not pylon5CD):
                    global pylon5
                    makeSound(11)
                    scorePylons(pylon5,5,chr(command[0]))
                    pylon5 = chr(command[0])
                    pylon5CD = True
                    CDPylon5()
                    root.after(10000, resetPylon5CD)
            elif(command[1] == 12):
                makeSound(12)
                scoreLasers(chr(command[0]))
        root.after(1, ReadInSerial)
    else:
        root.after(1, ReadInSerial)

def updateGarage():
    global redGarage
    global blueGarage
    global blueTotalPylons
    global redTotalPylons
    if(run):
        if(blueTotalPylons >= 3 and (not blueGarage)):
            startOpenBlueGarage()
            root.after(300,endOpenBlueGarage)
            blueGarage = True
        elif(redTotalPylons >= 3 and (not redGarage) ):
            startOpenRedGarage()
            root.after(300,endOpenRedGarage)
            redGarage = True
        if(blueTotalPylons < 3 and blueGarage):
            startCloseBlueGarage()
            root.after(300, endCloseBlueGarage)
            blueGarage = False
        elif(redTotalPylons < 3 and redGarage):
            startCloseRedGarage()
            root.after(300, endCloseRedGarage)
            redGarage = False

def scoreEndgame():
    global jediPoints
    global sithPoints
    POINTS = 10
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

def scoreLasers(team):
    global auton
    global blueLaserCount
    global redLaserCount
    global jediPoints
    global sithPoints


    if(auton):
        if(team == 'B'):
           blueLaserCount += 1
           blueLaserCount = blueLaserCount % 2
           if(blueLaserCount):
                jediPoints += 10
                startOpenBlueGarage()
                root.after(300, endOpenBlueGarage)
           else:
                jediPoints += 20

        elif(team == 'R'):
           startOpenRedGarage()
           redLaserCount = blueLaserCount % 2
           if(redLaserCount):
                startOpenRedGarage()
                root.after(300, endOpenRedGarage)
                sithPoints += 10
           else:
                sithPoints += 20
    else:
        blueLaserCount += 1
        blueLaserCount = blueLaserCount % 2
        if(team == 'B'):
            if(not blueLaserCount):
                if(blueGarage):
                    jediPoints += 30
                    startCloseBlueGarage()
                    root.after(300, endCloseBlueGarage)
                    root.after(10000,startOpenBlueGarage())
                    root.after(10300, endOpenBlueGarage)
        elif(team == 'R'):
            if(not redLaserCount):
                if(redGarage):
                    sithPoints += 30
                    startCloseBlueGarage()
                    root.after(300, endCloseBlueGarage)
                    root.after(10000,startOpenBlueGarage())
                    root.after(10300, endOpenBlueGarage)

def loadBlueGarage():
    global pylon1
    global pylon2
    global pylon3
    global pylon4
    global pylon5

    if(pylon1 == 'B'):
        pylon1 = 'N'
    if(pylon2 == 'B'):
        pylon2 = 'N'
    if(pylon3 == 'B'):
        pylon3 = 'N'
    if(pylon4 == 'B'):
        pylon4 = 'N'
    if(pylon5 == 'B'):
        pylon5 = 'N'

def loadRedGarage():
    global pylon1
    global pylon2
    global pylon3
    global pylon4
    global pylon5

    if(pylon1 == 'R'):
        pylon1 = 'N'
    if(pylon2 == 'R'):
        pylon2 = 'N'
    if(pylon3 == 'R'):
        pylon3 = 'N'
    if(pylon4 == 'R'):
        pylon4 = 'N'
    if(pylon5 == 'R'):
        pylon5 = 'N'

def startOpenBlueGarage():
    ser.write(b'14')

def startOpenRedGarage():
    ser.write(b'15')

def endOpenBlueGarage():
    ser.write(b'16')

def endOpenRedGarage():
    ser.write(b'17')

def startCloseBlueGarage():
    ser.write(b'18')

def startCloseRedGarage():
    ser.write(b'19')

def endCloseBlueGarage():
    ser.write(b'20')

def endCloseRedGarage():
    ser.write(b'21')

def resetPylon1():
    ser.write(b'22')

def resetPylon2():
    ser.write(b'23')

def resetPylon3():
    ser.write(b'24')

def resetPylon4():
    ser.write(b'25')

def resetPylon5():
    ser.write(b'26')

def CDPylon1():
    ser.write(b'27')

def CDPylon2():
    ser.write(b'28')

def CDPylon3():
    ser.write(b'29')

def CDPylon4():
    ser.write(b'30')

def CDPylon5():
    ser.write(b'31')

def OffCDPylon1():
    ser.write(b'27')

def OffCDPylon2():
    ser.write(b'28')

def OffCDPylon3():
    ser.write(b'29')

def OffCDPylon4():
    ser.write(b'30')

def OffCDPylon5():
    ser.write(b'31')


def resetPylon1CD():
    global pylon1CD
    pylon1CD = False
    OffCDPylon1()

def resetPylon2CD():
    global pylon2CD
    pylon2CD = False
    OffCDPylon2()

def resetPylon3CD():
    global pylon3CD
    pylon3CD = False
    OffCDPylon3()

def resetPylon4CD():
    global pylon4CD
    pylon4CD = False
    OffCDPylon4()

def resetPylon5CD():
    global pylon5CD
    pylon5CD = False
    OffCDPylon5()

"""
def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)
"""

def addBluePoint():
    global jediPoints
    jediPoints += 1
    updatePoints()

def addRedPoint():
    global sithPoints
    sithPoints += 1
    updatePoints()

def addBlue10Points():
    global jediPoints
    jediPoints += 10
    updatePoints()

def addRed10Points():
    global sithPoints
    sithPoints += 10
    updatePoints()

def penaltyBluePoint():
    global bluePenalty
    global jediPoints
    jediPoints -= 1
    bluePenalty -= 1
    updatePoints()

def penaltyRedPoint():
    global redPenalty
    global sithPoints
    redPenalty -= 1
    sithPoints -= 1
    updatePoints()

def penaltyBlue10Points():
    global bluePenalty
    global jediPoints
    bluePenalty -= 10
    jediPoints -= 10
    updatePoints()

def penaltyRed10Points():
    global redPenalty
    global sithPoints
    redPenalty -= 10
    sithPoints -= 10
    updatePoints()

def ResetBluePylons():
    global pylon1
    global pylon2
    global pylon3
    global pylon4
    global pylon5
    global blueTotalPylons

    if(pylon1 == 'B'):
        resetPylon1()
        pylon1 = 'N'
    if(pylon2 == 'B'):
        resetPylon2()
        pylon2 = 'N'
    if(pylon3 == 'B'):
        resetPylon3()
        pylon3 = 'N'
    if(pylon4 == 'B'):
        resetPylon4()
        pylon4 = 'N'
    if(pylon5 == 'B'):
        resetPylon5()
        pylon5 = 'N'

    blueTotalPylons = 0

def ResetRedPylons():
    global pylon1
    global pylon2
    global pylon3
    global pylon4
    global pylon5
    global redTotalPylons

    if(pylon1 == 'R'):
        resetPylon1()
        pylon1 = 'N'
    if(pylon2 == 'R'):
        resetPylon2()
        pylon2 = 'N'
    if(pylon3 == 'R'):
        resetPylon3()
        pylon3 = 'N'
    if(pylon4 == 'R'):
        resetPylon4()
        pylon4 = 'N'
    if(pylon5 == 'R'):
        resetPylon5()
        pylon5 = 'N'

    redTotalPylons = 0



#Define a tkinter GUI frame, get the screen resolution, then use it to set the size of the GUI.
root = tkinter.Tk()

#Read in data from the serial port- '/dev/tty should be changed to whatever
#  COM port you plan on using
ser = serial.Serial('/dev/ttyACM1', 9600, timeout=0)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(str (screen_width) + "x" + str (screen_height))

#Set the GUI frame
app = Game(root)
root.bind('<q>', addBluePoint)
root.bind('<w>', addBlue10Points)
root.bind('<e>', penaltyBluePoint)
root.bind('<r>', penaltyBlue10Points)

root.bind('<a>', addRedPoint)
root.bind('<s>', addRed10Points)
root.bind('<d>', penaltyRedPoint)
root.bind('<f>', penaltyRed10Points)

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

#Initialize the reset button
"""
startButton = Button(root, text="Restart", command=restart_program, bg = "yellow", highlightthickness=0, font = "Times " + str(int(20*ratio)))
startButton.pack
startButton.place(x=0.8*screen_width/2, y=.9*screen_height/2)
"""

#Initialize the Sith point counter
SithText = Label(root, text="SITH\n0", bg = "black", fg = "red", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
SithText.pack()
SithText.place(y = screen_height/8, x = screen_width/8)

#Initialize the Jedi point counter
JediText = Label(root, text="JEDI\n0", bg = "black", fg = "BLUE", font = "FranklinGothic "+ str(int(50*ratio)) + " bold")
JediText.pack()
JediText.place(y = screen_height/8, x = 6*screen_width/8)

#Start all the routines

updateGarage()
update_auton_clock()
initSound()
ReadInSerial()
root.mainloop()