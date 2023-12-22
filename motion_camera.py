import cv2
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from pygrabber.dshow_graph import FilterGraph
import webbrowser

# Constants
DELAY_FRAMES = 3
WIDTH, HEIGHT = 640, 480
VIDEO_PATH = ""
FRAMERATE = 60
RECORDING = False
OUTPUT_PATH = ""
OUTPUT_VIDEO_WRITER = None

# Global variables
stop_camera_flag = False
cap1, cap2 = None, None
frame_buffer = []


def get_available_cameras():
    """
    Returns a list of available cameras.

    Returns:
        list: A list of strings representing the available cameras. Each string contains the device index and the device name.
    """
    devices = FilterGraph().get_input_devices()
    available_cameras = [f"{device_index}: {device_name}" for device_index, device_name in enumerate(devices)]
    available_cameras.append("Local File")
    return available_cameras


def initialize_camera(device_info):
    """
    Initializes the camera based on the given device information.

    Args:
        device_info (str): The device information. If it is "Local File", the function initializes the camera using the global VIDEO_PATH variable. If it is a device index, the function initializes the camera using the device index and the cv2.CAP_DSHOW flag.

    Returns:
        cv2.VideoCapture: The initialized camera object.

        If the device_info is "Local File" and the global VIDEO_PATH variable is not set, None is returned.

    """
    global VIDEO_PATH, WIDTH, HEIGHT, FRAMERATE

    if device_info == "Local File":
        if not VIDEO_PATH:
            return None
        cap = cv2.VideoCapture(VIDEO_PATH)
        WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        FRAMERATE = cap.get(cv2.CAP_PROP_FPS)
    else:
        device_index = int(device_info.split(":")[0])
        cap = cv2.VideoCapture(device_index + cv2.CAP_DSHOW)
        WIDTH = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        HEIGHT = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return cap


def update_frame():
    """
    Updates the frame displayed in the "Motion Camera" window.
    
    This function reads frames from two video capture objects, resizes them to a specified width and height, and performs a motion blur effect on one of the frames. The frames are then blended together using an alpha value of 0.5. The blended frame is displayed in the "Motion Camera" window and written to an output video file if recording is enabled.
    
    Parameters:
    - None
    
    Return:
    - None
    """
    global DELAY_FRAMES, WIDTH, HEIGHT, FRAMERATE, RECORDING, OUTPUT_VIDEO_WRITER
    new_delay = slider.get()

    if new_delay < DELAY_FRAMES:
        frame_buffer.clear()

    DELAY_FRAMES = new_delay

    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    try:
        frame1 = cv2.resize(frame1, (WIDTH, HEIGHT))
        frame2 = cv2.resize(frame2, (WIDTH, HEIGHT))
        frame2 = ~frame2

    except:
        stop_camera()

    frame_buffer.append(frame2)

    if len(frame_buffer) > DELAY_FRAMES:
        delayed_frame = frame_buffer.pop(0)
        alpha = 0.5
        blended_frame = cv2.addWeighted(frame1, alpha, delayed_frame, alpha, 0)
        cv2.imshow("Motion Camera", blended_frame)

        
        if RECORDING:
            OUTPUT_VIDEO_WRITER.write(blended_frame)

   
    delay = int(1000 / FRAMERATE)
    root.after(delay, update_frame)


def select_camera():
    """
    Selects a camera and initializes it for capturing frames.

    Parameters:
        None

    Returns:
        None
    """
    global cap1, cap2, frame_buffer, WIDTH, HEIGHT
    cap1 = initialize_camera(camera_combobox.get())
    cap2 = initialize_camera(camera_combobox.get())
    WIDTH = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    HEIGHT = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(WIDTH , HEIGHT)
    frame_buffer = []
    update_frame()


def start_camera():
    """
    Starts the camera and begins capturing video frames.

    This function initializes the necessary variables and settings for capturing video frames from the camera.
    It first checks if the selected device is a local file or a camera. If it is a local file, it prompts the user
    to select a video file and sets the VIDEO_PATH variable to the selected file path. It then calls the
    get_video_dimensions() function to retrieve the width, height, and framerate of the video file. If the
    selected device is a camera, it sets the VIDEO_PATH variable to an empty string.

    After initializing the necessary variables and settings, the function creates a new thread and starts it.
    The thread calls the select_camera() function, which is responsible for capturing video frames from the camera.

    This function does not have any parameters.

    This function does not have a return value.
    """
    global stop_camera_flag, VIDEO_PATH, FRAMERATE
    stop_camera_flag = False

    selected_device = camera_combobox.get()

    if selected_device == "Local File":
        VIDEO_PATH = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov")])
        if not VIDEO_PATH:
            return
        WIDTH, HEIGHT, FRAMERATE = get_video_dimensions(VIDEO_PATH)
    else:
        VIDEO_PATH = ""

    thread = threading.Thread(target=select_camera)
    thread.start()


def start_recording():
    """
    Toggles the recording state.

    The function checks the global variable RECORDING to determine if the recording is currently ongoing. If it is, the function stops the recording by setting RECORDING to False. It also releases the video writer instance, sets it to None, and updates the record label text to "Recording: No". If the recording is not ongoing, the function prompts the user to select an output path using filedialog.asksaveasfilename(). If a valid output path is selected, the function sets RECORDING to True, initializes a video writer instance using cv2.VideoWriter(), and updates the record label text to "Recording: Yes".

    Parameters:
    - None

    Returns:
    - None
    """
    global RECORDING, OUTPUT_VIDEO_WRITER, OUTPUT_PATH, record_label

    if RECORDING:
        RECORDING = False
        if OUTPUT_VIDEO_WRITER is not None:
            OUTPUT_VIDEO_WRITER.release()
            OUTPUT_VIDEO_WRITER = None
        record_label.config(text="Recording: No")
    else:
        OUTPUT_PATH = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")]
        )

        if OUTPUT_PATH:
            RECORDING = True
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            OUTPUT_VIDEO_WRITER = cv2.VideoWriter(OUTPUT_PATH, fourcc, FRAMERATE/4, (WIDTH, HEIGHT))
            record_label.config(text="Recording: Yes")


def get_video_dimensions(file_path):
    """
    Calculates the dimensions and frame rate of a video file.

    Parameters:
        file_path (str): The path to the video file.

    Returns:
        tuple: A tuple containing the width, height, and frame rate of the video.
    """
    cap = cv2.VideoCapture(file_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    framerate = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return width, height, framerate


def stop_camera():
    """
    Stops the camera capture, releases resources, and closes any open windows.

    This function sets the `stop_camera_flag` global variable to `True` to signal the camera capture loop to stop.

    It releases the camera capture objects `cap1` and `cap2` using the `release()` method.

    It closes any open windows using the `destroyAllWindows()` method.

    If the `RECORDING` flag is `True`, it sets it to `False`. If the `OUTPUT_VIDEO_WRITER` object is not `None`, it releases it using the `release()` method.

    Parameters:
        None

    Returns:
        None
    """
    global stop_camera_flag, RECORDING, OUTPUT_VIDEO_WRITER
    stop_camera_flag = True

    try:
        cap1.release()
        cap2.release()
    except:
        pass

    cv2.destroyAllWindows()

    if RECORDING:
        RECORDING = False
        if OUTPUT_VIDEO_WRITER is not None:
            OUTPUT_VIDEO_WRITER.release()
            OUTPUT_VIDEO_WRITER = None


def on_close():
    """
    Closes the application by stopping the camera and destroying the root window.
    """
    stop_camera()
    root.destroy()


root = tk.Tk()
root.title("Motion Camera by LeoAqua")
root.geometry("350x350")
root.resizable(False, False)

text1 = ttk.Label(root, text="Device:", font=("Arial", 12))
text1.pack()

camera_combobox = ttk.Combobox(root, values=get_available_cameras())
camera_combobox.set(camera_combobox["values"][0])
camera_combobox.pack()

start_button = ttk.Button(root, text="Start", command=start_camera)
start_button.pack()

stop_button = ttk.Button(root, text="Stop", command=stop_camera)
stop_button.pack()

text2 = ttk.Label(root, text="Frame offset")
text2.pack()

text3 = ttk.Label(root, text="1 (for fast motion) <=> 50 (for very slow motion)")
text3.pack()

slider = tk.Scale(root, from_=1, to=50, orient=tk.HORIZONTAL)
slider.pack()

record_label = ttk.Label(root, text="Recording: No")
record_label.pack()

record_button = ttk.Button(root, text="Start/Stop Recording", command=start_recording)
record_button.pack()

credits = ttk.Label(root, text="Credits:\nCreated by LeoAqua\nOriginal Idea from Posy\nLinks:")
credits.pack()

def callback(link):
    webbrowser.open_new(link)

link = tk.Label(root, text="My GitHub", fg="blue", cursor="hand2")
link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Leo-Aqua"))
link.pack()

link2 = tk.Label(root, text="Posy's YT", fg="blue", cursor="hand2")
link2.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.youtube.com/@PosyMusic"))
link2.pack()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
