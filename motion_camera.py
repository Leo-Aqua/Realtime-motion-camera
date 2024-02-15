import cv2
import tkinter as tk
from PIL import Image, ImageTk
import webbrowser

class WebcamApp:
    def __init__(self, window, window_title):
        
        self.delay_frames = 5
        self.framebuffer = []
        self.framecounter = 0
        self.recording = False

        self.window = window
        self.window.title(window_title)
        
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source)
        
        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack(side=tk.LEFT)
        
        self.debug_info_label = tk.Label(window, text="Show debug info")
        self.debug_info_label.pack(side=tk.TOP)
        self.debug_info_check_var = tk.IntVar()
        self.debug_info_check = tk.Checkbutton(window, variable=self.debug_info_check_var)
        self.debug_info_check.pack(side=tk.TOP)

        self.recording_label = tk.Label(window, text="Record: ")
        self.recording_label.pack(side=tk.TOP)
        self.recording_check_var = tk.IntVar()
        self.recording_check = tk.Checkbutton(window, variable=self.recording_check_var)
        self.recording_check.pack(side=tk.TOP)
        
        self.delay_label = tk.Label(window, text="Delay: ")
        self.delay_label.pack(side=tk.TOP)
        self.delay_input_var = tk.StringVar()
        self.delay_input = tk.Spinbox(window, from_=0, to=100, increment=1, width=5 ,textvariable=self.delay_input_var)
        self.delay_input_var.set(1)
        self.delay_input.pack(side=tk.TOP)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output.avi', self.fourcc, 20.0, (640,  480))

        credits = tk.Label(window, text="Credits:\nCreated by LeoAqua\nOriginal Idea from Posy\nLinks:")
        credits.pack()

        def callback(link):
            webbrowser.open_new(link)

        link = tk.Label(window, text="My GitHub", fg="blue", cursor="hand2")
        link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Leo-Aqua"))
        link.pack()

        link2 = tk.Label(window, text="Posy's YT", fg="blue", cursor="hand2")
        link2.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://www.youtube.com/@PosyMusic"))
        link2.pack()
        
        self.update()
        
        self.window.mainloop()
        
    

    
    def update(self):
        self.framecounter += 1

        ret, frame = self.vid.read()
        show_debug = self.debug_info_check_var.get()
        try:
            new_delay = int(self.delay_input.get())
        except ValueError:
            new_delay = self.delay_frames
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            if new_delay < self.delay_frames:
                self.framebuffer.clear()
            self.delay_frames = new_delay

            # Apply transparency and inversion

            delayed_frame = ~frame # invert Image
            blended_frame = None
            self.framebuffer.append(delayed_frame)
            if len(self.framebuffer) > self.delay_frames + 1:
                delayed_frame = self.framebuffer.pop(0)
                blended_frame = cv2.addWeighted(frame, 0.5, delayed_frame, 0.5, 0)

                h, w, _ = blended_frame.shape
                if h > 600 or w > 800:
                    frame = cv2.resize(frame, (800, 600))
                if show_debug: #               image,           text,                  org,     fontFace,          fontScale, color, thickness, lineType
                    blended_frame = cv2.putText(
                        blended_frame,
                        f"frame: {self.framecounter}",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        1,
                        cv2.LINE_AA,
                    )
                    blended_frame = cv2.putText(
                        blended_frame,
                        f"delay: {str(self.delay_frames)}",
                        (50, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        1,
                        cv2.LINE_AA,
                    )
                    blended_frame = cv2.putText(
                        blended_frame,
                        f"recording: {str(self.recording_check_var.get())}",
                        (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        1,
                        cv2.LINE_AA,
                    )


                # Convert overlayed_frame to PhotoImage
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(blended_frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                if self.recording_check_var.get():
                    rgb = cv2.cvtColor(blended_frame, cv2.COLOR_RGB2BGR)
                    self.out.write(rgb)
        self.window.after(1, self.update)

def main():
    root = tk.Tk()
    app = WebcamApp(root, "MotionCam")
    
if __name__ == '__main__':
    main()
