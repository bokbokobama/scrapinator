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