import tkinter as tk
from tkinter import *


root = tk.Tk()
chev = IntVar()
cb1 = Checkbutton(root, text="Use Video example",variable=chev, offvalue=0, onvalue=1)
cb1.pack()

# Create a button to check the value of chev
check_button = Button(root, text="Check chev value", command=lambda: print(chev.get()))
check_button.pack()

root.mainloop()
