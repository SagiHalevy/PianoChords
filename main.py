#this program fetch data from an online website, the website may change anytime which will make some of the links irrelevant
import requests
from urllib import request
from tkinter import*
from PIL import ImageTk, Image
from os.path import exists
from bs4 import BeautifulSoup
import re
import json


#Create dictionary of (CHORD_NAME : CHORD_IMAGE_NAME), [after first run, dictionary is saved on computer]
def createChordsDict():
    if exists('ChordsDictionary.txt'):
        with open('ChordsDictionary.txt','r') as f:
            chordsDict = json.loads(f.read())
    else:
        allNotes = ['c','c-sharp','d','d-sharp','e','f','f-sharp','g','g-sharp','a','a-sharp','b']
        images = []
        for note in allNotes:
            url = 'https://www.pianochord.org/'+note+'-filter.html'
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            images += soup.findAll('img')

        #create dictionary between chord name and the name of its image
        chordsDict = {}
        for image in images:
            chordsDict[image['alt']] = re.search('images/(.*).png', image['src']).group(1)

        #save the dictionary on the computer to avoid fetching data every new run.
        with open('ChordsDictionary.txt', 'w') as f:
            f.write(json.dumps(chordsDict))

    createTxtChordsFile(chordsDict.keys())
    return chordsDict


#Creating a txt file with chords names (Chords names are taken from the 'alt' attributes from the website)
def createTxtChordsFile(chords):
    if not exists('chordstxt.txt'):
        with open('chordstxt.txt', 'w') as f:
            for chord in chords:
               f.write(chord+"\n")


#Load the selection-list in chords names that listed in txt file
def getChordsFromFile():
    with open("chordstxt.txt",'r') as chordsFile:
         chords = chordsFile.read().splitlines()
    return chords


#Gets chords name and downloads the chord image
def downloadChord(chord):
    if exists('downloadedChordImages/'+chord+'.png'):
        return Image.open('downloadedChordImages/'+chord+'.png')
    try:
        url = "https://www.pianochord.org/images/"+chord+".png"
        request.urlretrieve(url, 'downloadedChordImages/'+chord+".png")
        return Image.open('downloadedChordImages/'+chord+'.png')
    except Exception:
        print("Couldn't find chord")


#Show the chord image according to the selection-box
def showChord(event):
    #show selected chord on the search box
    searchChordBox.delete(0,END)
    searchChordBox.insert(0,chordsListBox.get(ANCHOR))

    #gets the chord image
    img = downloadChord(chordsDict[searchChordBox.get()])
    if not img: # if chord is not found, return
        return
    chordImage = ImageTk.PhotoImage(img)
    #update the selected chord image in the label
    chordImageLabel.configure(image=chordImage)
    chordImageLabel.image = chordImage
    chordImageLabel.place(relx=0.5, rely=0.8, anchor=CENTER)


#Gets list of chords and show them on selection-list
def updateChordList(chords):
    chordsListBox.delete(0,END)
    for chord in chords:
        chordsListBox.insert(END,chord)

#Update the selection-list upon searching with the selection-box
def updateSearchList(event):
    typed = searchChordBox.get()
    if not typed:
        data = chords
    else:
        data = []
        for chord in chords:
            if typed.lower() in chord.lower():
                data.append(chord)
    updateChordList(data)






chordsDict = createChordsDict()



root = Tk()
root.title("Piano Chords")
root.geometry("500x400")

mainFrame = Frame(root)
mainFrame = Frame(root, width=500, height = 500)
mainFrame.pack()

scrollbar = Scrollbar(mainFrame)
scrollbar.pack(side=RIGHT, fill=Y)

#create the list of chords
chordsListBox = Listbox(mainFrame)

chordsListBox.pack(side=LEFT, fill="both",expand=True)

scrollbar.config(command=chordsListBox.yview)
chordsListBox.config(yscrollcommand=scrollbar.set)



#create a label for the chord images
chordImageLabel = Label(root)

# #create the search box

searchChordBox = Entry(root)
searchChordBox.place(relx = 0.5, rely = 0.1, anchor=CENTER)




chordsListBox.bind('<<ListboxSelect>>',showChord)
mainFrame.place(relx = 0.375, rely = 0.15)


chords = getChordsFromFile()
updateChordList(chords)


searchChordBox.bind("<KeyRelease>", updateSearchList)





root.mainloop()
