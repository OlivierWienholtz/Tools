# Copyright 1986-2024 Altair Engineering Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining 
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os
import platform
import tkinter as tk
if platform.system() == 'Windows':
    import ctypes
    myappid = 'openradioss.jobgui.1.6.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('openradioss.jobgui.1.6.0')
#import time
import subprocess
from tkinter import filedialog
from tkinter import messagebox
from tkinter import Checkbutton

from button_with_highlight import ButtonWithHighlight
from placeholder_entry import PlaceholderEntry
from job_holder import JobHolder

try:
    from vortex_radioss.animtod3plot.Anim_to_D3plot import readAndConvert
    vd3penabled = True
except ImportError:
    # If VortexRadioss Module not present disable d3plot options
    vd3penabled = False
import gui_def

# Global Variables
job_holder = JobHolder()
Window     = gui_def.window(vd3penabled)


#----------------- Functions -----------------#
def close_window():
    if job_holder.is_empty() or messagebox.askokcancel('Close Window', 'Job is running. Close?'):
        Window.close()
        quit()

def on_closing():
    # Call the same function as the 'Close' button when the window is closed
    close_window()
    
def add_job():
    check_install()
    if job_file_entry.is_placeholder_active() or not os.path.exists(job_file_entry.get_user_input()):
        messagebox.showerror('', 'Select job.')
        return

    input_file = job_file_entry.get_user_input()
    file_extension = os.path.splitext(input_file)[1].lower()

    arg1 = job_file_entry.get_user_input()
    arg2 = nt_entry.get_user_input('1')
    arg3 = np_entry.get_user_input('1')
    # Get the value of single precision based on the checkbox state
    arg4 = 'sp' if single_status.get() else 'dp' 
    # Get the value of vtk-conversion based on the checkbox state
    arg5 = 'yes' if vtk_status.get() else 'no' 
    # Get the value of csv-conversion based on the checkbox state 
    arg6 = 'yes' if csv_status.get() else 'no'
    # Get the value of starter-only based on the checkbox state 
    arg7 = 'yes' if starter_status.get() else 'no'
    if vd3penabled:
    # Get the value of d3plot conversion based on the checkbox state 
        arg8 = 'yes' if d3plot_status.get() else 'no'
    else:
       arg8 = 'no'
    # Call the function to check MPI vars file for windows only
    if platform.system() == 'Windows':
        check_mpi_path()
 
    check_sp_exes()
 
    if messagebox.askokcancel('Add job', 'Add job?'):
        save_config()

        # Get the directory where your script is located
        script_directory = os.path.dirname(os.path.abspath(__file__))

        # Provide the absolute path to runopenradioss.py
        runopenradioss_script = os.path.join(script_directory, 'runopenradioss.py')

        if platform.system() == 'Windows':
            allcommand = [runopenradioss_script, os.path.normpath(arg1), arg2, arg3, arg4, arg5, arg6, arg7, arg8]
        elif platform.system() == 'Linux':
            allcommand = ["python3", runopenradioss_script, os.path.normpath(arg1), arg2, arg3, arg4, arg5, arg6, arg7, arg8]

        job_holder.push_job(allcommand)

def show_queue():
    job_holder.show_queue()

def clear_queue():
    job_holder.clear_queue()

def run_job():
    job_holder.run_job()
    Window.root.after(1000, run_job)
    return

def select_file():
    file_path = filedialog.askopenfilename(
        title='Select input file',
        filetypes=[('Radioss or Dyna file', '*.rad *.key *.k')]
    )
    job_file_entry.on_focus_gain()
    job_file_entry.delete(0, tk.END)
    job_file_entry.insert(0, file_path)

def check_mpi_path():
    mpi_path_file = "path_to_intel-mpi.txt"
    if np_entry.get_user_input() > '1' and not os.path.exists(mpi_path_file):
        messagebox.showinfo('', 'Running MPI requires intel mpi installation. Please browse to an intel-mpi location. Or select np = 1')
        directory_path = filedialog.askdirectory(
            title='Select intel-mpi directory'            
        )
        if directory_path:
            with open(mpi_path_file, 'w') as file:
                file.write('"' + directory_path + '"')
    else:
        # MPI path file exists or np <= 1, continue with the script
        pass

def check_sp_exes():
    if platform.system() == 'Windows':
        sp_executable = "../exec/starter_win64_sp.exe"
    elif platform.system() == 'Linux':
        sp_executable = "../exec/starter_linux64_gf_sp"
    if single_status.get() and not os.path.exists(sp_executable):
        messagebox.showinfo('WARNING', 'Single Precision Executables not Installed\n      Please Install or submit without sp option checked')

    else:
        # single precision executables exist continue with script
        pass

def check_install():
    is_installed = "../hm_cfg_files"
    if not os.path.exists(is_installed):
        messagebox.showinfo('INCORRECT INSTALL LOCATION', 'The guiscripts folder needs to be saved inside\n your OpenRadioss Folder\n (Same Folder Level as exec and hm_cfg_files)')

    else:
        # installation location correct continue with script
        pass

def save_config():
    with open('./config/sp', mode='w') as f:
        f.write(str(single_status.get()))
    with open('./config/anim_vtk', mode='w') as f:
        f.write(str(vtk_status.get()))
    with open('./config/th_csv', mode='w') as f:
        f.write(str(csv_status.get()))
    with open('./config/starter', mode='w') as f:
        f.write(str(starter_status.get()))
    if vd3penabled:
        with open('./config/anim_d3plot', mode='w') as f:
            f.write(str(d3plot_status.get()))

def apply_config():
    if os.path.exists('./config/sp'):
        with open('./config/sp', mode='r') as f:
            if f.readline() == 'True':
                single_status.set(True)
    if os.path.exists('./config/anim_vtk'):
        with open('./config/anim_vtk', mode='r') as f:
            if f.readline() == 'True':
                vtk_status.set(True)
    if os.path.exists('./config/th_csv'):
        with open('./config/th_csv', mode='r') as f:
            if f.readline() == 'True':
                csv_status.set(True)
    if os.path.exists('./config/starter'):
        with open('./config/starter', mode='r') as f:
            if f.readline() == 'True':
                starter_status.set(True)
    if os.path.exists('./config/anim_d3plot'):
        if vd3penabled:
            with open('./config/anim_d3plot', mode='r') as f:
                if f.readline() == 'True':
                    d3plot_status.set(True)

# File Menu
job_file_entry=Window.file('Job file (.rad, .key, or .k)', select_file, Window.icon_folder)

# Create checkboxes
nt_entry          = Window.thread_mpi('-nt', 5,0,2)
np_entry          = Window.thread_mpi('-np', 5,5,2)
single_status     = Window.checkbox1('Single Precision ',5,5)
vtk_status        = Window.checkbox1('Anim - vtk',5,2)
starter_status    = Window.checkbox2('Run Starter Only',5,2)
if vd3penabled:
    d3plot_status = Window.checkbox2('Anim - d3plot',5,2)
    csv_status    = Window.checkbox3('TH - csv',0,0)
else:
    csv_check_box = Window.checkbox2('TH - csv    ',5,2)

# Create buttons
Window.button('Add Job', add_job, (0, 5))
Window.button('Show Queue', show_queue, 5)
Window.button('Clear Queue', clear_queue, 5)
Window.button('Close', close_window, (5, 0))

# Create a menu bar
Window.menubar('Info')

apply_config()
Window.root.protocol("WM_DELETE_WINDOW", on_closing)
Window.root.after(1000, run_job)
Window.root.mainloop()
