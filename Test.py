#
# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
#
# uri = "mongodb+srv://thirawat:1234@cluster0.1h6mdye.mongodb.net/?retryWrites=true&w=majority"
#
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
#
# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

import tkinter as tk
from tkinter import *
from tkinter import messagebox


def clicked():
    r = tk.messagebox.askyesno('C', 'you want fuck me!')
    print(r)


root = tk.Tk()
Button(root, text="Click", command=lambda: clicked()).pack()
root.mainloop()
