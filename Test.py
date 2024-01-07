import tkinter as tk
from tkinter import *

root = tk.Tk()
root.geometry("1000x500")

# add widget
Label(root, text="Count Setting", font=('Tomato', 20, 'bold')).pack(pady=10)

# --- Connect to Database
DB_Labelframe = LabelFrame(root, text="Connect to MongoDB Database")
DB_Labelframe.pack(padx=10, pady=10)

Label(DB_Labelframe, text="Database").grid(row=0, column=0)
DB_entry = Entry(DB_Labelframe, width=50)
DB_entry.insert(END, "mongodb+srv://thirawat:1234@cluster0.1h6mdye.mongodb.net/?retryWrites=true&w=majority")
DB_entry.grid(row=1, column=1)
connect_DB = Button(DB_Labelframe, text="Connect")
connect_DB.grid(row=1, column=2, padx=10)
status_DB = Label(DB_Labelframe, text="status : OK")
status_DB.grid(row=2, column=1, sticky="w")

# --- Mask Setting
Mask_setting = LabelFrame(root, text="Select a mask for counting")
Mask_setting.pack(padx=10, pady=10)

# Image location (add "/" not "\")
img = PhotoImage(file="SourceData/maskSetting.png")

pathMask = StringVar()
r1 = Radiobutton(Mask_setting, image=img, variable=pathMask, value="SourceData/maskSetting.png")
r1.pack()
root.mainloop()