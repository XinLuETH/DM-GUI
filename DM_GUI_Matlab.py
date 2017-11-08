# -*- coding: utf-8 -*-
"""
@author: luixn

install the setup.exe from Boston instrument

m files:
    apply_sine.m
    apply_zernike.m
    butterworth_lowpass.m
    calculate_mirror_forces.m
    calculate_voltages.m
    calibrate.m
    closeDM.m
    find_voltage_map.m
    inpaint_nans.m
    load_calibration_data.m
    lowpassfilter.m
    openDM.m
    polyval_xy.m
    zernfun.m
mexw64:
    CLOSE_multiDM.mexw64
    OPEN_multiDM.mexw64
    UPDATE_multiDM.mexw64

mat file:
    18W157#032_OPEN_LOOP_CALIBRATION_DATA.mat

flat_mirror.txt     
"""

from tkinter import Tk, Frame, Button, messagebox, LabelFrame, Label, Entry, filedialog, OptionMenu, StringVar, END
import matlab.engine
import matplotlib
import numpy as np
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class DM_control(Frame): 
    def __init__(self, parent): 
        
        Frame.__init__(self, parent, background="grey") 
        self.parent = parent 
        self.parent.title("DM control") 
        self.map_DM(parent)
        self.initMC(parent)
        self.set_shape(parent)
        self.vortex(parent)
        self.sine(parent)
        self.num_actuator = None
        self.eng = matlab.engine.start_matlab()

    def initMC(self, parent):
        """
        a button to start the DM
        """
        self.start_DM = Button (parent, text = "Connect to DM", fg='black', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.start())
        self.start_DM.grid(row=1, column=18)
        self.close_DM = Button (parent, text = "Close DM", fg='black', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.close())
        self.close_DM.grid(row=12, column=18)
        
        
    def start(self):
        """"
        call the matlab to open and initialize the Multi-DM driver
        """

        # 4.0 or 6.0 is the driver_map_ID
        (self.error_code, self.driver_info) = self.eng.openDM(6.0, nargout=2)
        print(self.driver_info)
        #np.save("D:\Xin LU\PCO_PixelFly\current_DMdriver_info.npy", self.driver_info)
        #file_write =  open("testfile.txt", "w")
        #file_write.write(str(self.driver_info))
        #file_write.close()

        if self.error_code == 0:
            # change the background color
            self.start_DM.configure(bg="blue")
        elif self.error_code == -1:
            messagebox.showinfo("Warning", "DLL not registered, or TLB file not matching DLL, or can't instance COM object")
        elif self.error_code == -2:
            messagebox.showinfo("Warning", "Unknown error")
        elif self.error_code == -4:
            messagebox.showinfo("Warning", "Data send to driver failed")
        elif self.error_code == -5:
            messagebox.showinfo("Warning", "Driver not connected")

  
    def map_DM(self, parent):
        """
        generate the actuator map so that you can selet one by pressing the button
        """
        self.button=[]
        for i in range(144):
            if i == 0 or i == 11 or i == 132 or i == 143:
                self.button.append(Button(parent, bg = "black", height = 2, width = 5))
            else:
                move_number = 0
                if i > 131:
                    move_number = 2
                elif i >= 11:
                    move_number = 1
                self.button.append(Button(parent, text = str(i-move_number), height = 2, width = 5, command = lambda i=i-0: self.Onclick(i)))
            col,row=divmod(i,12)
            if i != 132:
                self.button[i].grid(row=12-row, column=col, padx=1, pady=1)
        self.selectedlable = Label(parent, text = "XXX", bg='green', font = "bold")
        self.selectedlable.grid(row=12, column=11)
            
    def set_shape(self, parent):
        """
        set the DM shape
        """

        # button load is to load a given voltage shape
        self.loadV = Button(parent, text = "load coef file max 28", fg='blue', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.load_coef())
        # button load is to load a given shape
        self.loadS = Button(parent, text = "load shape file", fg='blue', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.load_shape())

        # button arrowUp and arrowDown is to adjust the height of a selected actuator
        self.arrowUp = Button(parent, text ='manual poke '+u'\u21D1', fg='black', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.adjust_height(1))
        self.arrowDown = Button(parent, text = 'manual poke '+u'\u21D3', fg='black', font = "Arial 16 bold", height = 1, width = 15, command = lambda: self.adjust_height(-1))
        #self.selected_Num = 'Sel. Num.'
        #self.display_Num = Label(parent, text= self.selected_Num, font = "Arial 16 bold")
        
        self.loadV.grid(row=2, column=18)
        self.loadS.grid(row=3, column=18)
        
        self.arrowUp.grid(row=10, column=18)
        self.arrowDown.grid(row=11, column=18)

    
    def sine(self, parent):
        """
        create a sin surface of the DM
        """
        self.Label_framesine = LabelFrame(parent, text=" Sine ", font = "Arial 16 bold", width=200, height=175)
        self.Label_framesine.grid(row=4, column=18, rowspan=6, columnspan=1, ipadx=8, ipady=40)
                         
        self.Label_period = Label(self.Label_framesine, text="period", font = "Arial 16 bold")
        self.entry_period = Entry(self.Label_framesine, width=4)
        self.entry_period.insert(0, "2")
        self.Label_periodunit = Label(self.Label_framesine, text="pixel", font = "Arial 16 bold")
        self.Label_amplitude = Label(self.Label_framesine, text="amp.", font = "Arial 16 bold")
        self.entry_amplitude = Entry(self.Label_framesine, width=4)
        self.entry_amplitude.insert(0, "400")
        self.Label_amplitudeunit = Label(self.Label_framesine, text="nm", font = "Arial 16 bold")
        self.Label_phase = Label(self.Label_framesine, text="phase", font = "Arial 16 bold")
        self.init_phase = ('0', '1\\2', '1', '3\\2')
        self.phase_var = StringVar(self.Label_framesine)
        self.phase_var.set(self.init_phase[0])
        self.phase_list = OptionMenu(self.Label_framesine, self.phase_var, *self.init_phase)
        self.phaseunit = Label(self.Label_framesine, text=u'\u03C0', font = "Arial 16 bold")
        
        self.Label_axis = Label(self.Label_framesine, text="axis", font = "Arial 16 bold")
        self.paxis = ('X', 'Y', 'Both')
        self.axis_var = StringVar(self.Label_framesine)
        self.axis_var.set(self.paxis[0])
        self.axis_list = OptionMenu(self.Label_framesine, self.axis_var, *self.paxis)
        
        self.Label_initP = Label(self.Label_framesine, text="direction", font = "Arial 16 bold")
        self.direction = ('RL\\UD', 'LR\\DU')
        self.direction_var = StringVar(self.Label_framesine)
        self.direction_var.set(self.direction[0])
        self.initP_list = OptionMenu(self.Label_framesine, self.direction_var, *self.direction)

        # button flat is to set a flat mirror
        self.Label_superpose= Label(self.Label_framesine, text="overlay?", font = "Arial 16 bold")
        self.superpose = ('Y', 'N')
        self.superpose_var = StringVar(self.Label_framesine)
        self.superpose_var.set(self.superpose[1])
        self.superpose_list = OptionMenu(self.Label_framesine, self.superpose_var, *self.superpose)

        self.activate_sin = Button(self.Label_framesine, text = "Apply", fg='red', font = "Arial 16 bold", height = 1, width = 8, command = lambda: self.activate_sine())
        
        self.Label_period.grid(row=6, column=18, columnspan=1)
        self.entry_period.grid(row=6, column=20)
        self.Label_periodunit.grid(row=6, column=21)
        self.Label_amplitude.grid(row=5, column=18, columnspan=1)
        self.entry_amplitude.grid(row=5, column=20)
        self.Label_amplitudeunit.grid(row=5, column=21)
        self.Label_phase.grid(row=7, column=18, columnspan=1)
        self.phase_list.grid(row=7, column=20)
        self.phaseunit.grid(row=7, column=21)
        self.Label_axis.grid(row=8, column=18, columnspan=1)
        self.axis_list.grid(row=8, column=20)
        self.Label_initP.grid(row=9, column=18, columnspan=1)
        self.initP_list.grid(row=9, column=20)
        self.Label_superpose.grid(row=10, column=18, columnspan=1)
        self.superpose_list.grid(row=10, column=20)
        self.activate_sin.grid(row=11, column=18, columnspan=5)
        
        self.Label_framesine.grid_propagate(False)
        
    def vortex(self, parent):
        """
        acquire n,m to generate Zernike polynomials 
        """
        
        self.Label_frame = LabelFrame(parent, text=" Zernike coefficients [nm]", font = "Arial 16 bold", width=350, height=240)
        self.Label_frame.grid(row=1, column=19, rowspan=12, columnspan=20, padx=6, pady=6, ipadx=95, ipady=140)

            
              
        self.label_piston = Label(self.Label_frame, text="piston", font = "Arial 16 bold")
        self.entry_piston = Entry(self.Label_frame, width=4)
        self.entry_piston.insert(0, "0")
        self.label_tiltx = Label(self.Label_frame, text="tilt_x", font = "Arial 16 bold")
        self.entry_tiltx = Entry(self.Label_frame, width=4)
        self.entry_tiltx.insert(0, "0")
        self.label_tilty = Label(self.Label_frame, text="tilt_y", font = "Arial 16 bold")
        self.entry_tilty = Entry(self.Label_frame,width=4)
        self.entry_tilty.insert(0, "0")
        self.label_vertical_astigm = Label(self.Label_frame, text="vertical astigmatism", font = "Arial 16 bold")
        self.entry_vertical_astigm = Entry(self.Label_frame,width=4)
        self.entry_vertical_astigm.insert(0, "0")
        self.label_defocus = Label(self.Label_frame, text="defocus", font = "Arial 16 bold")
        self.entry_defocus = Entry(self.Label_frame,width=4)
        self.entry_defocus.insert(0, "0")
        self.label_oblique_astigm = Label(self.Label_frame, text="oblique astigmatism", font = "Arial 16 bold")
        self.entry_oblique_astigm = Entry(self.Label_frame,width=4)
        self.entry_oblique_astigm.insert(0, "0")
        self.label_oblique_trefoil = Label(self.Label_frame, text="oblique trefoil", font = "Arial 16 bold")
        self.entry_oblique_trefoil = Entry(self.Label_frame,width=4)
        self.entry_oblique_trefoil.insert(0, "0")
        self.label_horizontal_coma = Label(self.Label_frame, text="horizontal coma", font = "Arial 16 bold")
        self.entry_horizontal_coma = Entry(self.Label_frame,width=4)
        self.entry_horizontal_coma.insert(0, "0")
        self.label_vertical_coma = Label(self.Label_frame, text="vertical coma", font = "Arial 16 bold")
        self.entry_vertical_coma = Entry(self.Label_frame,width=4)
        self.entry_vertical_coma.insert(0, "0")
        self.label_vertical_trefoil = Label(self.Label_frame, text="vertical trefoil", font = "Arial 16 bold")
        self.entry_vertical_trefoil = Entry(self.Label_frame,width=4)
        self.entry_vertical_trefoil.insert(0, "0")
        self.label_oblique_quadrafoil = Label(self.Label_frame, text="oblique quadrafoil", font = "Arial 16 bold")
        self.entry_oblique_quadrafoil = Entry(self.Label_frame,width=4)
        self.entry_oblique_quadrafoil.insert(0, "0")
        self.label_vertical_2_astigmatism = Label(self.Label_frame, text="vertical 2nd astigmatism", font = "Arial 16 bold")
        self.entry_vertical_2_astigmatism = Entry(self.Label_frame,width=4)
        self.entry_vertical_2_astigmatism.insert(0, "0")
        self.label_primary_spherical = Label(self.Label_frame, text="primary spherical", font = "Arial 16 bold")
        self.entry_primary_spherical = Entry(self.Label_frame,width=4)
        self.entry_primary_spherical.insert(0, "0")
        self.label_oblique_2_astigmatism = Label(self.Label_frame, text="oblique 2nd astigmatism", font = "Arial 16 bold")
        self.entry_oblique_2_astigmatism = Entry(self.Label_frame,width=4)
        self.entry_oblique_2_astigmatism.insert(0, "0")
        self.label_vertical_quadrafoil = Label(self.Label_frame, text="vertical quadrafoil", font = "Arial 16 bold")
        self.entry_vertical_quadrafoil = Entry(self.Label_frame,width=4)
        self.entry_vertical_quadrafoil.insert(0, "0")

        self.save_coef = Button(self.Label_frame, text="save coef", fg='blue', font = "Arial 16 bold", height = 1, width = 8, command = lambda: self.savecoef())
        self.activate_vortex = Button(self.Label_frame, text = "activate", fg='red', font = "Arial 16 bold", height = 1, width = 8, command = lambda: self.activate_Zernike())
        self.record_shape = Button(self.Label_frame, text = "save shape", fg='blue', font = "Arial 16 bold", height = 1, width = 10, command = lambda: self.save_shape())
        self.flat = Button(self.Label_frame, text="flat", fg='blue', font="Arial 12 bold", height=1, width=2,
                                command=lambda: self.set_flat())

        self.label_piston.grid(row=2, column=18)
        self.entry_piston.grid(row=2, column=19)
        self.label_tilty.grid(row=3, column=18)
        self.entry_tilty.grid(row=3, column=19)
        self.label_tiltx.grid(row=4, column=18)
        self.entry_tiltx.grid(row=4, column=19)
        self.label_vertical_astigm.grid(row=6, column=18)
        self.entry_vertical_astigm.grid(row=6, column=19)
        self.label_defocus.grid(row=5, column=18)
        self.entry_defocus.grid(row=5, column=19)
        self.label_oblique_astigm.grid(row=7, column=18)
        self.entry_oblique_astigm.grid(row=7, column=19)
        self.label_oblique_trefoil.grid(row=3, column=20)
        self.entry_oblique_trefoil.grid(row=3, column=21)
        self.label_horizontal_coma.grid(row=9, column=18)
        self.entry_horizontal_coma.grid(row=9, column=19)
        self.label_vertical_coma.grid(row=8, column=18)
        self.entry_vertical_coma.grid(row=8, column=19)
        self.label_vertical_trefoil.grid(row=2, column=20)
        self.entry_vertical_trefoil.grid(row=2, column=21)
        self.label_oblique_quadrafoil.grid(row=6, column=20)
        self.entry_oblique_quadrafoil.grid(row=6, column=21)
        self.label_vertical_2_astigmatism.grid(row=8, column=20)
        self.entry_vertical_2_astigmatism.grid(row=8, column=21)
        self.label_primary_spherical.grid(row=4, column=20)
        self.entry_primary_spherical.grid(row=4, column=21)
        self.label_oblique_2_astigmatism.grid(row=7, column=20)
        self.entry_oblique_2_astigmatism.grid(row=7, column=21)
        self.label_vertical_quadrafoil.grid(row=5, column=20)
        self.entry_vertical_quadrafoil.grid(row=5, column=21)


        self.save_coef.grid(row=9, column=20, columnspan=1, rowspan=1)
        self.flat.grid(row=10, column=19)
        self.activate_vortex.grid(row=10, column=18, columnspan=1, rowspan=1)
        self.record_shape.grid(row=10, column=20, columnspan=1, rowspan=1)
        self.Label_frame.grid_propagate(False)
        
        
    def activate_sine(self):
        """
        generate sin surgace along the x direction from left to right, and load the voltage map
        """
        try:
            # determine the initial phase of the sin wave, Pi is added in the matlab file
            self.phase = float(self.init_phase.index(self.phase_var.get()))
            #determine the period of the sin wave
            self.period = float(self.entry_period.get())
            #determine the amplitude of the sin wave
            self.amplitudeS = float(self.entry_amplitude.get())
            # direct of the sin wave
            self.direct = self.axis_var.get()
            overly = self.superpose_var.get()

            if  self.direction_var.get() == 'R\\U':
                self.direct = self.direct + '+'
            else:
                self.direct = self.direct + '-'

            if 0<self.amplitudeS<900 and self.period>=2:
                if overly == "N":
                    self.sin_info = [self.phase, self.period, self.amplitudeS, self.direct, 'N']
                else:
                    try:
                        self.sin_info = [self.phase, self.period, self.amplitudeS, self.direct, self.coef]
                    except:
                        messagebox.showinfo("Warning", "Activate Zernike first")
                        return

                    if not (-1500<=(self.sum_coef+self.amplitudeS)<= 1500):
                        messagebox.showinfo("Warning", "Amplitude out of range")
                        return

                (self.shape, self.vol_map) = self.eng.apply_sine(self.sin_info, nargout=2)
                self.vol_map = [one for [one] in self.vol_map]

                self.showmap()
                self.excute()
            else:
                messagebox.showinfo("Warning", "Amplitude is too large/period is too small")
                return
        except:
            messagebox.showinfo("Warning", "Enter number")
            return
        
        
    def activate_Zernike(self):
        """
        call matlab file to generate a Zernike (n,m) and load the corresponding voltage map
        """
        self.coef= []
        try:
            self.coef.append(float(self.entry_piston.get()))
            self.coef.append(float(self.entry_tilty.get()))
            self.coef.append(float(self.entry_tiltx.get()))
            self.coef.append(float(self.entry_defocus.get()))
            self.coef.append(float(self.entry_vertical_astigm.get()))
            self.coef.append(float(self.entry_oblique_astigm.get()))
            self.coef.append(float(self.entry_vertical_coma.get()))
            self.coef.append(float(self.entry_horizontal_coma.get()))
            self.coef.append(float(self.entry_vertical_trefoil.get()))
            self.coef.append(float(self.entry_oblique_trefoil.get()))

            self.coef.append(float(self.entry_primary_spherical.get()))
            self.coef.append(float(self.entry_vertical_quadrafoil.get()))
            self.coef.append(float(self.entry_oblique_quadrafoil.get()))
            self.coef.append(float(self.entry_oblique_2_astigmatism.get()))
            self.coef.append(float(self.entry_vertical_2_astigmatism.get()))
            self.sum_coef = sum(self.coef)
            if -1500<=self.sum_coef<= 1500:
                self.coef = matlab.double(self.coef)

                (self.shape, self.vol_map) = self.eng.apply_zernike(self.coef, nargout=2)
                self.vol_map = [one for [one] in self.vol_map]
                self.showmap()
                self.excute()
            else:
                messagebox.showinfo("Warning", "Coefficient should < 1500")
        except:
             messagebox.showinfo("Warning", "Enter number")
        
    def savecoef(self):
        """
        set apply piston at 1200nm to the DM
        """
        #self.coef = [float(self.entry_piston.get())]+[0]*14
        try:
            self.filename = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('txt files', '*.txt')],
                                                     title='Enter your file name', parent=self.Label_frame)
        # self.filehandle = open(self.filename, 'w')
            re_coef = np.array(self.coef)
            np.savetxt(self.filename, re_coef)
        except AttributeError:
            messagebox.showinfo("Warning", "Activate first!")




    def Onclick(self, i):
        """"
        select an actuator        
        """
        
        #if self.num_actuator == None:
         #   self.num_actuator = i 
            #self.orig_color = self.button[i].cget("background")
          #  self.button[i].configure(background="blue")
        # convert i to actual DM maps
        col, row = divmod(i, 12)
        j = 12 * (12 - row) + 12 - col
        if self.num_actuator != j:
            self.button[i].configure(background="blue")
            if self.num_actuator != None:
                col, row = divmod(self.num_actuator,12)
                i=12 * (12 - row) + 12 - col
                self.button[i].configure(background="light grey")#self.orig_color
            self.num_actuator = j
        self.selectedlable.configure(text = str(self.vol_map[self.num_actuator])[0:5])
        
        
    def save_shape(self):
        """
        save the applied DM shape as a txt file, if you want to create a new file, just type in the name
        """
        #simpledialog.askstring('save_shape', 'Enter file name',  parent = self.Label_frame)
        self.filename = filedialog.asksaveasfilename(defaultextension = '.txt', filetypes = [('txt files', '*.txt')], title = 'Enter your file name', parent = self.Label_frame)
        #self.filehandle = open(self.filename, 'w')
        re_shape = np.array(self.shape)
        np.savetxt(self.filename, re_shape)
        #for item in re_shape:
         #   self.filehandle.writelines("%s\n" % item)
        #self.filehandle.close()
        
    def adjust_height(self, direction):
        """
        adjust the height of selected actuator
        """
        if self.num_actuator == None:
            messagebox.showinfo("Warning", "Select an actuator first!!")
            # must choose an actuator first
        else:
            
            if direction == -1:
                if self.vol_map[self.num_actuator] - 0.05 >= 0:
                    self.vol_map[self.num_actuator] = self.vol_map[self.num_actuator] - 1
                else:
                    messagebox.showinfo("Warning", "Stop pull it down!!")
            else:
                if self.vol_map[self.num_actuator] + 0.05 <= 99.99:
                    self.vol_map[self.num_actuator] = self.vol_map[self.num_actuator] + 1
                else:
                    messagebox.showinfo("Warning", "Stop pull it up!!")
            self.selectedlable.configure(text = str(self.vol_map[self.num_actuator])[0:5])
            self.excute()
            
            
    def mat_to_list(self):
        """
        convert the self.shape (a matlab array) to a python list, not used any more
        """
        shape_list = []
        (row, column) = self.shape.size
        for x in range(row):
            shape_list.append(list(self.shape[x]))
        return shape_list
        

    def load_shape(self):
        """
        load other shapes to set the matrix
        and delete the chosen actuator
        """
        
        self.ftypes = [('txt files', '*.txt')]
        self.dlg = filedialog.Open(self, filetypes = self.ftypes)
        self.select_file = self.dlg.show()
        
        if self.select_file != '':
            Voltage = self.readFile(self.select_file)
            self.vol_map = self.eng.calibrate(Voltage)
            self.vol_map = [one for [one] in self.vol_map]
            self.excute()
        else:
            return
        self.num_actuator = None  
              

    def load_coef(self):
        "load the save Zernike coefficient and change the corresponding Entry value"
        self.ftypes = [('txt files', '*.txt')]
        self.dlg = filedialog.Open(self, filetypes=self.ftypes)
        self.select_file = self.dlg.show()
        if self.select_file != '':
            Coef = self.readFile(self.select_file)
            self.coef = [float(i) for i in Coef]

            self.entry_piston.delete(0,END)
            self.entry_piston.insert(0,str(self.coef[0]))
            self.entry_tiltx.delete(0, END)
            self.entry_tiltx.insert(0, str(self.coef[1]))
            self.entry_tilty.delete(0, END)
            self.entry_tilty.insert(0, str(self.coef[2]))
            self.entry_defocus.delete(0, END)
            self.entry_defocus.insert(0, str(self.coef[3]))
            self.entry_vertical_astigm.delete(0, END)
            self.entry_vertical_astigm.insert(0, str(self.coef[4]))
            self.entry_oblique_astigm.delete(0, END)
            self.entry_oblique_astigm.insert(0, str(self.coef[5]))
            self.entry_vertical_coma.delete(0, END)
            self.entry_vertical_coma.insert(0, str(self.coef[6]))
            self.entry_horizontal_coma.delete(0, END)
            self.entry_horizontal_coma.insert(0, str(self.coef[7]))
            self.entry_vertical_trefoil.delete(0, END)
            self.entry_vertical_trefoil.insert(0, str(self.coef[8]))
            self.entry_oblique_trefoil.delete(0, END)
            self.entry_oblique_trefoil.insert(0, str(self.coef[9]))
            self.entry_primary_spherical.delete(0, END)
            self.entry_primary_spherical.insert(0, str(self.coef[10]))
            self.entry_vertical_quadrafoil.delete(0, END)
            self.entry_vertical_quadrafoil.insert(0, str(self.coef[11]))
            self.entry_oblique_quadrafoil.delete(0, END)
            self.entry_oblique_quadrafoil.insert(0, str(self.coef[12]))
            self.entry_oblique_2_astigmatism.delete(0, END)
            self.entry_oblique_2_astigmatism.insert(0, str(self.coef[13]))
            self.entry_vertical_2_astigmatism.delete(0, END)
            self.entry_vertical_2_astigmatism.insert(0, str(self.coef[14]))
            self.sum_coef = sum(self.coef)
            if -1500 <= self.sum_coef <= 1500:
                self.coef = matlab.double(self.coef)

                (self.shape, self.vol_map) = self.eng.apply_zernike(self.coef, nargout=2)
                self.vol_map = [one for [one] in self.vol_map]
                self.showmap()
                self.excute()
            else:
                messagebox.showinfo("Warning", "Coefficient should < 1500")
        else:
            return

    def set_flat(self):
        self.coef = [0]*28
        self.entry_piston.delete(0, END)
        self.entry_piston.insert(0, str(0))
        self.entry_tiltx.delete(0, END)
        self.entry_tiltx.insert(0, str(0))
        self.entry_tilty.delete(0, END)
        self.entry_tilty.insert(0, str(0))
        self.entry_defocus.delete(0, END)
        self.entry_defocus.insert(0, str(0))
        self.entry_vertical_astigm.delete(0, END)
        self.entry_vertical_astigm.insert(0, str(0))
        self.entry_oblique_astigm.delete(0, END)
        self.entry_oblique_astigm.insert(0, str(0))
        self.entry_vertical_coma.delete(0, END)
        self.entry_vertical_coma.insert(0, str(0))
        self.entry_horizontal_coma.delete(0, END)
        self.entry_horizontal_coma.insert(0, str(0))
        self.entry_vertical_trefoil.delete(0, END)
        self.entry_vertical_trefoil.insert(0, str(0))
        self.entry_oblique_trefoil.delete(0, END)
        self.entry_oblique_trefoil.insert(0, str(0))
        self.entry_primary_spherical.delete(0, END)
        self.entry_primary_spherical.insert(0, str(0))
        self.entry_vertical_quadrafoil.delete(0, END)
        self.entry_vertical_quadrafoil.insert(0, str(0))
        self.entry_oblique_quadrafoil.delete(0, END)
        self.entry_oblique_quadrafoil.insert(0, str(0))
        self.entry_oblique_2_astigmatism.delete(0, END)
        self.entry_oblique_2_astigmatism.insert(0, str(0))
        self.entry_vertical_2_astigmatism.delete(0, END)
        self.entry_vertical_2_astigmatism.insert(0, str(0))

        self.coef = matlab.double(self.coef)
        (self.shape, self.vol_map) = self.eng.apply_zernike(self.coef, nargout=2)
        self.vol_map = [one for [one] in self.vol_map]
        self.showmap()
        self.excute()

    def readFile(self, filename):
        # read the file
        self.file = open(filename, "r")
        self.text = self.file.read()
        self.read_data = list(self.text.split())
        #self.matrix = [float(i) for i in self.read_data]
        self.file.close()
       
        return self.read_data

    def showmap(self):
        """
        show the applied shape in GUI 
        """
        # convert the shape into nm scale
        self.shape_nm = np.array(self.shape) * 10 ** 9
        shapemap = Figure(figsize=(3,2), dpi=100)
        a = shapemap.add_subplot(111)
        self.a = a.imshow(self.shape_nm,  aspect='auto') #cmap='gray',
        shapemap.colorbar(self.a)
        a.axis('off')

        canvas = FigureCanvasTkAgg(shapemap, self.Label_frame)
        canvas.show()
        canvas.get_tk_widget().grid(row=11, column=18, columnspan=3, rowspan=2)

    def excute(self):
        """
        if all values in mirror_shape are no less than 0 and smaller than 1
        load the shape to DM
        otherwise, stop
        """
        self.num_actuator == None
        
        if len(self.vol_map) == 144 and all(x>=0 and x<=98 for x in self.vol_map):
            # covert list to double cell array for matlab
            self.vol_map_MATLAB = matlab.double(self.vol_map)
            self.error_code = self.eng.updateDM(self.driver_info, self.vol_map_MATLAB)

            if self.error_code == 0:
                pass
            elif self.error_code == -4:
                messagebox.showinfo("Data send to driver failed")
            elif self.error_code == -6:
                messagebox.showinfo("USB_ID and USB_pointer values unrecognized")
            else:
                messagebox.showinfo("Error")
        else:
            messagebox.showinfo("Warning", "wrong shape!!")
        
    def close(self):
        """
        close DM driver and stop the matlab engine
        """

        self.error_code = self.eng.closeDM(self.driver_info)
        #self.error_code = 0
        self.eng.quit()
        if self.error_code == 0:
            self.parent.destroy()
        elif self.error_code == -6:
            messagebox.showinfo("USB_ID and USB_pointer values unrecognized")
        else:
            messagebox.showinfo("Error")
            
    
    
def main(): 

    root = Tk() 
    root.title("DM control")
    # sets a size for the window and positions it on the screen
    root.geometry("1400x550") 
    DM_control(root) 
    
    root.mainloop()
    
    
    
    
if __name__ == '__main__': 
    main()