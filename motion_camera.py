import cv2
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from pygrabber.dshow_graph import FilterGraph
import tkinter
import webbrowser

delay_frames = 1
stop_camera_flag = False
width = 640
height = 480
video_path = ""
framerate = 30  # Default framerate

def get_available_cameras():
    """
    Returns a list of available cameras.

    This function retrieves the available input devices using the FilterGraph class and
    creates a list of camera names with their corresponding indices. The camera names are
    in the format "{device_index}: {device_name}". The function then appends the string
    "Local File" to the list of available cameras. Finally, the function returns the
    updated list of available cameras.

    Returns:
        list: A list of available cameras. Each camera is represented by a string in the
        format "{device_index}: {device_name}". The list also includes the string "Local
        File".
    """
    devices = FilterGraph().get_input_devices()
    available_cameras = [
        f"{device_index}: {device_name}"
        for device_index, device_name in enumerate(devices)
    ]
    available_cameras.append("Local File")
    return available_cameras


def initialize_camera(device_info):
    global video_path, width, height, framerate

    if device_info == "Local File":
        if not video_path:
            return None
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # Get the framerate of the video
        framerate = cap.get(cv2.CAP_PROP_FPS)
    else:
        device_index = int(device_info.split(":")[0])
        cap = cv2.VideoCapture(device_index + cv2.CAP_DSHOW)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return cap

def update_frame():
    global delay_frames, width, height, framerate
    new_delay = slider.get()

    if new_delay < delay_frames:
        frame_buffer.clear()

    delay_frames = new_delay

    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    try:
        frame1 = cv2.resize(frame1, (width, height))
        frame2 = cv2.resize(frame2, (width, height))
        frame2 = ~frame2

    except:
        stop_camera()

    frame_buffer.append(frame2)

    if len(frame_buffer) > delay_frames:
        delayed_frame = frame_buffer.pop(0)
        alpha = 0.5
        blended_frame = cv2.addWeighted(frame1, alpha, delayed_frame, alpha, 0)
        cv2.imshow("Motion Camera", blended_frame)

    # Calculate the delay based on the framerate of the video
    delay = int(1000 / framerate)
    root.after(delay, update_frame)

def select_camera():
    global cap1, cap2, frame_buffer
    cap1 = initialize_camera(camera_combobox.get())
    cap2 = initialize_camera(camera_combobox.get())
    frame_buffer = []

    update_frame()

def start_camera():
    global stop_camera_flag, video_path, framerate
    stop_camera_flag = False

    selected_device = camera_combobox.get()

    if selected_device == "Local File":
        video_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov")]
        )
        if not video_path:
            return
        width, height, framerate = get_video_dimensions(video_path)
    else:
        video_path = ""

    thread = threading.Thread(target=select_camera)
    thread.start()

# Helper function to get video dimensions and framerate
def get_video_dimensions(file_path):
    cap = cv2.VideoCapture(file_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    framerate = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return width, height, framerate


def stop_camera():
    """
    Stop the camera and release all resources.

    Parameters:
    None

    Returns:
    None
    """
    global stop_camera_flag
    stop_camera_flag = True
    try:
        cap1.release()
        cap2.release()
    except NameError:
        pass
    cv2.destroyAllWindows()


def on_close():
    """
    Close the application and stop the camera.

    This function is called when the application is closed. It first stops the camera
    by calling the `stop_camera()` function. Then, it destroys the root window by
    calling the `destroy()` method of the `root` object.

    Parameters:
    None

    Returns:
    None
    """
    stop_camera()
    root.destroy()


root = tk.Tk()
root.title("Motion Camera by LeoAqua")
root.geometry("350x300")
root.resizable(False,False)

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

text3 = ttk.Label(root, text="1 (used for fast motion) <=> 50 (used for very slow motion)")
text3.pack()

slider = tk.Scale(root, from_=1, to=50, orient=tkinter.HORIZONTAL)
slider.pack()


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
root.protocol("WM_DELETE_WINDOW", on_close)  # Handle window close event

root.mainloop()
