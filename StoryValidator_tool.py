#=============================================================================
# StoryValidator.py
#=============================================================================
"""
Evaluates story from Twine file (JSON format)
"""

import json
import re
import os
import sys
import warnings
import graphviz
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from tkinter import *
import PIL
from PIL import ImageTk, Image
from scrollimage import ScrollableImage 
import matplotlib as mpl
from graphviz import Digraph
from graphviz import *
from fpdf import FPDF
import matplotlib.pyplot as plt
from functools import partial

__author__ = "Carolina Veloso"
__version__ = "1.0.1"

class PDF(FPDF):
    ''' 
    Create the PDF object. 
    The PDF object is [...]

    '''
    def bounds(self):
       self.rect(5.0, 5.0, 200.0,287.0)

    def setup_image(self, fn):
        image = Image.open(fn)
        width, height = image.size

        # convert pixel in mm with 1px=0.264583 mm
        width, height = float(width * 0.264583), float(height * 0.264583)
        
        # A4 format size is w = 210 and h= 297 (200, 277 with borders and title)
        # Make sure image size is not greater than the pdf format size
        if (width > 200):
            width = 200
        if (height > 277): 
            height = 277

        self.image(fn, 210/2 - width/2 , 297/2 - height/2, width, height)

class GUI:
    ''' 
    Create the GUI object. 
    The GUI object is the user interface window that is drawn using Python's Tkinter framework.

    '''

    def __init__(self, win):

        self.flag_tooltips = 1
        self.selected_vars = []                 # story variables selected by the user
        self.graphValues = []                   # list of variable values for the graph

        # Create top frame
        top_frame = Frame(win, width=w*0.13, height=h*0.694, bg='skyblue')
        top_frame.grid(row=0, column=0, padx=20, pady=5)

        # Create frame for file input inside top_frame
        top_file = Frame(top_frame, width=w*0.26, height=h*0.23)
        top_file.grid(row=0, column=0, padx=0, pady=0)

        # Create frame for buttons under top_file
        top_buttons = Frame(top_file, width=w*0.26, height=h*0.21)
        top_buttons.grid(row=1, column=0, padx=0, pady=0)

        # Create labels in left_frame for file input
        self.file_name = tk.StringVar()
        self.file_name.set("")

        self.Label = Label(top_file, textvariable=self.file_name, bg="white", width="40", borderwidth=1, relief="solid")
        self.Label.grid(row=0, column=0, padx=5, pady=5, ipadx=0)

        # Create buttons
        self.B1= Button(top_buttons, text = "Choose a Story File", width="18", borderwidth=1, relief="solid", command=self.onChooseFileClick)
        self.B1.grid(row=1, column=0, padx=7, pady=5)
        self.B2= Button(top_buttons, text = "Load", width="18", borderwidth=1, relief="solid", command=self.onSubmitClick, state= DISABLED)
        self.B2.grid(row=1, column=1, padx=7, pady=5)

        # Create frame for options (checkboxes) under top_file
        self.options_frame = Frame(top_file, width=w*0.26, height=h*0.21)
        self.options_frame.grid(row=2, column=0, padx=0, pady=0)

        # Create and set values to entries for variable treshold
        self.entryMin = tk.StringVar()
        self.entryMin.set( "0" )
        self.entryMin.trace("w", self.changeVerifyButton)

        self.entryMax = tk.StringVar()
        self.entryMax.set( "1" )
        self.entryMax.trace("w", self.changeVerifyButton)

        # List of Checkboxes for "Analysis Conditions"
        Label(self.options_frame, text="------ Analysis Conditions ------").grid(row=0, pady=10)

        C0 = Checkbutton(self.options_frame, text="Number of Paths", width = "36", anchor="w", command=self.changeVerifyButton, state= DISABLED)
        C0.grid(row=1)
        C1 = Checkbutton(self.options_frame, text="Ending Hit Percentage", width = "36", anchor="w", command=self.changeVerifyButton, state=DISABLED)
        C1.grid(row=2)
        L1 = Label(self.options_frame, text="(Choose up to three)", width = "36", anchor="e", state=DISABLED)
        L1.grid(row=5, column = 0)
        C2 = Checkbutton(self.options_frame, text= "Variable Value Evolution", width = "36", anchor="w", command=self.changeVerifyButton, state=DISABLED)
        C2.grid(row=6)
        C3 = Checkbutton(self.options_frame, text="Variables value inside Threshold", width = "36", anchor="w", command=self.changeVerifyButton, state=DISABLED)
        C3.grid(row=7)
        L2 = Label(self.options_frame, text="Min:                     ", width = "38", state=DISABLED)
        L2.grid(row=8)
        L3 = Label(self.options_frame, text="Max:                     ", width = "38", state=DISABLED)
        L3.grid(row=9)
        E1 = Entry(self.options_frame, width=5, textvariable=self.entryMin, state=DISABLED)
        E1.grid(row=8)
        E2 = Entry(self.options_frame, width=5, textvariable=self.entryMax, state=DISABLED )
        E2.grid(row=9)
        C4 = Checkbutton(self.options_frame, text="Stroke Points", width = "36", anchor="w", command=self.changeVerifyButton, state=DISABLED)
        C4.grid(row=3)
        C5 = Checkbutton(self.options_frame, text="Lost Plot", width = "36", anchor="w", command=self.changeVerifyButton, state=DISABLED)
        C5.grid(row=4)

        self.checkboxes_list = [C0, C1, C2, C3, C4, C5]
        self.labels_list = [L2, L3, E1, E2]

        self.tooltips_items = {}

        # Add items to the dictionary with respective text
        self.tooltips_items[C0] = "Shows all possible narrative paths including\nwhich passages are visited in each path."
        self.tooltips_items[C1] = "Shows the amount of paths and the\nchances(%) for reaching each ending."
        self.tooltips_items[C2] = "First tree shows the final value of the selected variable for each path.\nThe second tree shows the value evolution in each passage."
        self.tooltips_items[C3] = "Highlights the passages where the selected variable\nhas a value greater than the defined MIN value and\nsmaller than the defined MAX value."
        self.tooltips_items[C4] = "Bolds the outline of the passages that\nare visited in all narrative paths."
        self.tooltips_items[C5] = "Shows which passages are never reached\nand which paths don't reach an ending."

        # Create list to select story variables
        self.mb = Menubutton (self.options_frame, text="Choose Story Variables  \u25BC", borderwidth=1, relief="solid", bg="white", activebackground = "white", state=DISABLED)
        self.mb.grid(row=5, column=0, padx=3, pady=4, sticky="w")
        self.mb.menu  =  Menu(self.mb, tearoff = 0, bg = "white")
        self.mb["menu"] = self.mb.menu

        self.B3 = Button(self.options_frame, text = "Verify", width = "15", borderwidth=1, relief="solid", command=self.onVerifyClick, state=DISABLED)
        self.B3.grid(row=10, padx=0, pady=10, ipadx=10)
        
        # Create "Select path" section
        L2 = Label(self.options_frame, text="------- Select path -------")
        L2.grid(row=11, pady=5)

        self.tooltips_items[L2] = "Select which path you wish to\nanalyse on the second tree."

        # Create list of story paths
        self.path_list = [""]
        self.path_selected = StringVar(win)

        self.pathList = ttk.Combobox(self.options_frame, textvariable = self.path_selected)   
        self.pathList.config(width="18", state='disabled')
        self.pathList.grid(row=12, pady=5)

        # Create the buttons to load selected path and to load the graph
        self.B4 = Button(self.options_frame, text = "Show Path", width = "15", borderwidth=1, relief="solid", command=self.onSeePathClick, state=DISABLED)
        self.B4.grid(row=13, padx=0, pady=5, ipadx=10)

        load_graph = partial(self.loadGraph, 1)
        self.B7 = Button(self.options_frame, text = "Show Vars. Timeline", width = "15", borderwidth=1, relief="solid", command=load_graph, state= DISABLED)
        self.B7.grid(row=14, padx=0, pady=5, ipadx=10)

        # Create right frame
        self.right_frame = Frame(win, width=w*0.13, height=h*0.694, bg='skyblue')
        self.right_frame.grid(row=0, column=1, padx=10, pady=5)

        # Create frame for the "full tree" inside right_frame
        self.full_tree = Frame(self.right_frame, width=w*0.36, height=h*0.58)
        self.full_tree.grid(row=0, column=0, padx=15, pady=10)

        # Create frame for the "small tree" inside right_frame
        self.small_tree = Frame(self.right_frame, width=w*0.36, height=h*0.58)
        self.small_tree.grid(row=0, column=1, padx=15, pady=10)

        # Create Dialog Trees
        self.dot = Digraph(strict= True)
        self.dot2 = Digraph(strict= True)

        # Create bottom_frame
        bottom_frame = Frame(win, width=w*0.13, height=h*0.347, bg='skyblue')
        bottom_frame.grid(row=1, column=1, padx=10, pady=0)

        # Create frame for "full tree's" textbox inside bottom_frame
        self.full_text = Frame(bottom_frame, width=w*0.326, height=h*0.29)
        self.full_text.grid(row=1, column=0, padx=15, pady=0)

        # Create frame for "small tree's" textbox inside bottom_frame
        self.small_text = Frame(bottom_frame, width=w*0.326, height=h*0.29)
        self.small_text.grid(row=1, column=1, padx=15, pady=0)

        # Create scrolltext
        self.txt = scrolledtext.ScrolledText(self.full_text, undo=True, width = 57, height=13)
        self.txt2 = scrolledtext.ScrolledText(self.small_text, undo=True, width= 57, height=13)

        # Display scrolltext in bottom_frame
        self.txt.grid(row=0, column=0)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(padx=10, pady=10, expand=True)

        # Display scrolltext in bottom_frame
        self.txt2.grid(row=0, column=0)
        self.txt2['font'] = ('consolas', '12')
        self.txt2.pack(padx=10, pady=10, expand=True)

        #self.story_var = StringVar(win)
        self.tk_checkboxes = []
        
        self.color_th = StringVar(win)
        self.color_th.trace("w", self.changeVerifyButton)
        
        self.color_end = StringVar(win)
        self.color_end.trace("w", self.changeVerifyButton)
     
        #Create help frame
        extra_frame = Frame(win, width=w*0.13, height=h*0.694, bg='skyblue')
        extra_frame.grid(row=1, column=0, padx=0, pady=0)

        # Create button to toogle the tooltips
        self.B5 = Button(extra_frame, text = "Toogle Tooltips", width="18", borderwidth=1, relief="solid", command=create_Tooltips)
        self.B5.grid(row=0, column=0, padx=7, pady=5)
        
        # Create button to save results to a pdf
        self.B6 = Button(extra_frame, text = "Save Report", width="18", borderwidth=1, relief="solid", command=print_PDF, state=DISABLED)
        self.B6.grid(row=1, column=0, padx=7, pady=0)

        # Just an empty label for design purposes
        self.L3 = Label(extra_frame, text="", width = "5", bg = "skyblue", fg = "green")
        self.L3.grid(row=2, column = 0)

    def onChooseFileClick(self):
        win.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.json*")))
    
        # If user selects cancel, reload window
        while not win.filename:
            win.filename = filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*")))
    
        name = os.path.basename(os.path.normpath(win.filename))
        self.file_name.set(name)

        self.B2.config(state=NORMAL) # turn "Submit" button active

    def onSubmitClick(self):
        global s
        
        self.B2.config(state=DISABLED)
        self.B6.config(state=DISABLED)
        self.mb.config(state=NORMAL)

        Reset_Paths()
        self.selected_vars = []
        
        if (s is not None):
            Reset()

        self.tk_checkboxes = [0] * 6
    
        # Transform checkbox list items in tk.IntVar()
        for i in range(len(self.tk_checkboxes)):
            self.tk_checkboxes[i] = tk.IntVar()

        # Activate checkboxes
        for i, item in enumerate(self.checkboxes_list):
            item.config(variable = self.tk_checkboxes[i], state=NORMAL)

        # Activate labels and entries
        for item in self.labels_list:
            item.config(state=NORMAL)

        create_story()

        # Create list of all story variables
        self.story_vars = {}
        
        for item in s.all_vars:
            a = tk.IntVar()
            a.set(0)
            self.story_vars[str(item)] = a
            
        self.mb.menu.delete(0, 20)

        for item in self.story_vars:
            self.mb.menu.add_checkbutton(label=str(item), onvalue=1, offvalue=0, variable = self.story_vars[item], command=self.changeVerifyButton)

        # Create list with colors
        color_list = ["blue", "red", "green", "orange", "purple"]

        # Create colorMenu widget with list of story variabled
        colorM = ttk.Combobox(self.options_frame, textvariable = self.color_th, values= color_list)   
        colorM.config(width="9", state="readonly")
        colorM.grid(row=7, sticky='e')
        colorM.bind("<<ComboboxSelected>>",lambda e: self.options_frame.focus()) # Move focus to another widget to avoid the blue highlight
        colorM.current(0) 

        # Create colorMenu widget with list of story variabled
        colorEndM = ttk.Combobox(self.options_frame, textvariable = self.color_end, values= color_list)   
        colorEndM.config(width="9", state="readonly")
        colorEndM.grid(row=2, sticky='e')
        colorEndM.bind("<<ComboboxSelected>>",lambda e: self.options_frame.focus()) # Move focus to another widget to avoid the blue highlight
        colorEndM.current(2)

    def onVerifyClick(self):
        global s
        global results_str
        global results_path
        global flag_path

        self.B3.config(state=DISABLED)
        self.B4.config(state=DISABLED)

        for item in self.story_vars:
            if (self.story_vars[item].get() == 1 and item not in self.selected_vars):
                self.selected_vars.append(item)
            elif (self.story_vars[item].get() == 0 and item in self.selected_vars):
                self.selected_vars.remove(item)
          
        s.vars_end_values = [[] for i in range(len(gui.selected_vars))]
        s.thr_passages = [[] for i in range(len(gui.selected_vars))]
        self.graphValues = [[] for i in range(len(gui.selected_vars))]

        Reset()

        if (all(self.tk_checkboxes[x].get() == 0 for x in range(6))):
            results_str = "Warning: No Analysis Condition was selected.\nPlease select an analysis condition and Verify again.\n\n"

            # insert results_str in in txt gui  
            self.txt.insert('end', results_str)

        if ( all(self.story_vars[x].get() == 0 for x in self.story_vars) and (self.tk_checkboxes[2].get() == 1 or self.tk_checkboxes[3].get() == 1)) :
            results_str = "Warning: No Story Variable was selected.\nPlease select a Story Variable and Verify again.\n"
        
            # insert results_str in in txt gui  
            self.txt.insert('end', results_str)
            
            # disable txt edit and scroll textbox to the bottom
            self.txt.configure(state ='disabled')
            self.txt.yview(END)

            self.txt2.insert(tk.INSERT, "")
            self.txt2.configure(state ='disabled')


            pass

        elif len(self.selected_vars) > 3:
            results_str = "Warning: More than 3 Story Variables were selected.\nPlease select three or less Story variables to analyse.\n"
        
            # insert results_str in in txt gui  
            self.txt.insert('end', results_str)

        else:
        
            # add different color to titles
            title_str = ""
            self.txt.tag_config('title', foreground="blue")

            if (self.tk_checkboxes[0].get() == 1):
                title_str = "*********************************************************\n"
                title_str = title_str + "                    NUMBER OF PATHS                    \n"
                title_str = title_str + "*********************************************************\n\n"
            
                pdf_text[0] += title_str

            # insert title_str in in txt gui       
            self.txt.insert('end', title_str, 'title')                      
            
            # run code that verifies story
            start()

            if (self.tk_checkboxes[0].get() == 1):
                results_str = results_str + "\nThe total number of paths is: " + str(s.number_paths) + "\n\n"
                pdf_text[0] += results_str
                self.txt.insert('end', results_str)

            if (self.tk_checkboxes[1].get() == 1):
                results_str = ""
                
                title_str = "*********************************************************\n"
                title_str = title_str + "                 ENDINGS HIT PERCENTAGE                 \n"
                title_str = title_str + "*********************************************************\n\n"

                pdf_text[0] += title_str

                # insert title_str in in txt gui      
                self.txt.insert('end', title_str, 'title')  
                
                total = s.number_paths - len(s.lost_paths)
                for i in s.list_endings_count:
                    if i in s.lost_plot:
                        results_str = results_str +"There's " + str(s.list_endings_count[i]) + " paths to " + i + ". Hit percentage: 0%\n"
                    else:
                        results_str = results_str +"There's " + str(s.list_endings_count[i]) + " paths to " + i + ". Hit percentage: " + str(round(s.list_endings_count[i]*100/total))+ "%\n"
                results_str =  results_str + "\n"
                update_Tree("full","endings", -1, -1)
                
                pdf_text[0] += results_str
                
                # insert results_str in in txt gui  
                self.txt.insert('end', results_str)

            if (self.tk_checkboxes[4].get() == 1):
                results_str = ""

                title_str = "*********************************************************\n"
                title_str = title_str + "                      STROKE POINTS                      \n"
                title_str = title_str + "*********************************************************\n\n"

                pdf_text[0] += title_str

                # insert title_str in in txt gui       
                self.txt.insert('end', title_str, 'title')  

                results_str = results_str + "The following passages are visited in all paths:\n"
                for i in s.stroke_points:
                    results_str = results_str + "['" + str(i) + "']\n"
                    self.dot.node(i, penwidth="3")
                    
                    if (flag_path == 1):
                        self.dot2.node(i, penwidth="3")

                results_str = results_str + "\n"
                pdf_text[0] += results_str
                
                # insert results_str in in txt gui  
                self.txt.insert('end', results_str)
            
            if (self.tk_checkboxes[5].get() == 1):
                results_str = ""

                title_str = "\n*********************************************************\n"
                title_str = title_str + "                       LOST PLOT                        \n"
                title_str = title_str + "*********************************************************\n\n"

                pdf_text[0] += title_str

                # insert title_str in in txt gui       
                self.txt.insert('end', title_str, 'title')  
            
                # Check paths that don't reach an ending
                if len(s.lost_paths) > 0 :          
                    results_str = results_str + "There is/are " +  str(len(s.lost_paths)) + " path(s) that can't reach an ending:" 
                    
                    for item in s.lost_paths:
                        results_str = results_str + "\nPATH #: " + item + "\n"
                else:
                    results_str = results_str + "All paths reach an ending. Everything OK.\n"

                # Check paassages that are never visited
                if len(s.lost_plot) > 0:
                    results_str = results_str +  "\nThe following passages are never reached: \n"
                    
                    for i in s.lost_plot:
                        results_str = results_str + str(i) + "\n"
                    
                else:
                    results_str = results_str + "\nAll passages are reached. Everything OK.\n"

                pdf_text[0] += results_str
                
                # insert results_str in in txt gui  
                self.txt.insert('end', results_str)

            if (self.tk_checkboxes[2].get() == 1):
                results_str = ""

                title_str =  "*********************************************************\n"
                title_str = title_str + "                VARIABLES ENDING VALUES                  \n"
                title_str = title_str + "*********************************************************\n\n"

                pdf_text[0] += title_str

                # insert title_str in in txt gui       
                self.txt.insert('end', title_str, 'title')

                for i in range(len(s.vars_end_values[0])):
                    results_str = results_str + "PATH #" + str(i+1) + ": \n"
                    for name in self.selected_vars:
                        index = self.selected_vars.index(name)
                        results_str = results_str + "Variable [" + name + "] ending value is: " + str(s.vars_end_values[index][i]) + "\n"
                    results_str = results_str + "\n"
                

                pdf_text[0] += results_str
                
                # insert results_str in in txt gui  
                self.txt.insert('end', results_str)
            
            if (self.tk_checkboxes[3].get() == 1):
                results_str = ""

                title_str = "*********************************************************\n"
                title_str = title_str + "           VARIABLES VALUES INSIDE THRESHOLD             \n"
                title_str = title_str + "*********************************************************\n\n"
        
                pdf_text[0] += title_str

                # insert title_str in in txt gui       
                self.txt.insert('end', title_str, 'title')  

                if (s.thr_str == ""):
                    s.thr_str = s.thr_str + "There are 0 passages where the story variable has values inside the selected threshold.\n"
                    results_str = results_str + s.thr_str + "\n"
                else:
                    results_str = results_str + s.thr_str + "\n"

                pdf_text[0] += results_str
                
                # insert results_str in in txt gui  
                self.txt.insert('end', results_str)

            if (flag_path == 1):

                # Add the value of story variable inside each passage's node
                for name in s.small_sequence:
                    for i in range(s.size):
                        if s.story.get("passages")[i].get("name") == name:
                            if "(set: $" in s.story.get("passages")[i].get("text"):
                                s.update_variables(s.story.get("passages")[i].get("text"))
            
                            # Add values of variables to the graph
                            for val in self.selected_vars:
                                self.graphValues[self.selected_vars.index(val)].append(s.all_vars[val])

                            # Write variables values for each passage on log
                            if (self.tk_checkboxes[2].get() == 1):
                                txt = name
                                for val in self.selected_vars:
                                    txt += "\n" + val +  " = " + str(s.all_vars[val])

                                self.dot2.node(name, label = txt)

                # Print paths's story to txt2
                for item in s.small_sequence:
                    for p_index in range(s.size):
                        if s.story.get("passages")[p_index].get("name") == str(item) :
                            results_path = results_path + "\n\n---- " + str(item) + " ----\n\n"
                            results_path = results_path + s.story.get("passages")[p_index].get("text")
                
                # If path can't reach an ending print ERROR
                for item in s.lost_paths:
                    if str(self.path_selected.get()) == "PATH #" + str(item.split("\n",1)[0]):
                        results_path = results_path + "\n\n>>> ERROR: This path couldn't reach an ending! <<<\n"
                
                # insert all text in results_path in txt2 gui
                pdf_text[1] += results_path  
                self.txt2.insert(tk.INSERT, results_path)
                self.txt2.configure(state ='disabled')

            # Create node and add edges to the passages in lost_plot if they connect
            if len(s.lost_plot) > 0:            
                    for i in s.lost_plot:
                        self.dot.node(i)
                        for j in range(s.size):
                            if s.story.get("passages")[j].get("name") == i:
                                links = s.story.get("passages")[j].get("links")
                                if links is not None: 
                                    link = links[0].get("link")
                                    self.dot.edge(i, link, penwidth = "1")

            # disable txt edit and scroll textbox to the bottom
               
        self.txt.configure(state ='disabled')
        self.txt.yview(END)
        create_Tree()

        if (flag_path == 0):
            path_list = []
            
            for i in range(s.number_paths):
                path_list.append("PATH #" + str(i+1))
                
            self.pathList = ttk.Combobox(self.options_frame, textvariable = self.path_selected, values= path_list)   
            self.pathList.config(width="18", state="readonly")
            self.pathList.grid(row=12, pady=0)
            self.pathList.current(0)

            self.path_selected.trace("w", self.changeSeePathButton)
            self.B4.config(state=NORMAL)
            
    def onSeePathClick(self):
        global flag_path
        
        flag_path = 1
        self.B7.config(state=NORMAL)
        self.onVerifyClick()

    def changeVerifyButton(self, *args):
        self.B3.config(state=NORMAL)
        self.L3.config(text = "")
    
    def changeSeePathButton(self, *args):
        self.B4.config(state=NORMAL)
        self.L3.config(text = "")
    
    def loadGraph(self, cond):
        global s

        self.B6.config(state=NORMAL)

        plt.rcParams['toolbar'] = 'None'
        fig = plt.figure(num='Variables Evolution Graph')

        x = []

        # Create x-axis
        for i in s.small_sequence:
            x.append(i)

        # Colors for each variable selected
        dot_color_list = ["blue", "green", "red"]

        # Plotting the lines points
        for value in self.graphValues:
            index = self.graphValues.index(value)
            plt.plot(x, value, label = str(self.selected_vars[index]), color = "grey", linestyle='dotted', marker='o', markerfacecolor= dot_color_list[index], markeredgecolor=dot_color_list[index])

        plt.xticks(rotation=90)
        plt.tight_layout()
        
        # Naming the x-axis 
        plt.xlabel('Passages')
    
        # Naming the y-axis 
        plt.ylabel('Variables Values') 

        plt.legend(loc='best')

        if cond == 0:
            # Save image for pdf printing
            dir_path = os.path.dirname(os.path.realpath(__file__)) 
            plt.savefig(str(dir_path)+ "/tmp/testplot.png", bbox_inches = "tight")
            plt.close()
        else:
            # Display Graph
            plt.show()
            plt.close('all')
            
    def reset_GUI(self):

        # Clear Scrolledtext Contents
        self.txt.delete('1.0', END)            
        self.txt2.delete('1.0', END)            
        
        # Clear Dialog Trees Contents
        self.dot.clear()                        
        self.dot2.clear()                       

        # Destroy left, right, bottom and top frame
        self.full_tree.destroy()
        self.small_tree.destroy()

        # Create right_frame
        self.right_frame = Frame(win, width=w*0.13, height=h*0.694, bg='skyblue')
        self.right_frame.grid(row=0, column=1, padx=10, pady=5)
        
        # Create full_tree frame
        self.full_tree = Frame(self.right_frame, width=w*0.36, height=h*0.58)
        self.full_tree.grid(row=0, column=0, padx=15, pady=10) 

        # Create full_tree frame
        self.small_tree = Frame(self.right_frame, width=w*0.36, height=h*0.58)
        self.small_tree.grid(row=0, column=1, padx=15, pady=10)

        # Create bottom_frame
        self.bottom_frame = Frame(win, width=w*0.13, height=h*0.35, bg='skyblue')
        self.bottom_frame.grid(row=1, column=1, padx=10, pady=0)
        
        # Create full_tree frame
        self.full_text = Frame(self.bottom_frame, width=w*0.326, height=h*0.29)
        self.full_text.grid(row=1, column=0, padx=15, pady=0)

        # Create small_tree frame
        self.small_text = Frame(self.bottom_frame, width=w*0.326, height=h*0.29)
        self.small_text.grid(row=1, column=1, padx=15, pady=0)

        self.txt = scrolledtext.ScrolledText(self.full_text, undo=True, width= 57, height=13)
        self.txt2 = scrolledtext.ScrolledText(self.small_text, undo=True, width= 57, height=13)

        # Display scrolltext in bottom_frame
        self.txt.grid(row=0, column=0)
        self.txt['font'] = ('consolas', '12')
        self.txt.pack(padx=10, pady=10, expand=True)
        
        # Display scrolltext in bottom_frame
        self.txt2.grid(row=0, column=0)
        self.txt2['font'] = ('consolas', '12')
        self.txt2.pack(padx=10, pady=10, expand=True)
                
class Story:
    ''' 
    The Story object contains all the attributes and information about the selected story (JSON format)

    '''

    def __init__(self, story, size):
        self.story = story
        self.number_paths = 0
        self.size = size
        self.lost_plot = []
        self.lost_paths = []
        self.stroke_points = []
        self.sequence = []
        self.small_sequence =[]
        self.all_vars = {}
        self.vars_end_values = []
        self.not_accepted = []
        self.thr_passages = []
        self.thr_str = ""
        self.list_endings_count = {}

    def treating_endings(self):
        for i in range(self.size):
            if (self.story.get("passages")[i].get("links") == None and s.story.get("passages")[i].get("tags") != None and "ENDING-POINT" in s.story.get("passages")[i].get("tags")):
                name = self.story.get("passages")[i].get("name")
                self.list_endings_count[name] = 0
    
    def get_all_passages(self):
        for i in range(self.size):
            self.lost_plot.append(self.story.get("passages")[i].get("name"))

    def update_sequence(self, name):
        self.sequence.append(name)
        if name in self.lost_plot:
            self.lost_plot.remove(name)

    def get_var_values(self):
        for name in self.sequence:
            for i in range(len(s.story["passages"])):
                if s.story.get("passages")[i].get("name") == name and "(set: $" in s.story.get("passages")[i].get("text"):
                    self.update_variables(s.story.get("passages")[i].get("text"))
    
    def update_variables(self, variable_string):
        sets = re.findall(r'\(set.*?\)', variable_string)

        for s in sets:
            sect_1 = s.split('(')[1].split(')')[0]      # get set statement                            
            s_split = sect_1.split()                          
            var_name = s_split[1][1:]                   # variable name
            cond = s_split[2]                           # extract condition: to, += or -=
            #var_value = 0
            var_value = int(s_split[3])                 # variable value

            if cond == "to":
                self.all_vars[var_name] = var_value
            elif cond == "+=" and var_name in self.all_vars:
                self.all_vars[var_name] += var_value
            elif cond == "-=" and var_name in self.all_vars:
                self.all_vars[var_name] -= var_value


    def if_treatment(self, passage_text):
        
        # update variables values in the sequence
        for name in self.sequence:
            for i in range(self.size):
                if self.story.get("passages")[i].get("name") == name:
                    if "(set: $" in self.story.get("passages")[i].get("text"):
                        self.update_variables(self.story.get("passages")[i].get("text"))   

        # re.findall() returns a list of all the "if statement" strings found
        statements = re.findall(r'\(.*?\]\]', passage_text)
        
        for s in statements:
            sect_1 = s.split('(')[1].split(')')[0]      # get if statement section

            sect_2 = s.split('[[')[1].split(']]')[0]    # get the "do this" of each if
            
            # in case there's a "->" or "|"". This is from Twine's documentation
            if "->" in sect_2:
                sect_2 = sect_2.split('->')[1]
            elif "|" in sect_2:
                sect_2 = sect_2.split('|')[1]
                         
            self.not_accepted.append(sect_2)                  

            s_split = sect_1.split()                    # split the if statement
            var1 = s_split[1][1:]                       # extract var1, story variable expected
            cond = s_split[2]                           # extract condition: is, <, >, <= or >=
            var2 = s_split[3]                           # extract var2, integer expected

            if len(s_split) > 4 :
                var3 = s_split[-1]                      # extract var3, integer expected
            
            # check if var1 is a story variable and if var2 is an integer
            if var1 in list(self.all_vars) and var2.lstrip('-+').isdigit():
            
                if (cond == "is"):
                    if (self.all_vars[var1] == int(var2)):
                        self.not_accepted.remove(sect_2)                    
                
                elif len(s_split) > 4 and var3.lstrip('-+').isdigit():
                    if (self.all_vars[var1] in range(int(var2), int(var3))):
                        self.not_accepted.remove(sect_2)  
                
                elif (cond == "<"):
                    if (self.all_vars[var1] < int(var2)):
                        self.not_accepted.remove(sect_2) 
                
                elif (cond == ">"):
                    if (self.all_vars[var1] > int(var2)):
                        self.not_accepted.remove(sect_2)  
            
                elif (cond == "<="):
                    if (self.all_vars[var1] <= int(var2)):
                        self.not_accepted.remove(sect_2)  
            
                elif cond == ">=":
                    if (self.all_vars[var1] >= int(var2)):
                        self.not_accepted.remove(sect_2)  
            else:
                print ("ERROR")

    def reset_Story(self):
        global gui

        self.number_paths = 0
        self.lost_paths = []
        self.lost_plot = []
        self.thr_passages = [[] for i in range(len(gui.selected_vars))]
        self.vars_end_values = [[] for i in range(len(gui.selected_vars))]
        self.not_accepted = []
        self.list_endings_count = {}
        self.thr_str= ""

class Tooltip(object):
    '''
    Create a Tooltip object
    '''
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

        self.x = 0
        self.y = 0

    def enter(self, event=None):
        global gui

        if (gui.flag_tooltips == 1):
            
            # Create "hit" area
            x, y, cx, cy = self.widget.bbox("insert")
            
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20

            # creates a toplevel window
            self.tw = tk.Toplevel(self.widget)

            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))

            # create label for the tooltip
            label = tk.Label(self.tw, text=self.text, justify='left',
                        background='#ffffe0', relief='solid', borderwidth=1,
                        font=("tahoma", "8", "normal"))
            label.pack(ipadx=1)
    
    def close(self, event=None):
        global gui
        if (gui.flag_tooltips == 1 and self.tw):
            self.tw.destroy()

#=============================================================================
# Creates all Tooltips objects
#=============================================================================
def create_Tooltips():
    global gui
    global tools
    #global flag_tooltips  

    gui.flag_tooltips = 1

    for item in gui.tooltips_items:
        tools.append( Tooltip(item, text = gui.tooltips_items[item]) )

    gui.B5.config(command=toogle_Tooltips, bg = "palegreen")

#=============================================================================
# Turns Tooltips widget ON and OFF
#============================================================================= 
def toogle_Tooltips():
    global gui
 
    if (gui.flag_tooltips == 1) :
        gui.B5.config(bg = "whitesmoke", borderwidth = 1)
        gui.flag_tooltips = 0
    else:
        gui.B5.config(command=toogle_Tooltips, bg = "palegreen")
        gui.flag_tooltips = 1

#=============================================================================
# Creates a new Story object
#=============================================================================
def create_story():
    global s
    
    with open(win.filename, encoding="utf8") as f:
        story_tmp = json.load(f)
        s = Story(story_tmp, len(story_tmp.get("passages")))

        # Setup Story Variables
        for i in range(len(s.story["passages"])):
            if "(set: $" in s.story.get("passages")[i].get("text"):
                s.update_variables(s.story.get("passages")[i].get("text"))
    
#=============================================================================
# Resets variables and the Story and GUI objects
#=============================================================================
def Reset():
    global results_str
    global results_path
    global s
    global gui
    global edge_sizes
    global pdf_text
    
    results_str = ""
    results_path = ""
    edge_sizes = {}
    pdf_text =["",""]
    
    s.reset_Story()
    gui.reset_GUI()

#=============================================================================
# Resets the story variables' and the paths' lists
#=============================================================================
def Reset_Paths():
    global flag_path
    global s
    global gui

    # Reset Variable List
    if (s != None):
        s.all_vars = {}

    # Reset "Path Select"
    gui.path_list = [""]
    gui.path_selected = StringVar(win)
    gui.path_selected.set(gui.path_list[0]) # default value

    gui.pathList = ttk.Combobox(gui.options_frame, textvariable = gui.path_selected, values = gui.path_list)   
    gui.pathList.config(width="18", state="disabled")
    gui.pathList.grid(row=12, pady=0)
    
    gui.B4.config(state=DISABLED)
    flag_path = 0

#=============================================================================
# Creates PDF files with Story Validator's log information
#=============================================================================
def print_PDF():
    global gui
    global pdf

    pdf = PDF()
    dir_path = os.path.dirname(os.path.realpath(__file__)) 

    page_w = pdf.w - 2*pdf.l_margin

    # Add Story Validator's log information to pdf
    pdf.add_page()
    pdf.bounds()
    
    pdf.set_font("Arial", size=20)

    pdf.cell(page_w, 10, "Story Validator's Log", align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10, style="B")
    pdf.write(12, "Story File selected: ")
    pdf.set_font("Arial", size=10)
    pdf.write(12, str(gui.file_name.get()))
    pdf.ln(7)
    
    pdf.set_font("Arial", size=10, style="B")
    pdf.write(12, "Analysis Conditions")
    pdf.ln(10)

    data = [['Condition','Selected?'],
            ['Number of Paths', 'Yes' if gui.tk_checkboxes[0].get() == 1 else 'No'],
            ['Ending Hit Percentage', 'Yes' if gui.tk_checkboxes[1].get() == 1 else 'No'],
            ['Variables Ending Value', 'Yes' if gui.tk_checkboxes[2].get() == 1 else 'No'],
            ['Variable value by given Treshold', 'Yes' if gui.tk_checkboxes[3].get() == 1 else 'No'],
            ['Stroke Points', 'Yes' if gui.tk_checkboxes[4].get() == 1 else 'No'],
            ['Lost Plot', 'Yes' if gui.tk_checkboxes[5].get() == 1 else 'No']]
   
    # Draw data on table headings
    pdf.set_font("Arial", size=10, style="B")
    for info in data[0]:
        pdf.cell(page_w/2, 7, str(info), border=1)

    pdf.ln(7)
    
    # Draw the remaining data on table fields/cells
    pdf.set_font("Arial", size=10)
    for row in data[1:]:
        for info in row:
            pdf.cell(page_w/2, 7, str(info), border=1)
 
        pdf.ln(7)

    pdf.set_font("Arial", size=10, style="B")
    pdf.write(12, "Story Variables selected: ")
    pdf.set_font("Arial", size=10)
    
    # Make selected_vars list into a comma-separated string
    joined_var_str = ", ".join(gui.selected_vars)
    
    pdf.write(12, joined_var_str)
    pdf.ln(5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.write(12, "Selected Threshold: ")
    pdf.set_font("Arial", size=10)
    pdf.write(12, "(MIN = " + str(gui.entryMin.get()) + " , MAX = " + str(gui.entryMax.get()) + ")")
    pdf.ln(5)
    pdf.set_font("Arial", size=10, style="B")
    pdf.write(12, "Selected Path: ")
    pdf.set_font("Arial", size=10)
    pdf.write(12, str(gui.path_selected.get().split("#",1)[1]))

    # Add Full Dialog Tree to pdf
    pdf.add_page()
    pdf.bounds()
    pdf.set_font("Arial", size=20)
    pdf.cell(0,10,"Full Dialog Tree",0,0,'C')

    pdf.setup_image(str(dir_path)+ "/tmp/TREE.png")

    # Add Full Results to pdf
    pdf.add_page()
    pdf.bounds()
    
    pdf.set_font("Arial", size=10)
    pdf.write(5, pdf_text[0])

    # Add Small Dialog Tree to pdf
    pdf.add_page()
    pdf.bounds()
    pdf.set_font("Arial", size=20)
    pdf.cell(0,10,"SELECTED: " + gui.path_selected.get(),0,0,'C')

    pdf.setup_image(str(dir_path)+ "/tmp/TREE2.png")

    # Add Small Results to pdf
    pdf.add_page()
    pdf.bounds()
    
    pdf.set_font("Arial", size=10)
    pdf.ws = 3
    pdf.write(5, pdf_text[1])

    # Add Graph
    pdf.add_page()
    pdf.bounds()
    pdf.set_font("Arial", size=20)
    pdf.cell(0,10,"Story Variables Evolution",0,0,'C')
    gui.loadGraph(0)
    pdf.setup_image(str(dir_path)+ "/tmp/testplot.png")

    # Print values to pdf
    file_name = str((gui.file_name.get()).split('.', 1)[0])
    file_path = str(dir_path)+ "/SavedLogs/" + file_name + "_REPORT.pdf"

    i = 1
    while Path(file_path).is_file():
        # File exists
        file_path = str(dir_path)+ "/SavedLogs/" + file_name + "_REPORT(" + str(i) + ").pdf"
        i += 1

    pdf.output(file_path)
    
    del pdf
    gui.L3.config(text = "Saved")

#=============================================================================
# Creates Dialog Tree using Graphviz
#============================================================================= 
def create_Tree():
    global gui
    global tools

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Save Dialog Tree to image
    gui.dot.render(filename='TREE', directory= str(dir_path)+ "/tmp", view=False, format='png')
    gui.dot2.render(filename='TREE2', directory= str(dir_path)+ "/tmp", view=False, format='png')

    # Draw Full Dialog Tree in GUI
    image = PhotoImage(file= str(dir_path)+ "/tmp/TREE.png")
    show_image = ScrollableImage(gui.full_tree, image=image, width=540, height=490)
    show_image.pack(padx=5, pady=5)

    # Draw Small Dialog Tree in GUI
    image = PhotoImage(file= str(dir_path)+ "/tmp/TREE2.png")
    show_image2 = ScrollableImage(gui.small_tree, image=image, width=540, height=490)
    show_image2.pack(padx=5, pady=5)

#=============================================================================
# Updates Dialog Trees
#=============================================================================
def update_Tree(tree_type, option, attr, name):
    global s
    global gui

    if (tree_type == "small"):
        for el in range(len(s.sequence[:-1])):
            gui.dot2.edge(s.sequence[el], s.sequence[el+1])
    else:
        if (gui.tk_checkboxes[0].get() == 0):
            for el in range(len(s.sequence[:-1])):
                gui.dot.edge(s.sequence[el], s.sequence[el+1], penwidth = "1")

    if(option == "paths" and tree_type == "full"):
        for el in range(len(s.sequence[:-1])):
            edge = str(s.sequence[el]) + str(s.sequence[el+1])
            if (edge in edge_sizes):
                edge_sizes[edge] += 1
                gui.dot.edge(s.sequence[el], s.sequence[el+1], label = " " + str(edge_sizes[edge]))
            else:
                edge_sizes[edge] = 1
                gui.dot.edge(s.sequence[el], s.sequence[el+1], label = str(edge_sizes[edge]))
    
    elif (option == "endings"):
        if (tree_type == "full"):
            total = s.number_paths - len(s.lost_paths)
            color = str(gui.color_end.get()) +"s9"
            for i in s.list_endings_count:
                n = s.list_endings_count[i]
                if (n == 0):
                    gui.dot.node(i, colorscheme= color, fillcolor = "1", style="filled")
                else: 
                    if n > 9:
                        gui.dot.node(i, colorscheme= color, fillcolor = "9", style="filled", label = i + "\n"+ str(round(s.list_endings_count[i]*100/total)) + "% ")
                    else:
                        gui.dot.node(i, colorscheme= color, fillcolor = str(s.list_endings_count[i]), style="filled", label = i + "\n"+ str(round(s.list_endings_count[i]*100/total)) + "% ")
        else:
            if s.sequence[-1] in s.list_endings_count: 
                gui.dot2.node(s.sequence[-1], style="filled")
    
    elif (option == "lost"):
        if (tree_type == "full"):
            gui.dot.node(s.sequence[-1], shape = "box")         
            for j in s.lost_plot:
                gui.dot.node(j)
        else:
            gui.dot2.node(s.sequence[-1], shape = "box")
            gui.dot2.node("x", width = "0", shape = "plaintext", fontsize="30", fontname = "Arial Black")
            gui.dot2.edge(s.sequence[-1], "x", arrowhead = "none", style = "dotted")

    elif(option == "variables"):

        # Change to correct colors
        if gui.color_th.get() == "blue":
            color = ["skyblue", "RoyalBlue1", "blue"]
        elif gui.color_th.get() == "red":
            color = ["salmon", "red", "red4"]
        elif gui.color_th.get() == "green":
            color = ["greenyellow", "forestgreen", "darkgreen"]
        elif gui.color_th.get() == "orange":
            color = ["tan1", "DarkOrange1", "OrangeRed2"]
        elif gui.color_th.get() == "purple":
            color = ["MediumPurple1", "purple", "purple4"]

        if (tree_type == "full"):       
            this_min = int(gui.entryMin.get())
            this_max = int(gui.entryMax.get())

            times = 0
            for n in attr:
                val = s.all_vars.get(n)
                index = attr.index(n)
                if (val >= this_min and val <= this_max):
                    s.thr_passages[index].append(name)
                    if (times == 0):
                        times = 1
                        gui.dot.node(name, fillcolor= color[0], style="filled")
                    elif (times == 1):
                        times = 2
                        gui.dot.node(name, fillcolor= color[1], style="filled")
                    else:
                        gui.dot.node(name, fillcolor= color[2], style="filled")
        else:
            counter = 0
            for index in range(len(s.thr_passages)):
                for item in s.thr_passages[index]:
                    counter = sum(x.count(item) for x in s.thr_passages)
                    if counter > 2 :
                        gui.dot2.node(item, fillcolor= color[2], style="filled")
                    elif counter == 1 :
                        gui.dot2.node(item, fillcolor= color[0], style="filled")
                    else :
                        gui.dot2.node(item, fillcolor= color[1], style="filled") 

#=============================================================================
# Initial setup to selected Story
#=============================================================================
def start():
    global s

    # Setup to story endings
    s.treating_endings()

    # Setup to all passages names
    s.get_all_passages()

    # Add first passage name to sequence
    name = s.story.get("passages")[0].get("name")
    s.update_sequence(name)

    # Traverse Dialogue
    visit_passages(0)

#=============================================================================
# Travels through all the passages
#=============================================================================
def visit_passages(index):
    global s
    global gui
    global flag_path
    global results_str
    global results_path
    
    passage = s.story.get("passages")[index]
    passage_text = passage.get("text")

    # Assess "if" statements when existent
    if "(if: $" in passage_text:
        s.if_treatment(passage_text)

    # Check for links and visit them
    links = passage.get("links")

    if links is not None:
        size = len(links)
      
        # Choose a link
        for link_index in range(size):
            next_passage = links[link_index].get("link") #name of next passage
            if next_passage not in s.not_accepted:
                s.update_sequence(next_passage)

                for p_index in range(s.size):
                    if s.story.get("passages")[p_index].get("name") == next_passage :
                        visit_passages(p_index)
            else:
                if all(item in s.not_accepted for item in list(s.list_endings_count)): 
                    s.number_paths += 1
                    s.lost_paths.append(str(s.number_paths) + "\n" + str(s.sequence))
                    s.get_var_values() #calculate variables values
                    for name in gui.selected_vars:
                        index = gui.selected_vars.index(name)
                        s.vars_end_values[index].append(s.all_vars.get(name))

                    update_Tree("full", "lost", -1, -1)

                    if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                        # add different color to titles
                        title_str = ""
                        gui.txt2.tag_config('title', foreground="blue")

                        title_str = title_str + "******************************************************\n"
                        title_str = title_str + "                  SELECTED PATH #: " + str(s.number_paths)+ "                  \n"
                        title_str = title_str + "********************************************************"
                        
                        pdf_text[1] += title_str
                        gui.txt2.insert('end', title_str, 'title')

                        # sequence of the path selected
                        s.small_sequence = s.sequence.copy() 
                        update_Tree("small","", -1, -1)
                    
                    if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                        update_Tree("small", "lost", -1, -1)
                    
                    if (gui.tk_checkboxes[0].get() == 1):
                        results_str = results_str +"PATH #: " + str(s.number_paths)+ "\n"
                        results_str = results_str + str(s.sequence) + "\n\n"
                        update_Tree("full","paths", -1, -1)
                    
                    if (gui.tk_checkboxes[3].get() == 1): 
                        for name in s.sequence:
                            for i in range(s.size):
                                if s.story.get("passages")[i].get("name") == name:
                                    if "(set: $" in s.story.get("passages")[i].get("text"):
                                        s.update_variables(s.story.get("passages")[i].get("text"))
                                    update_Tree("full","variables", gui.selected_vars, name)

                        if any(len(x) != 0 for x in s.thr_passages):
                            s.thr_str = s.thr_str + "PATH # " + str(s.number_paths) + ":\n"
                            for name in gui.selected_vars:
                                index = gui.selected_vars.index(name)
                                if len(s.thr_passages[index]) != 0 :
                                    s.thr_str = s.thr_str + "[" + name + "]\n"
                                    s.thr_str = s.thr_str + "On the following passages: " + str(s.thr_passages[index]) + "\n\n"

                            if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                                update_Tree("small","variables", -1, -1)

                        s.thr_passages = [[] for i in range(len(gui.selected_vars))]
                            
                s.not_accepted.remove(next_passage)
        
        # Clean last passage from sequence
        del s.sequence[-1] 
    
    else:
        s.number_paths += 1
        s.get_var_values() # Calculate variables values
        
        for name in gui.selected_vars:
            index = gui.selected_vars.index(name)
            s.vars_end_values[index].append(s.all_vars.get(name))
        

        # If passage not and Ending Point, we have a lost plot
        if (passage.get("name") not in s.list_endings_count):
            s.lost_paths.append(str(s.number_paths) + "\n" + str(s.sequence))
            update_Tree("full", "lost", -1, -1)
            if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                    update_Tree("small", "lost", -1, -1)

        if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
            # Add different color to titles
            title_str = ""
            gui.txt2.tag_config('title', foreground="blue")

            title_str = title_str + "********************************************************\n"
            title_str = title_str + "                   SELECTED PATH #: " + str(s.number_paths)+ "                  \n"
            title_str = title_str + "********************************************************"
            
            pdf_text[1] += title_str
            gui.txt2.insert('end', title_str, 'title')

            # Sequence of the path selected
            s.small_sequence = s.sequence.copy()
            
            update_Tree("small","", -1, -1)

        if (gui.tk_checkboxes[0].get() == 1):
            results_str = results_str +"PATH #: " + str(s.number_paths)+ "\n"
            results_str = results_str + str(s.sequence) + "\n\n"
            update_Tree("full","paths", -1, -1)
            
        else:
            update_Tree("full", "none", -1, -1)

        if (gui.tk_checkboxes[1].get() == 1):
            
            # Update ending count
            if passage.get("name") in s.list_endings_count:
                s.list_endings_count[passage.get("name")] += 1                    
                
            if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                update_Tree("small","endings", -1, -1)
        
        if (gui.tk_checkboxes[3].get() == 1): 
            for name in s.sequence:
                for i in range(s.size):
                    if s.story.get("passages")[i].get("name") == name:
                        if "(set: $" in s.story.get("passages")[i].get("text"):
                            s.update_variables(s.story.get("passages")[i].get("text"))
                        update_Tree("full","variables", gui.selected_vars, name)

            if any(len(x) != 0 for x in s.thr_passages):
                s.thr_str = s.thr_str + "PATH # " + str(s.number_paths) + ":\n"
                for name in gui.selected_vars:
                    index = gui.selected_vars.index(name)
                    if len(s.thr_passages[index]) != 0 :
                        s.thr_str = s.thr_str + "[" + name + "]\n"
                        s.thr_str = s.thr_str + "On the following passages: " + str(s.thr_passages[index]) + "\n\n"

                if (flag_path == 1 and gui.path_selected.get() != "" and gui.path_selected.get() == "PATH #"+ str(s.number_paths)):
                    update_Tree("small","variables", -1, -1)

                s.thr_passages = [[] for i in range(len(gui.selected_vars))]
            
        
        if(gui.tk_checkboxes[4].get() == 1):
            if len(s.stroke_points) == 0:
                s.stroke_points = s.sequence.copy()
            else:
                tmp = []
                for i in s.sequence:
                    if i in s.stroke_points:
                        tmp.append(i)
                s.stroke_points = tmp.copy()
            
        
        del s.sequence[-1]    

#=============================================================================
# Create Tkinter Instance
#=============================================================================
win = tk.Tk()
win.title("Story Validator")
w, h = win.winfo_screenwidth(), win.winfo_screenheight()
win.minsize(w, h)
win.state('zoomed')
win.resizable(False, False)
win.config(bg="skyblue") 

#=============================================================================
# Global Variables
#=============================================================================
gui = GUI(win)
s = None
flag_path = 0               # changes value to 1 when path_list is created
edge_sizes = {}             # a dictonary of sizes of each tree edge 
results_str= ""             # string with results to print to txt GUI
results_path = ""           # string with results to print to txt2 GUI
pdf_text = ["", ""]         

tools = []
pdf = None                  #pdf object

# Start the main loop
win.mainloop()