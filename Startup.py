#
# Scripts:
# Generating Startup EXE (Windows): pyinstaller --onefile --noconsole --icon="./Media/Logo-background.ico" --add-data="Media;Media" --name '360 Media Player' Startup.py
# Generating Startup EXE (MacOS): pyinstaller --onefile --noconsole --icon="./Media/Logo.icns" --add-data="Media:Media" --name '360 Media Player' Startup.py

import socket
import subprocess
import threading
import time
import tkinter as tk
from tkinter import filedialog
import json
import os
import platform
from PIL import Image, ImageTk
import sys

# Global variables for mediaProviderURL and mediaProviderPort
mediaProviderURL = ""
mediaProviderPort = ""
mediaPlayerPort = ""
directory_changed_event = threading.Event()
provider_process = None  
player_process = None  
mediaProviderString = "360_Media_Provider"
mediaPlayerString = "360_Media_Player"
defaultBackgroundColor = "#1F1B24"
defaultTextColor = "white"
defaultFontAndSize = ("Arial", 16)
headingFontAndSize = ("Arial", 36)
buttonFontAndSize = ("Arial", 12)

if getattr(sys, "frozen", False):
    icon_path = os.path.join(sys._MEIPASS, "Media/Logo-background.ico")
    logo_path = os.path.join(sys._MEIPASS, "./Media/Logo.png")
else:
    icon_path = "Media/Logo-background.ico"
    logo_path = "./Media/Logo.png"

def update_ui_after_start():
    global provider_process, player_process

    # Sleeping to make sure player fully started before printing
    # There is a period where it is starting, and does not yet have a PID, and this causes the failure condition to run
    # perhaps there is some alternative solution. 
    time.sleep(2) 
    if provider_process is not None and player_process is not None :
        update_ui_after_start_success()
    else:
        update_ui_after_start_failure()

def update_ui_after_start_success():
    page1.grid_remove() 
    root.minsize(300, 200)

    # Directory Selector with text and "Browse" button in the center
    headerFrame_p2 = tk.Frame(page2, bg=defaultBackgroundColor)
    headerFrame_p2.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

    # Display the image at the top left
    logo_label_p2 = tk.Label(headerFrame_p2, image=logo_image, bg=defaultBackgroundColor)
    logo_label_p2.grid(row=0, column=0, sticky="nw")

    # Label (centered)
    running_label = tk.Label(headerFrame_p2, text="360 Media Player is running!",
                            bg=defaultBackgroundColor, fg=defaultTextColor, font=headingFontAndSize)
    running_label.grid(row=0, column=1, padx=10, pady=20, sticky="n")

    ip_and_port_label_Player = tk.Label(
        page2, text=f"Access the 360 media player at: https://{local_ip}:{mediaPlayerPort}", anchor="w",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=defaultFontAndSize)
    ip_and_port_label_Player.grid(row=1, column=0, sticky="nw", padx=10, pady=10)
    
    ip_and_port_label_Provider = tk.Label(
        page2, text=f"Access the media provider at: https://{local_ip}:{mediaProviderPort}", anchor="w",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=defaultFontAndSize)
    ip_and_port_label_Provider.grid(row=2, column=0, sticky="nw", padx=10, pady=10)

    reminder_label = tk.Label(
        page2, text=f"Please visit both above addresses and accept the connection at least once.", anchor="w",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=defaultFontAndSize)
    reminder_label.grid(row=3, column=0, sticky="nw", padx=10, pady=10)

    reminder_label = tk.Label(
        page2, text=f"Then the media player will be available at  https://{local_ip}:{mediaPlayerPort}", anchor="w",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=defaultFontAndSize)
    reminder_label.grid(row=4, column=0, sticky="nw", padx=10, pady=10)

    close_button = tk.Button(page2, text="Close", command=cancel,
                          font=buttonFontAndSize)
    close_button.grid(row=5, column=0, sticky="nw", padx=10, pady=10)

    page2.grid(row=0, column=0, sticky="nsew")  # Display the second page
    page2.tkraise()

def update_ui_after_start_failure():
    page1.grid_remove() 
    root.minsize(300, 200)

    # Directory Selector with text and "Browse" button in the center
    headerFrame_p2 = tk.Frame(page2, bg=defaultBackgroundColor)
    headerFrame_p2.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

    # Display the image at the top left
    logo_label_p2 = tk.Label(headerFrame_p2, image=logo_image, bg=defaultBackgroundColor)
    logo_label_p2.grid(row=0, column=0, sticky="nw")

    # Label (centered)
    running_label = tk.Label(headerFrame_p2, text="360 Media Player!",
                            bg=defaultBackgroundColor, fg=defaultTextColor, font=headingFontAndSize)
    running_label.grid(row=0, column=1, padx=10, pady=20, sticky="n")

    ip_and_port_label_Player = tk.Label(
        page2, text=f"Failed to start. \nCommon Errors Include: \n->Incomplete installation \n->The startup file not ran in the same folder as the Player and Provider", anchor="w",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=defaultFontAndSize, justify="left")
    ip_and_port_label_Player.grid(row=1, column=0, sticky="nw", padx=10, pady=10)

    close_button = tk.Button(page2, text="Close", command=cancel,
                          font=buttonFontAndSize)
    close_button.grid(row=5, column=0, sticky="nw", padx=10, pady=10)

    page2.grid(row=0, column=0, sticky="nsew")  # Display the second page
    page2.tkraise()

def browse_directory():
    directory = filedialog.askdirectory()
    path_entry.delete(0, tk.END)
    path_entry.insert(0, directory)

def cancel():
    try:
        provider_process.terminate()
    except Exception as e:
        print("Problem closing provider_process:", str(e))
    try:
        player_process.terminate()
    except Exception as e:
        print("Problem closing player_process:", str(e))
    root.quit()

def get_local_ip():
    if platform.system() == "Windows":
        get_local_ip_Windows()
    elif platform.system() == "Darwin":
        get_local_ip_MacOS()

def get_local_ip_Windows():
    global local_ip
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"local_ip: {local_ip}")
    except Exception as e:
        print("Error:", e)
        local_ip = "Unable to retrieve local IP"

    return local_ip

def get_local_ip_MacOS():
    global local_ip
    local_ip = "127.0.0.1"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"Local IP address: {local_ip}")
    except Exception as e:
        print("Error:", e)
        local_ip = "Unable to retrieve local IP"

def execute_in_directory(directoryName, functionToExecute, *args):
    original_directory = os.getcwd()

    if not os.path.exists(directoryName):
        os.chdir("..")
        
    while os.path.exists(directoryName):
        os.chdir(directoryName)

    functionToExecute(*args)

    os.chdir(original_directory)

def get_provider_port():
    global mediaProviderPort
    
    try:
        with open('application.json', 'r') as app_file:
            app_data = json.load(app_file)
            mediaProviderPort = app_data.get('port', mediaProviderPort)
    except FileNotFoundError:
        pass
    print("mediaProviderPort:", mediaProviderPort)

def get_player_port():
    global mediaPlayerPort

    try:
        with open('application.json', 'r') as app_file:
            app_data = json.load(app_file)
            mediaPlayerPort = app_data.get('mediaPlayerPort', mediaPlayerPort)
    except FileNotFoundError:
        pass

    print("mediaPlayerPort:", mediaPlayerPort)

def save_selected_directory_to_config():
    global selected_directory 
    selected_directory = path_entry.get() 
    config_data = {"selected_directory": selected_directory}
    with open('startup-config.json', 'w') as config_file:
        json.dump(config_data, config_file)

def update_directory_path():
    try:
        with open('application.json', 'r') as app_file:
            app_data = json.load(app_file)
            # Update the 'directoryPath' value
            app_data['directoryPath'] = selected_directory
    except FileNotFoundError:
        pass

    # Save the modified JSON data back to the file
    with open('application.json', 'w') as app_file:
        json.dump(app_data, app_file, indent=4)

def update_ip_and_port():
    try:
        with open('application.json', 'r') as app_file:
            app_data = json.load(app_file)
            app_data['mediaProviderURL'] = local_ip
            app_data['mediaProviderPort'] = str(mediaProviderPort)
    except FileNotFoundError:
        pass

    with open('application.json', 'w') as app_file:
        json.dump(app_data, app_file, indent=4)

def start_provider_thread_within_directory(directoryName, functionToExecute):
    process_thread = threading.Thread(
        target=execute_thread_in_directory, args=(directoryName, functionToExecute))
    process_thread.start()

def start_player_thread_within_directory(directoryName, functionToExecute):
    directory_changed_event.wait()
    process_thread = threading.Thread(
        target=execute_thread_in_directory, args=(directoryName, functionToExecute))
    process_thread.start()

def execute_thread_in_directory(directoryName, functionToExecute, *args):
    execute_in_directory(directoryName, functionToExecute)
    directory_changed_event.set()

def start_provider():
    if platform.system() == "Windows":
        start_provider_Windows()
    elif platform.system() == "Darwin":
        start_provider_MacOS()

def start_provider_Windows():
    global provider_process

    try:
        # Start "node app.js" and capture the output in a subprocess
        provider_process = subprocess.Popen(
            ["node", "app.js"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
            )

        def monitor_process_output():
            while True:
                line = provider_process.stdout.readline()
                if not line:
                    break  # No more output
                # Print the line to the console in real-time
                print(line, end='')

        # Start a separate thread to monitor the subprocess output
        monitor_thread = threading.Thread(target=monitor_process_output)
        monitor_thread.start()

    except Exception as e:
        # Handle any errors or exceptions here
        print("Error running 'node app.js':", str(e))

def start_provider_MacOS():
    global provider_process

    try:
        # Start "node app.js" and capture the output in a subprocess
        provider_process = subprocess.Popen(
            ["node", "app.js"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1,
            # creationflags=subprocess.CREATE_NO_WINDOW
            )

        def monitor_process_output():
            while True:
                line = provider_process.stdout.readline()
                if not line:
                    break  # No more output
                # Print the line to the console in real-time
                print(line, end='')

        # Start a separate thread to monitor the subprocess output
        monitor_thread = threading.Thread(target=monitor_process_output)
        monitor_thread.start()

    except Exception as e:
        # Handle any errors or exceptions here
        print("Error running 'node app.js':", str(e))

def start_player():
    if platform.system() == "Windows":
        start_player_Windows()
    elif platform.system() == "Darwin":
        start_player_MacOS()

def start_player_Windows():
    global player_process

    try:
        player_process = subprocess.Popen(
            ["node", "-e",
                "const { execSync } = require('child_process'); console.log(execSync('npm run dev').toString());"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("360 Media Player is running")

        def monitor_process_output():
            while True:
                line = player_process.stdout.readline()
                if not line:
                    break  # No more output
                # Print the line to the console in real-time
                print(line, end='')

        # Start a separate thread to monitor the subprocess output
        monitor_thread = threading.Thread(target=monitor_process_output)
        monitor_thread.start()
    except Exception as e:
        # Handle any errors or exceptions here
        print("Error running 'npm run dev':", str(e))

def start_player_MacOS():
    global player_process

    try:
        player_process = subprocess.Popen(
            ["node", "-e",
                "const { execSync } = require('child_process'); console.log(execSync('npm run dev').toString());"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            bufsize=1,
            # creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("360 Media Player is running")

        def monitor_process_output():
            while True:
                line = player_process.stdout.readline()
                if not line:
                    break  # No more output
                # Print the line to the console in real-time
                print(line, end='')

        # Start a separate thread to monitor the subprocess output
        monitor_thread = threading.Thread(target=monitor_process_output)
        monitor_thread.start()
    except Exception as e:
        # Handle any errors or exceptions here
        print("Error running 'npm run dev':", str(e))

def start():
    # Needed because mac defaults to current user dir
    current_directory = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_directory)

    save_selected_directory_to_config()
    # Get local IP
    get_local_ip()
    # Get Provider Port
    execute_in_directory(mediaProviderString, get_provider_port)
    # Get Player Port
    execute_in_directory(mediaPlayerString, get_player_port)
    # Set Directory for Provider
    execute_in_directory(mediaProviderString, update_directory_path)
    # Set provider address for Player
    execute_in_directory(mediaPlayerString, update_ip_and_port)
    # Start Provider
    start_provider_thread_within_directory(mediaProviderString, start_provider)
    # Start Player
    start_player_thread_within_directory(mediaPlayerString, start_player)
    # Update UI after start
    update_ui_after_start()

# Create the main window
root = tk.Tk()
root.title("360 Media Player")
root.eval("tk::PlaceWindow . center")
root.iconbitmap(icon_path)

# Set a minimum size for the root window to make it larger by default
root.minsize(400, 200)

root.configure(bg=defaultBackgroundColor)

# Create a container frame for the first page
page1_container = tk.Frame(root, bg=defaultBackgroundColor)
page1_container.grid(row=0, column=0, sticky="nsew")

# Create the first page frame within the container
page1 = tk.Frame(page1_container, bg=defaultBackgroundColor)
page1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Directory Selector with text and "Browse" button in the center
headerFrame = tk.Frame(page1, bg=defaultBackgroundColor)
headerFrame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

# Load the image
original_image = Image.open(logo_path)
resized_image = original_image.resize((100, 100), Image.LANCZOS)
logo_image = ImageTk.PhotoImage(resized_image)

# Display the image at the top left
logo_label = tk.Label(headerFrame, image=logo_image, bg=defaultBackgroundColor)
logo_label.grid(row=0, column=0, sticky="nw")

# Label (centered)
heading_label = tk.Label(headerFrame, text="360 Media Player",
                         bg=defaultBackgroundColor, fg=defaultTextColor, font=headingFontAndSize)
heading_label.grid(row=0, column=1, padx=10, pady=20, sticky="n")

# Directory Selector with text and "Browse" button in the center
directory_frame = tk.Frame(page1, bg=defaultBackgroundColor)
directory_frame.grid(row=1, column=0, columnspan=2, pady=28, sticky="n")

browse_button = tk.Button(directory_frame, text="Select a directory:", font=buttonFontAndSize,
                          command=browse_directory)  # You need to define the command function 'browse_directory'
browse_button.grid(row=0, column=0, padx=(0, 10))

path_entry = tk.Entry(directory_frame, width=30, bg=defaultBackgroundColor,
                      fg=defaultTextColor, font=defaultFontAndSize)
path_entry.grid(row=0, column=1, padx=(0, 10))

# Buttons (centered horizontally with distance between them)
button_frame = tk.Frame(page1, bg=defaultBackgroundColor)
button_frame.grid(row=2, column=0, columnspan=2, pady=28, sticky="n")

# You need to define the command function 'cancel'
cancel_button = tk.Button(button_frame, text="Cancel",
                          font=defaultFontAndSize, command=cancel)
cancel_button.grid(row=0, column=0, padx=(0, 80))

# You need to define the command function 'start'
start_button = tk.Button(button_frame, text="Start",
                         font=defaultFontAndSize, command=start)
start_button.grid(row=0, column=1)

try:
    with open('startup-config.json', 'r') as config_file:
        config_data = json.load(config_file)
        selected_directory = config_data.get('selected_directory', '')
        path_entry.insert(0, selected_directory)
except FileNotFoundError:
    pass  # If the file doesn't exist, do nothing

# Second Page
page2 = tk.Frame(root, bg=defaultBackgroundColor)

# Initially, show the first page
page1_container.tkraise()

# You can now access mediaProviderURL and mediaProviderPort outside the tkinter application.
print("Closing Application")

root.mainloop()
