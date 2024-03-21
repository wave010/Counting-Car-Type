import tkinter as tk
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter.ttk import Combobox
from tkinter import filedialog
from tracker import *
from ultralytics import YOLO
import cv2
import cvzone
import pandas as pd
from datetime import datetime
import re
import pymongo
from configparser import ConfigParser
# ---------------------------------------------------
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# ---------------------------------------------------

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Counting Car Type Project")

        # Crate config setting
        self.config = ConfigParser()
        self.config.read("Setting/config.ini")

        # Model
        self.model = YOLO('YOLOModel/CarType_model.pt')

        # Create a container to hold the pages
        self.container = tk.Frame(root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Dictionary to store different pages
        self.pages = {}

        # Create and add pages to the dictionary
        for PageClass in (Home, Setting, CountVideo, CountCamera, DashBoard):
            page_name = PageClass.__name__
            page = PageClass(self.container, self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

        # Show the initial page
        self.show_page("Home")

    def show_page(self, page_name):
        self.config.read("Setting/config.ini")
        # Hide all pages and show the requested page
        for page in self.pages.values():
            page.grid_remove()
        self.pages[page_name].grid()


class Home(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # add widget
        Label(self, text="Count Car Type", font=('Tomato', 20, 'bold')).pack(pady=15)
        Button(self, text="Counting From Camera", width=30, pady=20, font=('Tomato', 10, 'bold'), bd=3, command=lambda: controller.show_page("CountCamera")).pack(pady=2)
        Button(self, text="Counting From Video", width=30, pady=20, font=('Tomato', 10, 'bold'), bd=3,  command=lambda: controller.show_page("CountVideo")).pack(pady=2)
        Button(self, text="Dashboard", width=30, pady=20, font=('Tomato', 10, 'bold'), bd=3, command=lambda: controller.show_page("DashBoard")).pack(pady=2)
        Button(self, text="Setting", width=30, pady=20, font=('Tomato', 10, 'bold'), bd=3, command=lambda: controller.show_page("Setting")).pack(pady=2)
        Button(self, text="Exit", width=30, pady=20, font=('Tomato', 10, 'bold', 'underline'), bd=3, command=lambda: self.quit()).pack(pady=2)


class Setting(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # add widget
        Label(self, text="Count Setting", font=('Tomato', 20, 'bold')).pack(pady=10)
        # --- Connect to Database
        DB_Labelframe = LabelFrame(self, text="Connect to MongoDB Database")
        DB_Labelframe.pack(padx=10, pady=10)

        Label(DB_Labelframe, text="Database").grid(row=0, column=0)
        DB_entry = Entry(DB_Labelframe, width=50)
        DB_entry.insert(END, "mongodb+srv://thirawat:1234@cluster0.1h6mdye.mongodb.net/?retryWrites=true&w=majority")
        DB_entry.grid(row=1, column=1)
        connect_DB = Button(DB_Labelframe, text="Connect", command=lambda: Connect(DB_entry.get()))
        connect_DB.grid(row=1, column=2, padx=10)
        status_DB = Label(DB_Labelframe, text="Status : ")
        status_DB.grid(row=2, column=1, sticky="w")

        # --- Mask Setting
        Mask_setting = LabelFrame(self, text="Select a mask for counting")
        Mask_setting.pack(padx=10, pady=10)

        self.img1 = PhotoImage(file="SourceData/maskSetting.png")
        self.img2 = PhotoImage(file="SourceData/maskSetting2.png")

        pathMask = StringVar()
        pathMask.set("SourceData/mask_selection.png")
        r1 = Radiobutton(Mask_setting, image=self.img1, variable=pathMask, value="SourceData/mask_selection.png")
        r1.grid(row=0, column=0)
        r2 = Radiobutton(Mask_setting, image=self.img2, variable=pathMask, value="SourceData/mask_selection2.png")
        r2.grid(row=0, column=1)

        # --- Only Count From Camera
        frame_count_cam_info = LabelFrame(self, text="Setting Only Counting Form Camera")
        frame_count_cam_info.pack(padx=10, pady=10)

        Label(frame_count_cam_info, text="Set all time to count").grid(row=0, column=0)
        Label(frame_count_cam_info, text="Take a total of").grid(row=1, column=0)

        time_all = Spinbox(frame_count_cam_info, from_=1, to=100)
        time_all.grid(row=1, column=1, pady=5, padx=5)

        type_time = Combobox(frame_count_cam_info, values=['Hrs', 'min'])
        type_time.current(0)
        type_time.grid(row=1, column=2, pady=5, padx=5)

        Label(frame_count_cam_info, text="Record data every").grid(row=2, column=0)

        rec_all = Spinbox(frame_count_cam_info, from_=1, to=100)
        rec_all.grid(row=2, column=1, pady=5, padx=5)

        rec_time = Combobox(frame_count_cam_info, values=['Hrs', 'min'])
        rec_time.current(1)
        rec_time.grid(row=2, column=2, pady=5, padx=5)

        Button(self, text="save", width=10, command=lambda: saveConfig(DB_entry.get(), time_all.get()+" "+type_time.get(), rec_all.get()+" "+rec_time.get(), pathMask)).pack(pady=5)
        Button(self, text="Back to Home", command=lambda: controller.show_page("Home")).pack(pady=5)

        def Connect(DB):
            client = pymongo.MongoClient(DB)
            try:
                client.admin.command('ping')
                tk.messagebox.showinfo("Database", "Pinged your deployment. You successfully connected to MongoDB!")
                status_DB.config(text="Status : OK")
            except Exception as e:
                tk.messagebox.showwarning("Database", "Error ! : "+ str(e))
                status_DB.config(text="Status : Error!")

        def saveConfig(database, Alltime, EveryTime, PathMask):
            try:
                limit = ""
                # setting time
                match1 = re.match(r'(\d+)\s*(\w+)', Alltime)
                value1, unit1 = match1.groups()
                value1 = int(value1)
                if unit1.startswith('Hrs'):
                    Alltime = value1 * 3600
                elif unit1.startswith('min'):
                    Alltime = value1 * 60

                match2 = re.match(r'(\d+)\s*(\w+)', EveryTime)
                value2, unit2 = match2.groups()
                value2 = int(value2)
                if unit2.startswith('Hrs'):
                    EveryTime = value2 * 3600
                elif unit2.startswith('min'):
                    EveryTime = value2 * 60
                # setting mask
                if PathMask.get() == "SourceData/mask_selection.png":
                    limit = "250,180,640,180"
                elif PathMask.get() == "SourceData/mask_selection2.png":
                    limit = "0,220,400,220"

                self.controller.config.set('Config', 'database', database)
                self.controller.config.set('Config', 'all_timecount', str(Alltime))
                self.controller.config.set('Config', 'every_record', str(EveryTime))
                self.controller.config.set('Config', 'path_mask', PathMask.get())
                self.controller.config.set('Config', 'limit', limit)

                # edit config file
                with open("Setting/config.ini", "w") as configfile:
                    self.controller.config.write(configfile)
                tk.messagebox.showinfo('Save', 'Save Config')

            except Exception as e:
                tk.messagebox.showwarning("Incorrect information", "Error ! : "+ str(e))


class CountVideo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config = self.controller.config

        # ------------------- for Count ----------------------------------------
        self.cap = None
        self.path = None
        self.time_start = None
        self.time_end = None

        # Create Object Model YOLO
        model = self.controller.model

        # List item Label name model
        class_list = {0: '2-Axle Truck', 1: '3-Axle Truck ', 2: 'Bicycle', 3: 'Large Bus', 4: 'Medium Bus',
                      5: 'Mini Bus',
                      6: 'car more  than 7 seats ', 7: 'car up to 7 seats', 8: 'Semi Trailer Truck', 9: 'Small Truck',
                      10: 'Trailer Truck', 11: 'Motorbike'}
        # Count id
        self.count_car_type = {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: set(), 6: set(), 7: set(), 8: set(), 9: set(), 10: set(), 11: set()}
        # Object Tracker
        tracker = Tracker()

        # Line Counter
        list_of_integers = self.config['Config']['limit'].split(",")
        limits = [int(x) for x in list_of_integers]
        self.totalCount = []

        # read mask image
        imgMask = cv2.imread(self.config['Config']['path_mask'])

        # create log DataFrame
        cols = ['frame', 'type_id', 'type_name', 'conf', 'x', 'y', 'w', 'h', 'cx', 'cy']
        self.log_df = pd.DataFrame(columns=cols)

        # ----------------------------------------------------------------------
        # add widget
        Label(self, text="Counting Car type From Video", font=('Tomato', 10, 'bold')).grid(row=0, column=0, sticky='N', pady=5, columnspan=2)

        # --- Button Select & Play Video
        Button(self, text="Select Video", command=lambda: selectVideo()).grid(row=1, column=0, sticky='w', padx=10)
        Button(self, text="Play", command=lambda: playCountCar()).grid(row=2, column=0, sticky='w', padx=10)
        path_video_lb = Label(self, text="Video Path : ")
        path_video_lb.grid(row=2, column=1, sticky='w')
        # ---------------------------------------------------------------

        # --- Frame Show image
        image_frame = Frame(self)
        image_frame.grid(row=3, column=0, rowspan=14, columnspan=2)
        # image
        f1 = LabelFrame(image_frame, bg="green")
        f1.grid(row=0, column=0)

        self.image_label = Label(f1, bg="red")
        self.image_label.grid(row=0, column=0)

        # Load the image and keep a reference to the PhotoImage
        img_frame = cv2.imread('SourceData/SelectVideo.png')
        img_frame = cv2.resize(img_frame, (640, 360))
        self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_frame))

        # Set the image to the label
        self.image_label['image'] = self.photo_image

        # -- frame Count Table
        tabel_frame = Frame(self)
        tabel_frame.grid(row=3, column=3)

        Label(tabel_frame, text="Counting table").grid(row=0, column=0, columnspan=1, sticky=NSEW)

        Label(tabel_frame, text="Passenger car up to 7 people").grid(row=1, column=0, sticky=W, padx=10)
        car_up_7 = Label(tabel_frame, text=str(len(self.count_car_type[7])))
        car_up_7.grid(row=1, column=1)

        Label(tabel_frame, text="Passenger car more than 7 people").grid(row=2, column=0, sticky=W, padx=10)
        car_more_7 = Label(tabel_frame, text=str(len(self.count_car_type[6])))
        car_more_7.grid(row=2, column=1)

        Label(tabel_frame, text="Small Truck (4 wheels)").grid(row=3, column=0, sticky=W, padx=10)
        small_truck = Label(tabel_frame, text=str(len(self.count_car_type[9])))
        small_truck.grid(row=3, column=1)

        Label(tabel_frame, text="2-Axle Truck (6 wheels)").grid(row=4, column=0, sticky=W, padx=10)
        axle_2_truck = Label(tabel_frame, text=str(len(self.count_car_type[0])))
        axle_2_truck.grid(row=4, column=1)

        Label(tabel_frame, text="3-Axle Truck (10 wheels)").grid(row=5, column=0, sticky=W, padx=10)
        axle_3_truck = Label(tabel_frame, text=str(len(self.count_car_type[1])))
        axle_3_truck.grid(row=5, column=1)

        Label(tabel_frame, text="Trailer Truck (More than 3 Axle)").grid(row=6, column=0, sticky=W, padx=10)
        trailer_truck = Label(tabel_frame, text=str(len(self.count_car_type[10])))
        trailer_truck.grid(row=6, column=1)

        Label(tabel_frame, text="Semi Trailer Truck (More than 3 Axle)").grid(row=7, column=0, sticky=W, padx=10)
        semi_trailer_truck = Label(tabel_frame, text=str(len(self.count_car_type[8])))
        semi_trailer_truck.grid(row=7, column=1)

        Label(tabel_frame, text="Mini Bus").grid(row=8, column=0, sticky=W, padx=10)
        bus_mini = Label(tabel_frame, text=str(len(self.count_car_type[5])))
        bus_mini.grid(row=8, column=1)

        Label(tabel_frame, text="Medium Bus").grid(row=9, column=0, sticky=W, padx=10)
        bus_me = Label(tabel_frame, text=str(len(self.count_car_type[4])))
        bus_me.grid(row=9, column=1)

        Label(tabel_frame, text="Large Bus").grid(row=10, column=0, sticky=W, padx=10)
        bus_lar = Label(tabel_frame, text=str(len(self.count_car_type[3])))
        bus_lar.grid(row=10, column=1)

        Label(tabel_frame, text="Bicycle (2-3 wheels)").grid(row=11, column=0, sticky=W, padx=10)
        bicycle = Label(tabel_frame, text=str(len(self.count_car_type[2])))
        bicycle.grid(row=11, column=1)

        Label(tabel_frame, text="Tuk-Tuk and Motorbike").grid(row=12, column=0, sticky=W, padx=10)
        motorbike = Label(tabel_frame, text=str(len(self.count_car_type[11])))
        motorbike.grid(row=12, column=1)

        Label(tabel_frame, text="Total Count").grid(row=13, column=0, sticky=W, padx=10)
        tot_count = Label(tabel_frame, text=str(len(self.totalCount)))
        tot_count.grid(row=13, column=1)
        # --- Button Back to home page
        bu_frame = Frame(self)
        bu_frame.grid(row=17, column=0, sticky='w', padx=10)

        self.back = Button(bu_frame, text="Back", command=lambda: controller.show_page("Home"))
        self.back.grid(row=0, column=0, sticky='w', padx=10)
        self.download = Button(bu_frame, text="Download", command=lambda: ExportFile())
        self.download.grid(row=0, column=1, sticky='w', padx=10)
        self.saveDB = Button(bu_frame, text="Save to Database", command=lambda: SaveToDatabase())
        self.saveDB.grid(row=0, column=2, sticky='w', padx=10)

        def selectVideo():
            try:
                video_path = filedialog.askopenfilename(filetypes=[
                    ("all video format", "mp4"),
                    ("all video format", "avi")])
                if len(video_path) > 0:
                    self.path = video_path
                    path_video_lb.config(text="Video : "+ self.path)
                    self.cap = cv2.VideoCapture(video_path)
                    img_ = cv2.imread('SourceData/PlayVideo.png')
                    img_ = cv2.resize(img_, (640, 360))
                    self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_))
                    self.image_label['image'] = self.photo_image

                    # Reset Data
                    self.count_car_type = {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: set(), 6: set(), 7: set(),
                                           8: set(), 9: set(), 10: set(), 11: set()}
                    self.totalCount = []

                    self.log_df = pd.DataFrame(columns=['frame', 'type_id', 'type_name', 'conf', 'x', 'y', 'w', 'h', 'cx', 'cy'])

                    # update data on Counting tabel
                    car_up_7.config(text=str(len(self.count_car_type[7])))
                    car_more_7.config(text=str(len(self.count_car_type[6])))
                    small_truck.config(text=str(len(self.count_car_type[9])))
                    axle_2_truck.config(text=str(len(self.count_car_type[0])))
                    axle_3_truck.config(text=str(len(self.count_car_type[1])))
                    trailer_truck.config(text=str(len(self.count_car_type[10])))
                    semi_trailer_truck.config(text=str(len(self.count_car_type[8])))
                    bus_mini.config(text=str(len(self.count_car_type[5])))
                    bus_me.config(text=str(len(self.count_car_type[4])))
                    bus_lar.config(text=str(len(self.count_car_type[3])))
                    bicycle.config(text=str(len(self.count_car_type[2])))
                    motorbike.config(text=str(len(self.count_car_type[11])))
                    tot_count.config(text=str(len(self.totalCount)))
                else:
                    path_video_lb.config(text="Select your Video")
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))

        def ExportFile():
            try:
                if self.cap is None:
                    tk.messagebox.showwarning("Warning!", "Please Select Video")
                elif len(self.log_df) == 0:
                    tk.messagebox.showwarning("Warning!", "Play Video")
                else:
                    file = filedialog.asksaveasfilename(
                        filetypes=[("excel file", ".xlsx")],
                        defaultextension=".xlsx")
                    if file:
                        df_info = pd.DataFrame(
                            [[str(self.path), self.cap.get(cv2.CAP_PROP_FPS), int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)), (int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))/self.cap.get(cv2.CAP_PROP_FPS)), self.time_start, self.time_end]],
                            columns=['path', 'fps', 'total frame', 'duration (sec)', 'start_count', 'end_count'])
                        df_con = self.log_df.groupby(['type_name']).size().reset_index(name='counts')

                        with pd.ExcelWriter(file, engine='xlsxwriter') as writer:
                            df_info.to_excel(writer, sheet_name='video info', index=False)
                            self.log_df.to_excel(writer, sheet_name='Counting log', index=False)
                            df_con.to_excel(writer, sheet_name='Summary of car types', index=False)
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))

        def SaveToDatabase():
            try:
                if self.cap is None:
                    tk.messagebox.showwarning("Warning!", "Please Select Video")
                elif len(self.log_df) == 0:
                    tk.messagebox.showwarning("Warning!", "Play Video")
                else:
                    # Create a new client and connect to the server
                    uri = self.config['Config']['Database']
                    client = pymongo.MongoClient(uri)
                    mydb = client['mydatabase']
                    mycol = mydb["CountFormVideo"]
                    try:
                        my_dict_log = self.log_df.to_dict(orient='records')
                        my_dict_data = {
                            "Path": str(self.path),
                            'fps': self.cap.get(cv2.CAP_PROP_FPS),
                            'total frame': self.cap.get(cv2.CAP_PROP_FRAME_COUNT),
                            'duration (s)': (int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) / self.cap.get(cv2.CAP_PROP_FPS)),
                            'start_count': self.time_start,
                            'end_count': self.time_end,
                            'Log': my_dict_log
                        }
                        mycol.insert_one(my_dict_data)
                        tk.messagebox.showinfo("DataBase MongoDB", "Successfully inserted into the database")
                    except Exception as e:
                        tk.messagebox.showwarning("Warning!", f"An error occurred: {type(e).__name__} - {e}")
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))

        def playCountCar():
            try:
                if self.cap is None:
                    tk.messagebox.showwarning("Warning!", "Please Select Video")
                else:
                    show = tk.messagebox.askyesno("Show Frame", "Do you want to show video?")
                    img_ = cv2.imread('SourceData/VideoProcessing.png')
                    img_ = cv2.resize(img_, (640, 360))
                    self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_))
                    self.image_label.configure(image=self.photo_image)
                    # lock button
                    self.back['state'] = tk.DISABLED
                    self.download['state'] = tk.DISABLED
                    self.saveDB['state'] = tk.DISABLED

                    count_frame = 1
                    self.time_start = datetime.now()
                    while True:
                        ret, frame = self.cap.read()
                        # Check if the frame is empty or invalid
                        if not ret or frame is None:
                            img_ = cv2.imread('SourceData/EndCounting.png')
                            img_ = cv2.resize(img_, (640, 360))
                            self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_))
                            self.image_label.configure(image=self.photo_image)
                            self.time_end = datetime.now()
                            # unlock button
                            self.back['state'] = tk.NORMAL
                            self.download['state'] = tk.NORMAL
                            self.saveDB['state'] = tk.NORMAL
                            break  # Exit the loop if there's an issue with reading frames

                        frame = cv2.resize(frame, (640, 360))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        imgRegion = cv2.bitwise_and(frame, imgMask)

                        # Detect Object Car Type
                        result = model(imgRegion)
                        a = result[0].boxes.data
                        px = pd.DataFrame(a).astype("float")

                        # list object predict
                        list_obj = []
                        for index, row in px.iterrows():
                            x1 = int(row[0])
                            y1 = int(row[1])
                            x2 = int(row[2])
                            y2 = int(row[3])
                            conf = row[4]
                            d = int(row[5])
                            list_obj.append([x1, y1, x2, y2, d, conf])
                        # Tracker ID for Car Type
                        bbox_id = tracker.update(list_obj)

                        # Create line counter
                        cv2.line(frame, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 2)
                        for bbox in bbox_id:
                            x3, y3, x4, y4, id, cls, conf = bbox
                            cx = int(x3 + x4) // 2
                            cy = int(y3 + y4) // 2
                            w, h = x4 - x3, y4 - y3

                            # Bounding Box to obj
                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 3)
                            cv2.putText(frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 1)

                            cvzone.cornerRect(frame, (x3, y3, w, h), l=9)
                            cvzone.putTextRect(frame, f'{conf:0.2f} {class_list[cls]}', (max(0, x3), max(35, y3)), 1, 1, 3)

                            # Counting Car
                            if limits[0] < cx < limits[2] and limits[1] - 20 < cy < limits[1] + 20:
                                if self.totalCount.count(id) == 0:
                                    self.totalCount.append(id)
                                    self.count_car_type[cls].add(id)  # add id to dict {count_car_type}

                                    add_log = pd.DataFrame([[count_frame, cls, class_list[cls], conf, x3, y3, w, h, cx, cy]], columns=cols)
                                    self.log_df = pd.concat([self.log_df, add_log], ignore_index=True)

                                    # update data on Counting tabel
                                    car_up_7.config(text=str(len(self.count_car_type[7])))
                                    car_more_7.config(text=str(len(self.count_car_type[6])))
                                    small_truck.config(text=str(len(self.count_car_type[9])))
                                    axle_2_truck.config(text=str(len(self.count_car_type[0])))
                                    axle_3_truck.config(text=str(len(self.count_car_type[1])))
                                    trailer_truck.config(text=str(len(self.count_car_type[10])))
                                    semi_trailer_truck.config(text=str(len(self.count_car_type[8])))
                                    bus_mini.config(text=str(len(self.count_car_type[5])))
                                    bus_me.config(text=str(len(self.count_car_type[4])))
                                    bus_lar.config(text=str(len(self.count_car_type[3])))
                                    bicycle.config(text=str(len(self.count_car_type[2])))
                                    motorbike.config(text=str(len(self.count_car_type[11])))
                                    tot_count.config(text=str(len(self.totalCount)))
                        if show:
                            self.photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
                            self.image_label.configure(image=self.photo_image)
                        count_frame += 1 # count number of frame
                        root.update()
                        # Add a delay to control the frame rate
                        cv2.waitKey(1)
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))


class CountCamera(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.config = self.controller.config

        self.time, self.time_rec = int(self.config['Config']['all_timecount']), int(self.config['Config']['every_record'])
        # database
        uri = self.config['Config']['Database']
        self.client = pymongo.MongoClient(uri)
        self.myDatabase = self.client['mydatabase']
        self.myCollect = self.myDatabase["CountFormCamera"]

        # ------------------- for Count ----------------------------------------
        self.cap = None
        self.time_start = None
        self.time_end = None

        # Create Object Model YOLO
        model = self.controller.model

        # List item Label name model
        class_list = {0: '2-Axle Truck', 1: '3-Axle Truck ', 2: 'Bicycle', 3: 'Large Bus', 4: 'Medium Bus',
                      5: 'Mini Bus',
                      6: 'car more  than 7 seats ', 7: 'car up to 7 seats', 8: 'Semi Trailer Truck', 9: 'Small Truck',
                      10: 'Trailer Truck', 11: 'Motorbike'}
        # Count id
        self.count_car_type = {0: set(), 1: set(), 2: set(), 3: set(), 4: set(), 5: set(), 6: set(), 7: set(), 8: set(),
                               9: set(), 10: set(), 11: set()}
        # Object Tracker
        tracker = Tracker()

        # Line Counter
        self.list_of_integers = self.config['Config']['limit'].split(",")
        self.limits = [int(x) for x in self.list_of_integers]
        self.totalCount = []

        # read mask image
        self.imgMask = cv2.imread(self.config['Config']['path_mask'])

        # create log DataFrame
        cols = ['frame', 'type_id', 'type_name', 'conf', 'x', 'y', 'w', 'h', 'cx', 'cy']
        self.log_df = pd.DataFrame(columns=cols)
        # ----------------------------------------------------------------------

        # add widget
        Label(self, text="Counting Car type From Camera", font=('Tomato', 10, 'bold')).grid(row=0, column=0, sticky='N', pady=5, columnspan=2)

        # --- Button Select & Play Video
        Button_frame = Frame(self)
        Button_frame.grid(row=2, column=0, pady=5)

        Button(Button_frame, text="Play", command=lambda: playCountCar()).grid(row=1, column=0, sticky='w', padx=10)
        Button(Button_frame, text="Reset Config", command=lambda: resetConfig()).grid(row=1, column=1, sticky='w', padx=10)

        self.UseExample = IntVar()
        Checkbutton(Button_frame, text="Use Video Example", variable=self.UseExample, offvalue=0, onvalue=1).grid(row=1, column=2, sticky='w')

        path_video_lb = Label(Button_frame, text="Time all :"+str(self.time)+" Time record: "+str(self.time_rec))
        path_video_lb.grid(row=1, column=3, sticky='w')
        # ---------------------------------------------------------------

        # --- Frame Show image
        image_frame = Frame(self)
        image_frame.grid(row=3, column=0, rowspan=14, columnspan=3)
        # image
        f1 = LabelFrame(image_frame, bg="green")
        f1.grid(row=0, column=0)

        self.image_label = Label(f1, bg="red")
        self.image_label.grid(row=0, column=0)

        # Load the image and keep a reference to the PhotoImage
        img_frame = cv2.imread('SourceData/SelectVideo.png')
        img_frame = cv2.resize(img_frame, (640, 360))
        self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_frame))

        # Set the image to the label
        self.image_label['image'] = self.photo_image

        # -- frame Count Table
        tabel_frame = Frame(self)
        tabel_frame.grid(row=3, column=3)

        Label(tabel_frame, text="Counting table").grid(row=0, column=0, columnspan=1, sticky=NSEW)

        Label(tabel_frame, text="Passenger car up to 7 people").grid(row=1, column=0, sticky=W, padx=10)
        car_up_7 = Label(tabel_frame, text=str(len(self.count_car_type[7])))
        car_up_7.grid(row=1, column=1)

        Label(tabel_frame, text="Passenger car more than 7 people").grid(row=2, column=0, sticky=W, padx=10)
        car_more_7 = Label(tabel_frame, text=str(len(self.count_car_type[6])))
        car_more_7.grid(row=2, column=1)

        Label(tabel_frame, text="Small Truck (4 wheels)").grid(row=3, column=0, sticky=W, padx=10)
        small_truck = Label(tabel_frame, text=str(len(self.count_car_type[9])))
        small_truck.grid(row=3, column=1)

        Label(tabel_frame, text="2-Axle Truck (6 wheels)").grid(row=4, column=0, sticky=W, padx=10)
        axle_2_truck = Label(tabel_frame, text=str(len(self.count_car_type[0])))
        axle_2_truck.grid(row=4, column=1)

        Label(tabel_frame, text="3-Axle Truck (10 wheels)").grid(row=5, column=0, sticky=W, padx=10)
        axle_3_truck = Label(tabel_frame, text=str(len(self.count_car_type[1])))
        axle_3_truck.grid(row=5, column=1)

        Label(tabel_frame, text="Trailer Truck (More than 3 Axle)").grid(row=6, column=0, sticky=W, padx=10)
        trailer_truck = Label(tabel_frame, text=str(len(self.count_car_type[10])))
        trailer_truck.grid(row=6, column=1)

        Label(tabel_frame, text="Semi Trailer Truck (More than 3 Axle)").grid(row=7, column=0, sticky=W, padx=10)
        semi_trailer_truck = Label(tabel_frame, text=str(len(self.count_car_type[8])))
        semi_trailer_truck.grid(row=7, column=1)

        Label(tabel_frame, text="Mini Bus").grid(row=8, column=0, sticky=W, padx=10)
        bus_mini = Label(tabel_frame, text=str(len(self.count_car_type[5])))
        bus_mini.grid(row=8, column=1)

        Label(tabel_frame, text="Medium Bus").grid(row=9, column=0, sticky=W, padx=10)
        bus_me = Label(tabel_frame, text=str(len(self.count_car_type[4])))
        bus_me.grid(row=9, column=1)

        Label(tabel_frame, text="Large Bus").grid(row=10, column=0, sticky=W, padx=10)
        bus_lar = Label(tabel_frame, text=str(len(self.count_car_type[3])))
        bus_lar.grid(row=10, column=1)

        Label(tabel_frame, text="Bicycle (2-3 wheels)").grid(row=11, column=0, sticky=W, padx=10)
        bicycle = Label(tabel_frame, text=str(len(self.count_car_type[2])))
        bicycle.grid(row=11, column=1)

        Label(tabel_frame, text="Tuk-Tuk and Motorbike").grid(row=12, column=0, sticky=W, padx=10)
        motorbike = Label(tabel_frame, text=str(len(self.count_car_type[11])))
        motorbike.grid(row=12, column=1)

        Label(tabel_frame, text="Total Count").grid(row=13, column=0, sticky=W, padx=10)
        tot_count = Label(tabel_frame, text=str(len(self.totalCount)))
        tot_count.grid(row=13, column=1)
        # --- Button Back to home page
        bu_frame = Frame(self)
        bu_frame.grid(row=17, column=0, sticky='w', padx=10)

        self.back = Button(bu_frame, text="Back", command=lambda: controller.show_page("Home"))
        self.back.grid(row=0, column=0, sticky='w', padx=10)
        update_label = Label(bu_frame, text="click Reset Config and Play for Start Count")
        update_label.grid(row=0, column=1, sticky='w', padx=15)

        def resetConfig():
            try:
                self.config.read("Setting/config.ini")
                #time
                self.time, self.time_rec = int(self.config['Config']['all_timecount']), int(self.config['Config']['every_record'])
                # database
                self.client = pymongo.MongoClient(self.config['Config']['Database'])
                self.myDatabase = self.client['mydatabase']
                self.myCollect = self.myDatabase["CountFormCamera"]
                # Line Counter
                self.list_of_integers = self.config['Config']['limit'].split(",")
                self.limits = [int(x) for x in self.list_of_integers]
                self.totalCount = []
                # read mask image
                self.imgMask = cv2.imread(self.config['Config']['path_mask'])
                # config Label
                path_video_lb.config(text="Time all :"+str(self.time)+" Time record: "+str(self.time_rec))
                tk.messagebox.showinfo('Config Reset', 'Config is reset')
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))

        def playCountCar():
            try:
                if self.UseExample.get() == 0:
                    self.cap = cv2.VideoCapture(0)
                else:
                    self.cap = cv2.VideoCapture("SourceData/video2.mp4")

                if self.cap is None:
                    tk.messagebox.showwarning("Warning!", "Please Select Video")
                else:
                    self.back['state'] = tk.DISABLED
                    interval = self.time_rec  # Time interval in seconds
                    total_time = self.time  # Total time in seconds
                    count_time = 0

                    start_time = datetime.now()
                    hello_time = datetime.now()

                    self.time_start = datetime.now()
                    count_frame = 1
                    Round_ = 1
                    update_label.config(text="Counting in progress")
                    while True:
                        ret, frame = self.cap.read()
                        # Check if the frame is empty or invalid
                        if not ret or frame is None:
                            img_ = cv2.imread('SourceData/EndCounting.png')
                            img_ = cv2.resize(img_, (640, 360))
                            self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_))
                            self.image_label.configure(image=self.photo_image)
                            self.back['state'] = tk.NORMAL
                            break  # Exit the loop if there's an issue with reading frames

                        # Check if Every time to Record
                        elapsed_hello_time = datetime.now() - hello_time
                        if elapsed_hello_time.total_seconds() >= interval:
                            count_time += 1

                            # add to database
                            self.time_end = datetime.now()
                            my_dict_log = self.log_df.to_dict(orient='records')
                            my_dict_data = {
                                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                                'start_count': self.time_start,
                                'end_count': self.time_end,
                                'total time (s)': self.time,
                                'each time record (s)': self.time_rec,
                                'round': Round_,
                                'Log': my_dict_log
                            }
                            self.myCollect.insert_one(my_dict_data)

                            update_label.config(text="Round: "+ str(Round_)+ " Record")
                            Round_+=1 # update round
                            hello_time = datetime.now()

                            # reset
                            self.log_df = pd.DataFrame(columns=['frame', 'type_id', 'type_name', 'conf', 'x', 'y', 'w', 'h', 'cx', 'cy'])
                            self.time_start = self.time_end

                        # Check if End to Record
                        elapsed_time = datetime.now() - start_time
                        if elapsed_time.total_seconds() >= total_time:
                            img_ = cv2.imread('SourceData/EndCounting.png')
                            img_ = cv2.resize(img_, (640, 360))
                            self.photo_image = ImageTk.PhotoImage(Image.fromarray(img_))
                            self.image_label['image'] = self.photo_image

                            # add to database
                            self.time_end = datetime.now()
                            my_dict_log = self.log_df.to_dict(orient='records')
                            my_dict_data = {
                                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                                'start_count': self.time_start,
                                'end_count': self.time_end,
                                'total time (s)': self.time,
                                'each time record (s)': self.time_rec,
                                'round': Round_,
                                'Log': my_dict_log
                            }
                            if len(my_dict_log) == 0:
                                update_label.config(text="Record, End Count")
                            else:
                                self.myCollect.insert_one(my_dict_data)
                                update_label.config(text="Round: " + str(Round_) + " Record, End Count")
                            self.cap = None
                            self.back['state'] = tk.NORMAL
                            break

                        frame = cv2.resize(frame, (640, 360))
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        imgRegion = cv2.bitwise_and(frame, self.imgMask)

                        # Detect Object Car Type
                        result = model(imgRegion)
                        a = result[0].boxes.data
                        px = pd.DataFrame(a).astype("float")

                        # list object predict
                        list_obj = []
                        for index, row in px.iterrows():
                            x1 = int(row[0])
                            y1 = int(row[1])
                            x2 = int(row[2])
                            y2 = int(row[3])
                            conf = row[4]
                            d = int(row[5])
                            list_obj.append([x1, y1, x2, y2, d, conf])
                        # Tracker ID for Car Type
                        bbox_id = tracker.update(list_obj)

                        # Create line counter
                        cv2.line(frame, (self.limits[0], self.limits[1]), (self.limits[2], self.limits[3]), (0, 255, 0), 2)
                        for bbox in bbox_id:
                            x3, y3, x4, y4, id, cls, conf = bbox
                            cx = int(x3 + x4) // 2
                            cy = int(y3 + y4) // 2
                            w, h = x4 - x3, y4 - y3

                            # Bounding Box to obj
                            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                            cv2.rectangle(frame, (x3, y3), (x4, y4), (255, 0, 255), 3)
                            cv2.putText(frame, str(id), (cx, cy), cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 255, 255), 1)

                            cvzone.cornerRect(frame, (x3, y3, w, h), l=9)
                            cvzone.putTextRect(frame, f'{conf:0.2f} {class_list[cls]}', (max(0, x3), max(35, y3)), 1, 1, 3)

                            # Counting Car
                            if self.limits[0] < cx < self.limits[2] and self.limits[1] - 20 < cy < self.limits[1] + 20:
                                if self.totalCount.count(id) == 0:
                                    self.totalCount.append(id)
                                    self.count_car_type[cls].add(id)  # add id to dict {count_car_type}

                                    add_log = pd.DataFrame(
                                        [[count_frame, cls, class_list[cls], conf, x3, y3, w, h, cx, cy]],
                                        columns=cols)
                                    self.log_df = pd.concat([self.log_df, add_log], ignore_index=True)

                                    # update data on Counting tabel
                                    car_up_7.config(text=str(len(self.count_car_type[7])))
                                    car_more_7.config(text=str(len(self.count_car_type[6])))
                                    small_truck.config(text=str(len(self.count_car_type[9])))
                                    axle_2_truck.config(text=str(len(self.count_car_type[0])))
                                    axle_3_truck.config(text=str(len(self.count_car_type[1])))
                                    trailer_truck.config(text=str(len(self.count_car_type[10])))
                                    semi_trailer_truck.config(text=str(len(self.count_car_type[8])))
                                    bus_mini.config(text=str(len(self.count_car_type[5])))
                                    bus_me.config(text=str(len(self.count_car_type[4])))
                                    bus_lar.config(text=str(len(self.count_car_type[3])))
                                    bicycle.config(text=str(len(self.count_car_type[2])))
                                    motorbike.config(text=str(len(self.count_car_type[11])))
                                    tot_count.config(text=str(len(self.totalCount)))

                        self.photo_image = ImageTk.PhotoImage(Image.fromarray(frame))
                        self.image_label.configure(image=self.photo_image)
                        root.update()

                        count_frame += 1  # count number of frame
                        # Add a delay to control the frame rate
                        cv2.waitKey(1)
            except Exception as e:
                tk.messagebox.showwarning("Warning", "Error ! : "+ str(e))


class DashBoard(tk.Frame):
        def __init__(self, parent, controller):
            tk.Frame.__init__(self, parent)
            self.controller = controller
            self.path = ""
            # add widget
            Label(self, text="Counting Car type From Camera", font=('Tomato', 10, 'bold')).grid(row=0, column=0, sticky='N', pady=5, columnspan=3)

            # --- Button Back to home page
            bu_frame = Frame(self)
            bu_frame.grid(row=1, column=0, sticky='w', padx=10)
            Button(bu_frame, width=10, text="Back", command=lambda: controller.show_page("Home")).grid(row=0, column=0, pady=3)
            Button(bu_frame, width=10, text="Select File", command=lambda: selectFile()).grid(row=0, column=1, pady=3)

            self.la_path = Label(bu_frame, text="File Path: ")
            self.la_path.grid(row=0, column=2, pady=5)

            Button(bu_frame, text="Plot", width=10, command=lambda: plot()).grid(row=2, column=0, padx=10)
            Button(bu_frame, text="Plot2", width=10, command=lambda: plot1()).grid(row=2, column=1, padx=10)
            # ------- plot dashboard
            plot_frame = Frame(self)
            plot_frame.grid(row=2, column=0, sticky='w', padx=10)

            def plot():
                try:
                    if len(self.path) > 0:

                        # Delete all widgets in plot_frame
                        for widget in plot_frame.winfo_children():
                            widget.destroy()

                        # Read Data
                        self.df_video = pd.read_excel(self.path, sheet_name='video info')
                        self.df_log = pd.read_excel(self.path, sheet_name='Counting log')
                        self.df_sum_car = pd.read_excel(self.path, sheet_name='Summary of car types')

                        #  ---------------- plot
                        # the figure that will contain the plot
                        plt.subplots_adjust(wspace=0.5)
                        fig = Figure(figsize=(10, 4), dpi=100)

                        # adding the subplot
                        plot1 = fig.add_subplot(121)
                        plot2 = fig.add_subplot(122)

                        # plotting the graph
                        plot1.pie(self.df_sum_car['counts'], labels=self.df_sum_car['type_name'], textprops={'fontsize': 6})
                        plot1.set_title("Total of Car Type Pie Chart", fontsize=6)

                        x_values = range(len(self.df_sum_car['type_name']))  # Generating x-values
                        plot2.bar(x_values, self.df_sum_car['counts'], width=1)
                        plot2.set_xticks(x_values)  # Setting x-ticks to be at the center of each bar
                        plot2.set_xticklabels(self.df_sum_car['type_name'], fontsize=6, rotation=15)  # Setting x-tick labels with rotation
                        plot2.set_title("Total of Car Type Bar", fontsize=6)
                        plot2.set_xlabel('Car Type', fontsize=6)
                        plot2.set_ylabel('Count', fontsize=6)

                        # creating the Tkinter canvas
                        # containing the Matplotlib figure
                        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
                        canvas.draw()

                        # placing the canvas on the Tkinter window
                        canvas.get_tk_widget().pack()

                        # creating the Matplotlib toolbar
                        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
                        toolbar.update()

                        # placing the toolbar on the Tkinter window
                        canvas.get_tk_widget().pack()
                    else:
                        tk.messagebox.showwarning("Warning", "Pls, Select File For Plot Graph")
                except Exception as e:
                    print(str(e))
                    tk.messagebox.showwarning("Warning", "Error ! : " + str(e))

            def plot1():
                try:
                    if len(self.path) > 0:

                        # Delete all widgets in plot_frame
                        for widget in plot_frame.winfo_children():
                            widget.destroy()

                        # Read Data
                        self.df_log = pd.read_excel(self.path, sheet_name='Counting log')
                        #  ---------------- plot
                        # the figure that will contain the plot
                        fig = plt.figure(figsize=(10, 4))
                        plt.scatter(self.df_log['cx'].values, self.df_log['cy'].values, color='red', marker='*')
                        self.bg_img = plt.imread('SourceData/frameV2.jpg')
                        plt.imshow(self.bg_img, extent=[0, 640, 0, 360])

                        plt.xlim(0, 640)
                        plt.ylim(0, 360)

                        plt.xlabel('cx')
                        plt.ylabel('cy')

                        # creating the Tkinter canvas
                        # containing the Matplotlib figure
                        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
                        canvas.draw()

                        # placing the canvas on the Tkinter window
                        canvas.get_tk_widget().pack()

                        # creating the Matplotlib toolbar
                        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
                        toolbar.update()

                        # placing the toolbar on the Tkinter window
                        canvas.get_tk_widget().pack()
                    else:
                        tk.messagebox.showwarning("Warning", "Pls, Select File For Plot Graph")
                except Exception as e:
                    print(str(e))
                    tk.messagebox.showwarning("Warning", "Error ! : " + str(e))

            def selectFile():
                try:
                    data_path = filedialog.askopenfilename(filetypes=[
                        ("all Excel format", "xlsx")])
                    if len(data_path) > 0:
                        self.path = data_path
                        self.la_path.config(text="File Path: "+ self.path)
                    else:
                        self.la_path.config(text="Select your File")
                except Exception as e:
                    tk.messagebox.showwarning("Warning", "Error ! : " + str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.geometry("1000x500")
    root.iconphoto(False, tk.PhotoImage(file='SourceData/IconCCT.png'))
    root.resizable(False, False)
    root.mainloop()