# Import necessary modules
from functools import lru_cache
import customtkinter as ctk
from collections.abc import Callable
from customtkinter import IntVar
import matplotlib.pyplot as plt
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from numpy._typing._array_like import NDArray
from typing import Any
from PIL import ImageTk, Image
import os
from CTkMessagebox import CTkMessagebox
import pandas as pd
import os
from BackendModule import HistogramMaker, ScatterMaker


#--------------------------------------

# Main Application Class
class App(ctk.CTk):
    # Initialize the application
    def __init__(self) -> None: 
        super().__init__()
        self.std_bool =False
        self.no_of_std_float = 0
        
        # Configure window
        self.title("Physics Plot Maker")
        self.geometry("700x650")

        # 1. Configure the root window's grid to expand
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Initialize text variables
        self.first_text = """In this app we will model data to make plots, \n
        there are two different types of plots you can make using this program. \n
        then you can pick model like linear, quadratic, exponential amd many other and this app will display \n
        the best fit equation and many more values that are needed for scientific modeling and plotting \n
        These steps would be explained in detail as you go further ahead"""
        self.second_text = """Here you will provide the path link to the excel file to input data to get a Scatter Plot 
        \n Please make sure that the file is closed before plotting"""
        self.txt_lin_m: str = "m (slope)"
        self.txt_lin_b: str = "y (intercept)"
        self.txt_quad_a: str = "a (quadratic coefficient)"
        self.txt_quad_b: str = "b (linear coefficient)"
        self.txt_quad_c: str = "c (constant term)"
        self.txt_inv_a: str = "a (numerator coefficient)"
        self.txt_inv_b: str = "b (intercept)"
        self.txt_exp_a: str = " A (exponential coefficient)"
        self.txt_exp_b: str = " b (power coefficient)"
        self.txt_log_a: str = "a (logarithmic coefficient)"
        self.txt_log_b: str = "b (horizontal shift term)"
        self.txt_log_c: str = "c (vertical shift term)"
        
        # Setup UI Tabs
        self.setup_ui_tabs()
    
    # Setup UI Tabs    
    def setup_ui_tabs(self):
        """Creates the tab view and places content within the first tab. This method  configures the grid layout for proper resizing
        and it also add label to the outputs tab."""
        
        # Create the CTkTabview
        self.tabview = ctk.CTkTabview(master=self, command=self.tabular_swther)
        # Use grid instead of pack for better integration with the root window's grid
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Add the tabs
        # We store references to the internal frames created by add()
        self.main_frame = self.tabview.add("Plot Picker")
        self.main_screen()
        self.empty_frame = self.tabview.add("Outputs")

        # Configure the grid of the specific frame we are adding content to
        # (The tabview handles its own internal layout, we just configure the added frames)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        # Call main_screen to populate 'Plot Picker'
        self.tabview.set("Plot Picker")
        self.add_label_to_outputs_tab()
         
    #main Screen
    def main_screen (self) -> None:
        """ Destroys the main frame widgets and creates the main screen with plot options
        """
        
        # Destroy previous widgets if any
        try:
            self.button_frame.destroy()
        except:
            pass
        
        # Clear existing widgets in main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Clear Advance Tab if it exists   
        try:
            self.tabview.delete("Advance Tab")
        except:
            pass  
            
        # Add main screen widgets
        # Main label    
        self.label = ctk.CTkLabel(master=self.main_frame, text=self.first_text)
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Sub-label; label 2
        self.label2 = ctk.CTkLabel(master=self.main_frame, text="Which plot do you want to make")
        self.label2.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        #button 1
        self.button_1 = ctk.CTkButton(master=self.main_frame, text="Scatter", command=self.plot_sel_scat)
        self.button_1.grid(row=2, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        
        # Button 2
        self.button_2 = ctk.CTkButton(master=self.main_frame, text="Histogram", command=self.plot_sel_hist)
        self.button_2.grid(row=2, column=1, padx=(10, 20), pady=(0, 20), sticky="ew")
        
   
    #scatter plot selector
    def plot_sel_scat (self) -> None:
        """ Destroys the main frame widgets and calls the scatter data input screen
        """
        
        try:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
                self.button_frame = ctk.CTkFrame(self)
        except:
            pass
        
        # function to call scatter data input screen
        self.scat_data()
        
    
    
    #histogram plot selector 
    def plot_sel_hist (self) -> None:
        """ Destroys the main frame widgets and calls the histogram data input screen
        """
        # Clear existing widgets in main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Call histogram data input screen
        self.hist_data()


    #scatter data input
    def scat_data(self) -> None:
        """This is the main input screen for scatter, this function creates all the labels, entries and checkboxes needed for scatter plot input
        1. Path to excel file
        2. X values column number
        3. Sigma X values column number (optional)
        4. Y values column number
        5. Sigma Y values column number (optional)
        6. X-axis label
        7. Y-axis label
        8. Title of the plot
        9. Next and Previous buttons (these buttons are created using a separate function)
        
        This function is primarily called by the plot_sel_scat function when the user selects scatter plot option from the main screen.
        It also can be called by the s3_to_prev function when the user clicks the Previous button from the model picking screen
         
        """
        
        # configuring the frame
        self.main_frame.grid_rowconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(7, weight=1)
        self.main_frame.grid_rowconfigure(8, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_rowconfigure(10, weight=1)
        self.main_frame.grid_rowconfigure(11, weight=1)
        self.main_frame.grid_rowconfigure(12, weight=1)
        
        #path label & entry
        # adding the label
        self.label1 = ctk.CTkLabel(master=self.main_frame, text=self.second_text)
        self.label1.grid(row=0, column=0, columnspan=2, padx=10, pady=6, sticky="nsew")
        
        in_labal_2 =ctk.CTkLabel(self.main_frame, text="Path to Excel file; .xlsx file supported only")
        in_labal_2.grid(row=1, column=0, columnspan=2, pady=1, sticky="n")
        self.scat_path_entry = ctk.CTkEntry(self.main_frame, width=500, placeholder_text= "Enter the Path to Excel File")
        self.scat_path_entry.grid(row=2, column=0, columnspan=4, pady=5)
        
        #x quantities
        #x values column label & entry
        self.label4 = ctk.CTkLabel(master=self.main_frame, text="Add the column number where the x values are")
        self.label4.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        self.x_column_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the Column Number ")
        self.x_column_entry.grid(row=4, column=0, columnspan=2, padx=20,  pady=5, sticky="w")
        
        #sigma x values column label & entry
        self.std_x_chkbox = ctk.CTkCheckBox(self.main_frame, text="Do you have sigma x value[s]", command=self.toggle_sigma_x_checkbox)
        self.std_x_chkbox.grid(row=5, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")
        self.label_sigx = ctk.CTkLabel(master=self.main_frame, text="Add the column number where sigma x values are")
        self.x_sig_column_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the Column Number ")
        
        #Checkbox for single or multiple sigma x values
        self.single_std_x_chkbox = ctk.CTkCheckBox(self.main_frame, text="Check this box if you have a single sigma x value")
        
        #x-axis label 
        self.label7 = ctk.CTkLabel(master=self.main_frame, text="Enter the x-axis label")
        self.label_x_axis = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "x-axis [units]  ")
        self.label7.grid(row=9, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        self.label_x_axis.grid(row=10, column=0, columnspan=2, padx=20,  pady=5, sticky="w")
        
        
        #y quantities       
        #y values column label & entry
        self.label_y_1 = ctk.CTkLabel(master=self.main_frame, text="Add the column number where the y values are")
        self.label_y_1.grid(row=3, column=0, columnspan=2, padx=30, pady=5, sticky="e")
        self.y_column_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the Column Number ")
        self.y_column_entry.grid(row=4, column=0, columnspan=2, padx=50,  pady=5, sticky="e")
        
        #sigma y values column label & entry
        self.std_y_chkbox = ctk.CTkCheckBox(self.main_frame, text="Do you have sigma y value[s]", command=self.toggle_sigma_y_checkbox)
        self.std_y_chkbox.grid(row=5, column=0, columnspan=2, pady=5, padx= 40, sticky = "e")
        self.label_y_2 = ctk.CTkLabel(master=self.main_frame, text="Add the column number where sigma y values are")
        self.y_column_sig_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the Column Number ")
        
        #Checkbox for single or multiple sigma y values  
        self.single_std_y_chkbox = ctk.CTkCheckBox(self.main_frame, text="Check this box if you have a single sigma y value", command=self.toggle_sigma_y_checkbox)
        
        #y-axis label
        self.label_y_1 = ctk.CTkLabel(master=self.main_frame, text="Enter the y-axis label")
        self.label_y_axis = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "y-axis [units] ")
        self.label_y_1.grid(row=9, column=0, columnspan=2, padx=120, pady=5, sticky="e")
        self.label_y_axis.grid(row=10, column=0, columnspan=2, padx=50,  pady=5, sticky="e")

        #title label and entry
        self.label_title = ctk.CTkLabel(master=self.main_frame, text="Enter the title")
        self.entry_title = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "y-axis [units] vs x-axis [units]")
        self.label_title.grid(row=10, column=0, columnspan=4, padx=5, pady=5, sticky="s")
        self.entry_title.grid(row=11, column=0, columnspan=4, padx=5,  pady=5, sticky="s")
        
        #back button
        self.nxt_prev_btns("Previous", self.main_screen, "Next", self.second_screen_destroy)
    
    #histogram data input
    def hist_data (self) -> None:
        """This is the main input screen for histogram, this function creates all the labels, entries and checkboxes needed for histogram plot input
        1. Path to excel file
        2. Data values column number
        3. Number of bins (optional)
        4. Title of the plot
        This function is primarily called by the plot_sel_hist function when the user selects histogram plot option from the main screen.
        """
        
        # configuring the frame
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(8, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_rowconfigure(10, weight=1)
        self.main_frame.grid_rowconfigure(11, weight=1)
        self.main_frame.grid_rowconfigure(12, weight=50)
        self.main_frame.grid_rowconfigure(13, weight=4)
        
        #path label & entry
        label_hist_path = ctk.CTkLabel(master=self.main_frame, text="Here you will provide the path link to the excel file to input data to get a histogram \n Please make sure that the file is closed ")
        label_hist_path.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        in_labal1: None =ctk.CTkLabel(self.main_frame, text="Path to Excel file; .xlsx file supported only").grid(row=1, column=0, columnspan=2, pady=5)
        self.hist_path_entry = ctk.CTkEntry(self.main_frame, width=500, placeholder_text= "Enter the Path to Excel File")
        self.hist_path_entry.grid(row=2, column=0, columnspan=4, pady=5,)
        
        # values of the histogram
        label_hist_col = ctk.CTkLabel(master=self.main_frame, text="Add the column number where the data is, in the Excel file")
        label_hist_col.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.hist_column_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the Column Number ")
        self.hist_column_entry.grid(row=4, column=0, columnspan=4, pady=5,)
        
        # number of bins if someone wants to change
        label5 = ctk.CTkLabel(master=self.main_frame, text="Enter the number of bins if you want to change (default is 10)")
        label5.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.hist_bin_entry = ctk.CTkEntry(self.main_frame, width=200, placeholder_text= "Enter the number of bins ")
        self.hist_bin_entry.grid(row=6, column=0, columnspan=4, pady=5,)        
        
        # Histogram title
        title_label = ctk.CTkLabel(master=self.main_frame, text= "Enter the Title of the Histogram")
        title_label.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.hist_title_entry = ctk.CTkEntry(self.main_frame, width=250, placeholder_text= "Default Title is: Data Histogram ")
        self.hist_title_entry.grid(row=8, column=0, columnspan=4, pady=5,)  
        # button for plotting
        button1 = ctk.CTkButton(self.main_frame, text= "Plot",command= self.hist_output)
        button1.grid(row=13, column= 0, padx=0, pady=(0, 20), sticky = "se")
        
        #back button
        button = ctk.CTkButton(self.main_frame, text= "Previous",command=self.main_screen)
        button.grid(row=13, column= 0, padx=20, pady=(0, 20), sticky = "sw")
    
    #Histogram output
    def hist_output (self) -> None:
        
        """
        This method creates the output for histogram. It retrieves user inputs, validates them, and generates the histogram plot.
        It also manages the display of optional parameters like standard deviation and normalization based on user selections.
        1. Retrieves user inputs from entry fields.
        2. Validates the inputs and handles errors with message boxes.
        3. Generates the histogram plot using the HistogramMaker class.
        4. Displays the plot in the output tab and provides an option to save the plot as an image.
        This function is primarily called by the hist_data function when the user clicks the plot button.
        """
        
        #destroy previous widget in output frame
        for widget in self.empty_frame.winfo_children():
            widget.destroy()
        
        # get user input
        hist_path: str = self.hist_path_entry.get()
        bin_entry:str = self.hist_bin_entry.get()
        title_entry:str = self.hist_title_entry.get()
        
        #Handle optional standard deviation input
        try:
            if self.toggle_hist_optional_visibility() == 1:
                no_of_std_str:str = self.entry_std.get()
                if not self.entry_std.get():
                    self.no_of_std_float = 1
                try:
                    self.no_of_std_float =float(no_of_std_str)
                except TypeError:
                    CTkMessagebox(title="Error", message="Enter Numbers")
                    return
        except:
            pass
        
        
        #Check for the file path
        try:
            df = pd.read_excel(hist_path, header=None)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load Excel file: {str(e)}")
            return
        
        
        # if the file path is wrong
        if not hist_path:
            CTkMessagebox(title="Error", message="Please enter a valid path to the Excel file.")
            return
        
        # if the user doesn't enter the bins 
        if not bin_entry:
            self.no_of_bis = 10
        else:
            try:
                self.no_of_bis = int(bin_entry)
            except TypeError:
                CTkMessagebox(title="Error", message="Number of bins must be in integers")
                return
            
        #check to see if the column number is in correct format
        try:
            self.hist_column:int = int(self.hist_column_entry.get())
        except ValueError:
            CTkMessagebox(title="Error", message= "X and Y column numbers must be integers.")
            return
        
        #check for title
        if not title_entry:
            self.hist_title = "Data Histogram"
        else:
            self.hist_title = title_entry
            
        #check for the data in the file
        try:
            self.hist_x_vals: NDArray = np.array(df.iloc[:, self.hist_column-1].values)

            self.histo: HistogramMaker =HistogramMaker(self.hist_x_vals, self.hist_title, self.std_bool, self.no_of_std_float, self.draw_checker(), self.normal_check(), bins= self.no_of_bis)
            ax = self.histo.histogramcreater()
            canvas = FigureCanvasTkAgg(ax, master= self.empty_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
            self.tabview.set("Outputs")
            self.action_button1: Callable[[], None] = self.histo.histogram_saver
            self.save_button_hist =ctk.CTkButton(master=self.empty_frame, text="Save Plot as Image",width=100, command=self.action_button1)
            self.save_button_hist.place(relx=0.95, rely=0.1, anchor="se")
            if not self.check_tab_exist("Advance Tab"):
                self.Advance_frame = self.tabview.add("Advance Tab")
                self.hist_advance_tab()
        except Exception as e:
            CTkMessagebox(title="Error",message= f"Failed to extract the values from the file: {str(e)}")
            return
    
    #check if tab exists    
    def check_tab_exist(self, name) -> bool:  
        """
        Check if a tab with the given name exists in the tabview.
        """
        try:
            self.tabview.tab(name)
            return True
        except ValueError:
            return False

    #histogram advance tab
    def hist_advance_tab(self) -> None:
        
        """This function is used to create advance tabs for histogram plot
        1. Standard Deviation checkbox
        2. Standard Deviation number entry and button
        3. Checkbox for normalization
        This function is called by the hist_output function when the user plots a histogram.
        """
        
        self.Advance_frame.grid_rowconfigure(2, weight=1)
        self.Advance_frame.grid_rowconfigure(3, weight=1)
        self.Advance_frame.grid_rowconfigure(4, weight=1)
        self.Advance_frame.grid_rowconfigure(5, weight=1)
        # standard deviation checkbox
        self.std_chkbox = ctk.CTkCheckBox(self.Advance_frame, text="Do you want to Display the Standard Deviation Value on the Histogram", command=self.toggle_hist_optional_visibility)
        self.std_chkbox.grid(row=1, column=0, columnspan=4, pady=5, padx= 70)
        
        # standard deviation number entry and button
        self.entry_std = ctk.CTkEntry(self.Advance_frame, width= 240, font=("Arial", 9), placeholder_text="Enter desired STDs away from mea; i.e. 1, 1.5, 2")
        self.std_dis_chkbox = ctk.CTkCheckBox(self.Advance_frame, text="Do you want to mark the standard Deviation on the plot", command=self.draw_checker)
        
        #checkbox for normalization
        self.normal_his_check = ctk.CTkCheckBox(self.Advance_frame,text="Check this if you want a normalized Histogram", command=self.normal_check)
        self.normal_his_check.grid(row=4, column=0, pady=10, padx=70)
    
    # check for normalization        
    def normal_check(self) -> bool:
        """This function checks if the normalization checkbox is checked or not.
        Returns:
            bool: _True if checked, False otherwise.
        """
        try:
            if self.normal_his_check.get() == 1:
                return True
            else:
                return False 
        except:
            return False
    
    # check for drawing standard deviation
    def draw_checker(self) -> bool:
        """This function checks if the draw standard deviation checkbox is checked or not.
        Returns:
            bool: True if checked, False otherwise.
        """
        try:
            if self.std_dis_chkbox.get() == 1:
                return True
            else:
                return False 
        except:
            return False
            
        
        
    # toggle histogram optional visibility    
    def toggle_hist_optional_visibility(self) -> int:
        """
        This function is called every time the checkbox is clicked.
        Returns:
            int: 1 if the checkbox is checked, 0 otherwise.
        """
        # Check if the checkbox is currently checked (value is 1 for checked, 0 for unchecked)
        #self.hist_advance_tab()
        if self.std_chkbox.get() == 1:
            
            # If checked, use grid() to make the entry widget appear
            self.entry_std.grid(row=2, column=0, columnspan=2, padx=70, pady=10)
            self.std_dis_chkbox.grid(row=3, column=0, columnspan=4, pady=5, padx= 70)
            self.std_bool = True
            return 1
        else:
            # If unchecked, use grid_remove() to hide the entry widget
            self.entry_std.grid_remove()
            self.std_dis_chkbox.grid_remove()
            self.std_bool = False
            return 0

    # toggle sigma x checkbox
    def toggle_sigma_x_checkbox(self) -> None:
        """
        This function is called every time the checkbox is clicked.
        """
        # Check if the checkbox is currently checked (value is 1 for checked, 0 for unchecked)
        if self.std_x_chkbox.get() == 1:
            # If checked, use grid() to make the entry widget appear
            self.label_sigx.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="w")
            self.x_sig_column_entry.grid(row=7, column=0, columnspan=2, padx=20,  pady=5, sticky="w")
            self.single_std_x_chkbox.grid(row=8, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")

        else:
            # If unchecked, use grid_remove() to hide the entry widget
            self.label_sigx.grid_remove()
            #self.x_column_entry.grid_remove()
            self.single_std_x_chkbox.grid_remove()
            self.x_sig_column_entry.grid_remove()
            #self.label7.grid_remove()
            #  self.label_x_axis.grid_remove()
    
    # toggle sigma y checkbox        
    def toggle_sigma_y_checkbox(self) -> None:
        """
        This function is called every time the checkbox is clicked.
        
        """
        # Check if the checkbox is currently checked (value is 1 for checked, 0 for unchecked)
        if self.std_y_chkbox.get() == 1:
            # If checked, use grid() to make the entry widget appear
            self.label_y_2.grid(row=6, column=0, columnspan=2, padx=30, pady=5, sticky="e")
            self.y_column_sig_entry.grid(row=7, column=0, columnspan=2, padx=50,  pady=5, sticky="e")
            self.single_std_y_chkbox.grid(row=8, column=0, columnspan=2, pady=5, padx= 40, sticky = "e")

        else:
            # If unchecked, use grid_remove() to hide the entry widget
            self.label_y_2.grid_remove()
            self.y_column_sig_entry.grid_remove()
            self.single_std_y_chkbox.grid_remove()

    #scatter data input screen destroyer
    def second_screen_destroy (self) -> None:
        """This function is used to destroy the scatter data input screen and call the model picking screen
        """

        if self.scatter_plot_input() == 2:
            self.plot_sel_scat()
        else:
                
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            
            self.model_picking_screen()
            self.nxt_prev_btns("Previous", self.s3_to_prev, text2= "Plot", cmd2=self.s3_to_next)
  
    #scatter to previous
    def s3_to_prev(self) -> None:
        """
        This method is used to go back to the scatter data input screen from the model picking screen
        1. Destroys current widgets in main frame
        2. Calls the scatter data input screen
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        try:

            for widget in self.empty_frame.winfo_children():
                widget.destroy()
        except:
            pass
        self.scat_data()            
    
    #scatter to next
    def s3_to_next(self):
        """
        This method is used to go to the output screen from the model picking screen
        1. Destroys current widgets in main frame
        2. Destroys current widgets in output frame
        3. Calls the scatter plot maker
        """
        
        try:
            for widget in self.empty_frame.winfo_children():
                widget.destroy()
        except:
            pass
        
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        self.scatter_plt_maker()
        #self.tabview.set("Outputs")
        self.current_tab = self.tabview.get()
        self.nxt_prev_btns("previous", self.swth_tb_fun)
        
    #switch tab function   
    def swth_tb_fun(self) -> None:
        """This method is used to switch between the plot picker tab and the outputs tab
        1. Destroys current widgets in button frame
        2. Switches to the other tab
        """
        
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        if self.current_tab== "Outputs":
            self.tabview.set("Plot Picker")
            self.current_tab = self.tabview.get()
            
            self.nxt_prev_btns("Previous", self.s3_to_prev, text2= "Plot", cmd2=self.s3_to_next)
        elif self.current_tab == "Plot Picker":
            self.current_tab = self.tabview.get()
            for widget in self.button_frame.winfo_children():
                widget.destroy()
            self.s3_to_prev()
        
    #model picking screen 
    def model_picking_screen(self) -> None:
        """This is the model picking screen for scatter plot, this function creates all the labels, radio buttons and checkboxes needed for model picking
        1. Radio buttons for model selection
        2. Checkboxes for best fit line, equation, R², σ
        3. Checkbox for advance tab
        This function is primarily called by the second_screen_destroy function when the user clicks the Next button from the scatter data input screen.
        
        """
    
        # configuring the frame 
        self.plt_chrecker = False
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(4, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)
        self.main_frame.grid_rowconfigure(7, weight=1)
        self.main_frame.grid_rowconfigure(8, weight=1)
        self.main_frame.grid_rowconfigure(9, weight=1)
        self.main_frame.grid_rowconfigure(10, weight=1)
        self.main_frame.grid_rowconfigure(11, weight=1)
        self.main_frame.grid_rowconfigure(12, weight=1)
        self.main_frame.grid_rowconfigure(13, weight=1)
        
        self.txt_pos1 ="Enter value"
        self.txt_pos2 ="Enter value"
        self.txt_pos3 ="Enter value"
        
        self.label1 = ctk.CTkLabel(master=self.main_frame, text="Pick one of the folloing to model and get a best fit line and equation")
        self.label1.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
        

        self.radvar = IntVar()
        self.model_1 = ctk.CTkRadioButton(self.main_frame, text="Linear Model", variable=self.radvar, value = 1, command=self.p1_button_function)
        self.model_1.grid(row=3, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")

        self.model_2 = ctk.CTkRadioButton(self.main_frame, text="Quadratic Model", variable=self.radvar, value = 2, command=self.p1_button_function)
        self.model_2.grid(row=4, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")
        self.model_3 = ctk.CTkRadioButton(self.main_frame, text="Inverse Square Model", variable=self.radvar, value = 3, command=self.p1_button_function)
        self.model_3.grid(row=5, column=0, columnspan=4, pady=5, padx= 40, sticky = "w")
        self.model_4 = ctk.CTkRadioButton(self.main_frame, text="Exponential Model", variable=self.radvar, value = 4, command=self.p1_button_function)
        self.model_4.grid(row=6, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")
        self.model_4 = ctk.CTkRadioButton(self.main_frame, text="Natural Nog", variable=self.radvar, value = 5, command=self.p1_button_function)
        self.model_4.grid(row=7, column=0, columnspan=2, pady=5, padx= 40, sticky = "w")
        self.line_show_ceckbox = ctk.CTkCheckBox(self.main_frame, text="Check this, if you want the best fit line plotted on the graph")
        self.line_show_ceckbox.grid(row=9, column=0, columnspan=4, pady=5, padx= 40, sticky="w")
        self.eq_show_ceckbox = ctk.CTkCheckBox(self.main_frame, text="Check this, if you want to display best fit equation on the graph")
        self.eq_show_ceckbox.grid(row=10, column=0, columnspan=4, pady=5, padx= 40, sticky="w")
        self.r2_show_ceckbox = ctk.CTkCheckBox(self.main_frame, text="Check this, if you want to display R² on the graph")
        self.r2_show_ceckbox.grid(row=11, column=0, columnspan=4, pady=5, padx= 40, sticky="w")
        self.sigmay_show_ceckbox = ctk.CTkCheckBox(self.main_frame, text="Check this, if you want to display σᵧ on the graph")
        self.sigmay_show_ceckbox.grid(row=12, column=0, columnspan=4, pady=5, padx= 40, sticky="w")
        self.math_output_ceckbox = ctk.CTkCheckBox(self.main_frame, text="Check this, if you want all mathematical details in a seperate tab", command=self.adv_scat_tab)
        self.math_output_ceckbox.grid(row=13, column=0, columnspan=4, pady=5, padx= 40, sticky="w")

    #advance scatter tab
    def adv_scat_tab(self) -> None:
        """This function is used to create advance tabs for scatter plot
        1. Checkbox for displaying parameters on plot legend
        2. Checkbox for displaying chi-squared on plot
        3. Checkbox for displaying reduced chi-squared on plot
        This function is called by the model_picking_screen function when the user selects the advance tab checkbox.
        """
        # configuring the frame
        if self.math_output_ceckbox.get() == 1:
            self.previous_tab = self.tabview.get()
            advance_frame = self.tabview.add("Advance Tab")
            scat_adv_lbl1 = ctk.CTkLabel(master=advance_frame, text="Here you will find all the mathematical details of the best fit line and model")
            scat_adv_lbl1.place(relx=0.5, rely=0.1, anchor="center")
            self.scat_adv_chbx1 = ctk.CTkCheckBox(advance_frame, text="Do you want to display the parameters on the plot legend")
            self.scat_adv_chbx1.place(relx=0.03, rely=0.18, anchor="w")
            self.scat_adv_chbx2 = ctk.CTkCheckBox(advance_frame, text="Do you want to display the chi-squared on the plot")
            self.scat_adv_chbx2.place(relx=0.03, rely=0.26, anchor="w")
            self.scat_adv_chbx3 = ctk.CTkCheckBox(advance_frame, text="Do you want to display the reduced chi-squared on the plot")
            self.scat_adv_chbx3.place(relx=0.03, rely=0.34, anchor="w")
            self.scat_adv_prnt_btn = ctk.CTkButton(advance_frame, text="Print Parameters to Console", command=self.scat_adv_print_params)
            self.scat_adv_prnt_btn.place(relx=0.1, rely=0.5, anchor="w")
            self.adv_txtbx = ctk.CTkTextbox(master=advance_frame, width=300, height=200)
        elif self.math_output_ceckbox.get() == 0:
            try:
                self.tabview.delete("Advance Tab")
            except:
                pass
            self.param_chkr = False
        
    #tabular switcher
    def tabular_swther(self) -> None:
        """This method is used to switch to the Outputs tab from the Advance Tab
        1. Sets the current tab to Outputs
        2. Destroys current widgets in button frame
        3. Configures the buttons for navigation
        """
        #change tab to other tabs
        try:
            self.current_tab = "Outputs"
            for widget in self.button_frame.winfo_children():
                widget.destroy()
            if self.tabview.get() == "Plot Picker":
                self.nxt_prev_btns("previous", self.swth_tb_fun, text2="Plot", cmd2=self.s3_to_next, adv_bool=False)
            elif self.tabview.get() == "Outputs":
                self.nxt_prev_btns("previous", self.swth_tb_fun, adv_bool=False)
            elif self.tabview.get() == "Advance Tab":
                self.nxt_prev_btns("Apply Changes", self.aply_changes, adv_bool=True)   
        except:
            pass
    
    #next and previous buttons method
    def nxt_prev_btns(self, text1, cmd1, text2=None, cmd2=None, adv_bool=False) -> None:
        """Separate method to create and configure the button sub-frame.
        Args:
            text1 (str): Text for the first button.
            cmd1 (Callable[[], None]): Command for the first button.
            text2 (str, optional): Text for the second button. Defaults to None.
            cmd2 (Callable[[], None], optional): Command for the second button. Defaults to None.
            adv_bool (bool, optional): If True, configures the button frame for advanced options. Defaults to False.
            """
    
        # Create buttons in the new frame
        self.button1 = ctk.CTkButton(self.button_frame, text=text1, command=cmd1)

        # Configure columns to space buttons apart
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        if adv_bool == True:
            self.button_frame.columnconfigure(1, weight=1)
        else:
            self.button_frame.columnconfigure(1, weight=0)
             
        if text2 is not None and cmd2 is not None:
            self.button2 = ctk.CTkButton(self.button_frame, text=text2, command=cmd2)

            # Grid buttons side-by-side in one row
            self.button1.grid(row=13, column=0, padx=10, pady=10, sticky="w")
            self.button2.grid(row=13, column=1, padx=380, pady=10, sticky="e")
        else:
            # Grid only the first button, centered
            self.button1.grid(row=13, column=0, columnspan=2, padx=10, pady=10, sticky="e")

        # Grid the button frame in the root window
        self.button_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

    def p1_button_function(self) -> None:
        """This function is called every time a radio button is selected.
        It updates the entry fields based on the selected model.
        """
        # Update entry fields based on selected model
        if self.radvar.get() == 1:
            try:
                self.fst_ges_entry.destroy()
                self.snd_ges_entry.destroy()
                self.thrd_ges_entry.destroy()
            except:
                pass
            try:
                self.fst_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos1)
                self.snd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos2)
                # Update placeholders for the linear model
                self.fst_ges_entry.configure(placeholder_text="Enter " + self.txt_lin_m)
                self.snd_ges_entry.configure(placeholder_text="Enter " + self.txt_lin_b)
                
                # Re-grid the entries
                self.fst_ges_entry.grid(row=8, column=0, columnspan=1, pady=5, padx=10,)
                self.snd_ges_entry.grid(row=8, column=1, columnspan=1, pady=5, padx=50,)
            except AttributeError:
                CTkMessagebox(title="Error", message= "Select Model to plot the  best fit line.")
                
        elif self.radvar.get() == 2:
            try:
                self.fst_ges_entry.destroy()
                self.snd_ges_entry.destroy()
                self.thrd_ges_entry.destroy()
            except:
                pass
            
            self.fst_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos1)
            self.snd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos2)
            self.thrd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos3)
            # Update placeholders for the quadratic model
            self.fst_ges_entry.configure(placeholder_text="Enter " + self.txt_quad_a)
            self.snd_ges_entry.configure(placeholder_text="Enter " + self.txt_quad_b)
            self.thrd_ges_entry.configure(placeholder_text="Enter " + self.txt_quad_c)
            # Re-grid the entries
            self.fst_ges_entry.grid(row=8, column=0, columnspan=1, pady=5, padx=20, sticky="w",) 
            self.snd_ges_entry.grid(row=8, column=1, columnspan=1, pady=5, padx=100,)
            self.thrd_ges_entry.grid(row=8, column=2, columnspan=1, pady=5, padx=40,)
            
        elif self.radvar.get() == 3: 
            try:
                self.fst_ges_entry.destroy()
                self.snd_ges_entry.destroy()
                self.thrd_ges_entry.destroy()
            except:
                pass
            
            self.fst_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos1)
            self.snd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos2)
            # Update placeholders for the inverse square model
            self.fst_ges_entry.configure(placeholder_text="Enter " + self.txt_inv_a)
            self.snd_ges_entry.configure(placeholder_text="Enter " + self.txt_inv_b)
            
            
            self.fst_ges_entry.grid(row=8, column=0, columnspan=1, pady=5, padx=10,)
            self.snd_ges_entry.grid(row=8, column=1, columnspan=1, pady=5, padx=50,)
        elif self.radvar.get() == 4:
            try:
                self.fst_ges_entry.destroy()    
                self.snd_ges_entry.destroy()    
                self.thrd_ges_entry.destroy()
            except: 
                pass
            self.fst_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos1)
            self.snd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos2)
            
            
            # Update placeholders for the exponential model
            self.fst_ges_entry.configure(placeholder_text="Enter " + self.txt_exp_a)
            self.snd_ges_entry.configure(placeholder_text="Enter " + self.txt_exp_b)
            
            
            self.fst_ges_entry.grid(row=8, column=0, columnspan=1, pady=5, padx=10,)
            self.snd_ges_entry.grid(row=8, column=1, columnspan=1, pady=5, padx=50,)        
    
        elif self.radvar.get() == 5:
            try:
                self.fst_ges_entry.destroy()
                self.snd_ges_entry.destroy()
                self.thrd_ges_entry.destroy()
            except:
                pass
            self.txt_pos1:str = "Enter"+self.txt_log_a
            self.txt_pos2:str = "Enter"+self.txt_log_b
            self.txt_pos3:str = "Enter"+self.txt_log_c
            
            self.fst_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos1)
            self.snd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos2)
            self.thrd_ges_entry = ctk.CTkEntry(self.main_frame, width= 205, placeholder_text=self.txt_pos3)
            # Update placeholders for the logarithmic model
            self.fst_ges_entry.configure(placeholder_text="Enter " + self.txt_log_a)
            self.snd_ges_entry.configure(placeholder_text="Enter " + self.txt_log_b)
            self.thrd_ges_entry.configure(placeholder_text="Enter " + self.txt_log_c)
            # Re-grid the entries
            self.fst_ges_entry.grid(row=8, column=0, columnspan=1, pady=5, padx=20, sticky="w",) 
            self.snd_ges_entry.grid(row=8, column=1, columnspan=1, pady=5, padx=100,)
            self.thrd_ges_entry.grid(row=8, column=2, columnspan=1, pady=5, padx=40,)
        elif self.radvar.get() is None:
            CTkMessagebox(title="Error", message= "Select a Model for .")
            
        else:
            
            self.snd_ges_entry.grid_remove()

    #scatter data input screen
    def input_scrn(self) -> None:
        """This is the scatter data input screen, this function creates all the labels and entry fields needed for scatter plot data input
        1. Labels and entry fields for file path, x column, y column
        2. Labels and entry fields for axis labels and title
        This function is primarily called by the scatter_data function when the user clicks the Next button from the initial scatter plot screen.
        """
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
    #scatter data input screen      
    def scatter_plot_input(self) -> None | int:
        """This is the scatter data input screen, this function creates all the labels and entry fields needed for scatter plot data input
        1. Labels and entry fields for file path, x column, y column
        2. Labels and entry fields for axis labels and title
        This function is primarily called by the scatter_data function when the user clicks the Next button from the initial scatter plot screen.
        """
        #try to get file path
        scat_path:str = self.scat_path_entry.get()
        if not scat_path:
            CTkMessagebox(title="Error", message="Please enter a valid path to the Excel file.")
            return 2
        #Check for file data
        try:
            df = pd.read_excel(scat_path, header=None)
        except Exception as e:
            CTkMessagebox(title="Error", message=f"Failed to load Excel file: {str(e)}")
            return 2
        
        try:            
            self.scat_x_column:int = int(self.x_column_entry.get())
            self.scat_y_column:int = int(self.y_column_entry.get())
        except ValueError:
            CTkMessagebox(title="Error", message= "X and Y column numbers must be integers.")
            return 2
        
        
        try:
            self.scat_x_vals: NDArray = np.array(df.iloc[:, self.scat_x_column-1].values)
            self.scat_y_vals: NDArray = np.array(df.iloc[:, self.scat_y_column-1].values)
            if len(self.scat_x_vals) != len(self.scat_y_vals):
                CTkMessagebox(title="Error", message="X and Y values must have the same length.")
                return 2
        except:
            CTkMessagebox(title="Error", message= "Something went wrong when extracting x and y values")
            return 2       
        
        # get sigma x and y if checked
        if self.std_x_chkbox.get() == 1:
            try:
                col_idx_x: int = int(self.x_sig_column_entry.get()) - 1
                sigx_len = len(df.iloc[:, col_idx_x].values)
                
                if self.single_std_x_chkbox.get() == 1:
                    single_val_x = df.iloc[0, col_idx_x]
                    
                    self.scat_sigx_val: NDArray = np.full(len(self.scat_x_vals), single_val_x)
                elif self.single_std_x_chkbox.get() == 0 and sigx_len == len(self.scat_x_vals):
                    self.scat_sigx_val:NDArray = np.array(df.iloc[:, col_idx_x].values)
                elif self.single_std_x_chkbox.get() == 0 and sigx_len != len(self.scat_x_vals):
                    CTkMessagebox(title="Error", message="Something went wrong with sigma x extraction")
                    return 2
                self.scat_sigx_val2 = self.scat_sigx_val        
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Extraction failed: {e}")
                
                return 2
        else:
            self.scat_sigx_val2 = None     

        # get sigma y
        if self.std_y_chkbox.get() == 1:
            try:
                col_idx_y: int = int(self.y_column_sig_entry.get()) - 1
                sigy_len = len(df.iloc[:, col_idx_y].values)
                
                if self.single_std_y_chkbox.get() == 1:
                    # Extract the single scalar value from the first row of the column
                    single_val = df.iloc[0, col_idx_y]
                    self.scat_sigy_val: NDArray = np.full(len(self.scat_y_vals), single_val)
                elif self.single_std_y_chkbox.get() == 0 and sigy_len == len(self.scat_y_vals):
                    # Extract the entire column as an array
                    self.scat_sigy_val:NDArray = np.array(df.iloc[:, col_idx_y].values)
                elif self.single_std_y_chkbox.get() == 0 and sigy_len != len(self.scat_y_vals):
                    CTkMessagebox(title="Error", message="Something went wrong with sigma x extraction")
                    return 2
                self.scat_sigy_val2 = self.scat_sigy_val  

            except Exception as e:
                CTkMessagebox(title="Error", message=f"Extraction failed: {e}")
                return 2
        else:
            self.scat_sigy_val2 = None 
              

        # get axis labels and title
        self.xname_entry:str = self.label_x_axis.get()
        self.yname_entry:str = self.label_y_axis.get()
        self.title_entry:str = self.entry_title.get()
        if not self.xname_entry: self.xname_entry:str = "x-axis [units]"
        if not self.yname_entry: self.yname_entry:str = "y-axis [units]"
        if not self.title_entry: self.title_entry:str = "y-axis [units] vs x-axis [units]"

    #scatter plot maker
    def scatter_plt_maker(self) -> None:
        """This function is used to create the scatter plot and display it in the output tab.
        1. Retrieves user selections from model picking screen
        2. Creates the scatter plot using the ScatterMaker class
        3. Displays the plot in the output tab
        """
        
        # retrieve user selections from model picking screen
        l_sc: bool= t_f_checker(int(self.line_show_ceckbox.get()))
        eq_sc: bool= t_f_checker(int(self.eq_show_ceckbox.get()))
        r2_sc: bool= t_f_checker(int(self.r2_show_ceckbox.get()))
        sigmaout_sc: bool= t_f_checker(int(self.sigmay_show_ceckbox.get()))
        if self.math_output_ceckbox.get() == 1:
            self.param_chkr: bool = t_f_checker(int(self.scat_adv_chbx1.get()))
            self.chi_sq_chkr: bool = t_f_checker(int(self.scat_adv_chbx2.get()))
            self.red_chi_sq_chkr: bool = t_f_checker(int(self.scat_adv_chbx3.get()))
    

        dis_chkr_bools: list[bool] = [l_sc, eq_sc, r2_sc, sigmaout_sc, self.param_chkr, self.chi_sq_chkr, self.red_chi_sq_chkr]
        
        # get initial parameter guesses based on selected model
        if self.radvar.get() in [1,3,4]:
            try:
                param1 = float(self.fst_ges_entry.get())
                param2 = float(self.snd_ges_entry.get())
                self.params: list |None = [param1, param2]
            except:
                CTkMessagebox(title="Waring", message= "Caution: Proceeding with default guesses of 1s. \n " +"Since no valid guesses were provided.")
                self.params: list |None = [1.0, 1.0]
        elif self.radvar.get() in [2,5]:
            try:
                param1 = float(self.fst_ges_entry.get())
                param2 = float(self.snd_ges_entry.get())
                param3 = float(self.thrd_ges_entry.get())
                self.params: list | None= [param1, param2, param3]
            except:
                CTkMessagebox(title="Waring", message= "Caution: proceeding with default parameters of 1. \n " +"Since no valid parameters were provided.")
                self.params: list | None = [1.0, 1.0, 1.0]
        elif dis_chkr_bools == [False, False, False, False]:
            self.params: list | None = None
        elif self.radvar.get() not in  [1,2,3,4,5] and any(dis_chkr_bools):
            if sum (dis_chkr_bools) >=1:
                CTkMessagebox(title="Error", message= "one or more checkbox[es] have been checked before selecting a model. \n Please select a Model.")
            self.nxt_prev_btns("Previous", self.swth_tb_fun, text2="Plot", cmd2=self.s3_to_next)
            self.model_picking_screen()
        else:
            CTkMessagebox(title="Error", message= "Please select a model to plot the best fit line.")
            self.nxt_prev_btns("Previous", self.swth_tb_fun, text2="Plot", cmd2=self.s3_to_next)
            self.model_picking_screen()


        
        
        
        
        self.scater = ScatterMaker(self.scat_x_vals, self.scat_y_vals, self.params, self.scat_sigx_val2, self.scat_sigy_val2, self.radvar.get(),
                                self.xname_entry, self.yname_entry, self.title_entry, dis_chkr_bools)
        ax1 = self.scater.sccater_creater()
        canvas = FigureCanvasTkAgg(ax1, master= self.empty_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.action_button2: Callable[[], None] = self.scater.scat_saver
        self.save_button_scat =ctk.CTkButton(master=self.empty_frame, text="Save Plot as Image",width=100, command=self.action_button2)
        self.save_button_scat.place(relx=0.95, rely=0.1, anchor="se")
        self.tabview.set("Outputs")
        self.plt_chrecker: bool = True
           
    #add label to outputs tab
    def add_label_to_outputs_tab(self) -> None:
        self.generic_text_label = ctk.CTkLabel(master=self.empty_frame, text="This tab will display the Plots" , font=("Arial", 25))
        self.generic_text_label.pack(side="top", fill= "both")
    
    #apply changes from advance tab    
    def aply_changes(self):
        try:
            if self.radvar.get() not in [1,2,3,4,5]:
                CTkMessagebox(title="Error", message="Select a model to apply advanced settings.")
                return
            else:
                
                self.param_chkr: bool = t_f_checker(int(self.scat_adv_chbx1.get()))
                self.chi_sq_chkr: bool = t_f_checker(int(self.scat_adv_chbx2.get()))
                self.red_chi_sq_chkr: bool = t_f_checker(int(self.scat_adv_chbx3.get()))
                self.tabview.set(self.previous_tab)
               
                
                self.swth_tb_fun()
            
                
        except:
            self.param_chkr = False
            self.chi_sq_chkr = False
            self.red_chi_sq_chkr = False
    
    #scatter advance tab print parameters
    def scat_adv_print_params(self):
        try:
            
            if self.plt_chrecker == True:
                self.adv_txtbx.configure(state="normal")
                self.adv_txtbx.delete("1.0", "end")
                eqlist  = self.scater.eq_flt_to_str()
                ri_txt: str = self.scater.ufit_str()
                chi12= self.scater.chi2_and_rchi2_disp()
               
                chi2_str: str = fr"χ² = {round(chi12[0],3)}"
                rchi2_str: str = fr"χ²ᵥ = {round(chi12[1],3)}"
                self.adv_txtbx.insert("1.0", eqlist[0] + "\n"+ eqlist[1] +" \n" + eqlist[2] +"\n" + ri_txt + "\n\n" + chi2_str + "\n\n" + rchi2_str)
                self.adv_txtbx.place(relx=0.5, rely=0.6, anchor="center")
                self.adv_txtbx.configure(state="disabled")
            else:
                CTkMessagebox(title="Error", message="No plot has been generated yet.")
                return
               
        except:
              CTkMessagebox(title="Error", message="No plot has been generated yet.")
              return

       
       

 
"""
genral functions
"""
# true false checker        
def t_f_checker(checkbox_val: int) -> bool:
        if checkbox_val == 1:
            return True
        else:
            return False




        
    
#main loop
if __name__ == "__main__":
    root = App()
    root.mainloop()

