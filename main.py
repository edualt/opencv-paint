import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

canvas = None  # Variable global para el lienzo
brush_size = 2  # Tamaño inicial del pincel

class DraggableToolbar(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
    
    def on_release(self, event):
        pass
    
    def on_drag(self, event):
        x = self.winfo_x() - self.start_x + event.x
        y = self.winfo_y() - self.start_y + event.y
        self.place(x=x, y=y)

def draw_line(event):
    global img, start_x, start_y, brush_size
    temp_img = img.copy()
    cv2.line(temp_img, (start_x, start_y), (event.x, event.y), (0, 0, 0), brush_size)
    update_canvas(temp_img)

def draw_freehand(event):
    global start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.bind("<B1-Motion>", continue_line)

def continue_line(event):
    global start_x, start_y
    cv2.line(img, (start_x, start_y), (event.x, event.y), (0, 0, 0), brush_size)
    start_x, start_y = event.x, event.y
    update_canvas(img)

def draw_rectangle(event):
    global start_x, start_y, brush_size
    start_x, start_y = event.x, event.y
    canvas.bind("<B1-Motion>", continue_rectangle)
    canvas.bind("<ButtonRelease-1>", end_rectangle)

def continue_rectangle(event):
    global img, start_x, start_y, temp_img
    temp_img = img.copy()
    cv2.rectangle(temp_img, (start_x, start_y), (event.x, event.y), (0, 0, 0), brush_size)
    update_canvas(temp_img)

def end_rectangle(event):
    global img, start_x, start_y
    cv2.rectangle(img, (start_x, start_y), (event.x, event.y), (0, 0, 0), brush_size)
    update_canvas(img)

def draw_circle(event):
    global start_x, start_y, brush_size
    start_x, start_y = event.x, event.y
    canvas.bind("<B1-Motion>", continue_circle)
    canvas.bind("<ButtonRelease-1>", end_circle)

def continue_circle(event):
    global img, start_x, start_y, temp_img
    temp_img = img.copy()
    center = ((start_x + event.x) // 2, (start_y + event.y) // 2)
    radius = int(((event.x - start_x) ** 2 + (event.y - start_y) ** 2) ** 0.5 / 2)
    cv2.circle(temp_img, center, radius, (0, 0, 0), brush_size)
    update_canvas(temp_img)

def end_circle(event):
    global img, start_x, start_y
    center = ((start_x + event.x) // 2, (start_y + event.y) // 2)
    radius = int(((event.x - start_x) ** 2 + (event.y - start_y) ** 2) ** 0.5 / 2)
    cv2.circle(img, center, radius, (0, 0, 0), brush_size)
    update_canvas(img)

def erase(event):
    global img, temp_img, start_x, start_y
    start_x, start_y = event.x, event.y
    canvas.bind("<B1-Motion>", continue_erase)
    canvas.bind("<ButtonRelease-1>", end_erase)

def continue_erase(event):
    global img, temp_img
    temp_img = img.copy()
    cv2.circle(temp_img, (event.x, event.y), 10, (255, 255, 255), -1)
    img = temp_img.copy() 
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
    canvas.config(image=img_tk)
    canvas.image = img_tk
    update_canvas(img)

def end_erase(event):
    global img, start_x, start_y
    start_x, start_y = 0, 0
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")

def update_brush_size(value):
    global brush_size
    brush_size = int(value)

def update_canvas(image):
    global canvas
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
    canvas.config(image=img_tk)
    canvas.image = img_tk

def main():
    global canvas, img, start_x, start_y
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Draggable Toolbar")

    # Crear un lienzo en blanco con OpenCV
    canvas = tk.Label(root)
    canvas.place(x=0, y=0)
    img = 255 * np.ones((600, 800, 3), np.uint8)  # Blanco puro
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(img))
    canvas.config(image=img_tk)

    toolbar = DraggableToolbar(root, width=200, height=50, bg="lightgray")
    toolbar.place(x=0, y=0)

    button1 = tk.Button(toolbar, text="Line", command=lambda: canvas.bind("<Button-1>", start_draw))
    button1.pack(side=tk.LEFT, padx=5, pady=5)

    button2 = tk.Button(toolbar, text="Polyline", command=lambda: canvas.bind("<Button-1>", draw_freehand))
    button2.pack(side=tk.LEFT, padx=5, pady=5)

    button3 = tk.Button(toolbar, text="Rectangle", command=lambda: canvas.bind("<Button-1>", draw_rectangle))
    button3.pack(side=tk.LEFT, padx=5, pady=5)

    button4 = tk.Button(toolbar, text="Circle", command=lambda: canvas.bind("<Button-1>", draw_circle))
    button4.pack(side=tk.LEFT, padx=5, pady=5)

    button5 = tk.Button(toolbar, text="Erase", command=lambda: canvas.bind("<Button-1>", erase))
    button5.pack(side=tk.LEFT, padx=5, pady=5)

    brush_label = tk.Label(toolbar, text="Brush Size:")
    brush_label.pack(side=tk.LEFT, padx=5, pady=5)
    brush_slider = tk.Scale(toolbar, from_=1, to=10, orient=tk.HORIZONTAL, command=update_brush_size)
    brush_slider.pack(side=tk.LEFT, padx=5, pady=5)
    brush_slider.set(2)  # Tamaño inicial del pincel

    start_x, start_y = 0, 0

    def start_draw(event):
        global start_x, start_y
        start_x, start_y = event.x, event.y
        canvas.bind("<B1-Motion>", draw_line)
        canvas.bind("<ButtonRelease-1>", finish_draw)

    def finish_draw(event):
        global start_x, start_y
        canvas.unbind("<B1-Motion>")
        cv2.line(img, (start_x, start_y), (event.x, event.y), (0, 0, 0), brush_size)
        update_canvas(img)

    root.mainloop()

if __name__ == "__main__":
    main()
