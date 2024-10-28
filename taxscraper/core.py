import pandas as pd
from tqdm import tqdm
import counties

import tkinter
from tkinter import ttk

import sv_ttk

root = tkinter.Tk()

button = ttk.Button(root, text="Click me!")
button.pack()

# This is where the magic happens


root.mainloop()


  
import tkinter as tk       
from tkinter import ttk
import sv_ttk

class Application(tk.Frame):              
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)   
        self.grid()                       
        self.createWidgets()

    def createWidgets(self):
        self.quitButton = tk.Button(self, text='Quit',
            command=self.quit)            
        self.quitButton.grid()            
sv_ttk.set_theme("light")

app = Application()                       
app.master.title('Scrapinator')    
app.mainloop()       


parcelList = ['18 124 01 006',
              '18 124 01 011',
              '18 124 01 111',
              '18 124 01 112',
              '18 124 02 003',
              '18 124 02 004',
              '18 124 02 005',
              '18 124 02 006',
              '18 124 03 001',
              '18 125 01 003',]

return_df = pd.DataFrame()

for parcel in tqdm(parcelList):
    return_df = pd.concat([return_df, counties.scrape_data(parcel, "dekalb")])
print(return_df)
return_df.to_csv
