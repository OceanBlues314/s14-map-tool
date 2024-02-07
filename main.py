import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk


class DraggableImage:
    def __init__(self, canvas, x, y, image, **kwargs):
        self.canvas = canvas
        self.image = image
        self.item = canvas.create_image(x, y, image=self.image, **kwargs)

        self.drag_data = {"x": 0, "y": 0}
        self.canvas.tag_bind(self.item, "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind(self.item, "<ButtonRelease-1>", self.on_drag_stop)
        self.canvas.tag_bind(self.item, "<B1-Motion>", self.on_drag)

    def on_drag_start(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag_stop(self, event):
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def on_drag(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]

        self.canvas.move(self.item, delta_x, delta_y)

        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def delete(self):
        self.canvas.delete(self.item)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("s14 map util")
        self.resizable(False, False)

        # Load the background image using Pillow
        self.bg_image = Image.open("images/s14map.png")
        self.photo = ImageTk.PhotoImage(self.bg_image)
        self.ward_image = Image.open("images/ward.png")

        self.canvas = Canvas(self, width=self.bg_image.width, height=self.bg_image.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")

        self.images = []

        self.image_mode = "Blue"
        self.debug_mode = False  # Debug mode is initially off

        # Pre-spawn images
        self.coordinates = [(892, 733), (1029, 572), (645, 597), (881, 426),
                            (569, 439), (695, 351), (990, 743), (1057, 666),
                            (297, 220), (446, 120)]

        self.pre_spawn_images()
        self.after(100, self.update_debug_info)

        status_frame = tk.Frame(self)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Label for the hotkeys on the left
        self.hotkeys_label = tk.Label(status_frame,
                                      text="Ward/Pink Ward: [W], [Ctrl+W]      Toggle Ward Color Red/Blue: [R], "
                                           "[B]      Delete Ward: [D]",
                                      anchor="w")
        self.hotkeys_label.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Label for the image mode on the right
        self.mode_label = tk.Label(status_frame, text="Ward Selection: Blue", anchor="e")
        self.mode_label.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        # Keybindings
        self.bind("<b>", lambda event: self.set_image_mode("Blue"))
        self.bind("<r>", lambda event: self.set_image_mode("Red"))
        self.bind("<Control-w>", lambda event: self.spawn_image(event, True))
        self.bind("<w>", lambda event: self.spawn_image(event, False))
        self.bind("<d>", self.delete_image)
        #self.bind("<0>", self.toggle_debug_mode)  # prints cursor coordinates

    def set_image_mode(self, mode):
        self.image_mode = mode
        self.mode_label.config(text=f"Ward Selection: {mode}")
        print(f"Image mode set to {mode}")

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        print(f"Debug mode {'on' if self.debug_mode else 'off'}")

    def update_debug_info(self):
        if self.debug_mode:
            x, y = self.winfo_pointerxy()
            canvas_x = self.canvas.winfo_rootx()
            canvas_y = self.canvas.winfo_rooty()
            x -= canvas_x
            y -= canvas_y
            # Print the cursor's position in canvas space
            print(f"Cursor position in canvas: {x}, {y}")
        # continuous update
        self.after(100, self.update_debug_info)

    def spawn_image(self, event, ctrl=False):
        # Determine the cursor position
        x, y = event.x, event.y

        # Select the image based on the current color selection and keypress
        if self.image_mode == "Blue":
            if ctrl:  # Ctrl key is pressed
                image_path = "images/ward2.png"
            else:
                image_path = "images/ward.png"
        else:  # red
            if ctrl:  # Ctrl key is pressed
                image_path = "images/ward2_red.png"
            else:
                image_path = "images/ward_red.png"

        # Load the image and create a draggable instance
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.spawn(x, y, photo)

    def pre_spawn_images(self):
        image_files = ["adc.png", "adc2.png", "jg.png", "jg2.png", "mid.png", "mid2.png", "sup.png", "sup2.png",
                       "top.png", "top2.png"]
        for i, image_file in enumerate(image_files):
            image = Image.open(f"images/prespawn/{image_file}")
            photo = ImageTk.PhotoImage(image)
            x, y = self.coordinates[i]  # Adjust positioning as necessary
            self.spawn(x, y, photo)

    def spawn(self, x, y, image):
        image_item = DraggableImage(self.canvas, x, y, image)
        self.images.append(image_item)

    def delete_image(self, event):
        x, y = self.winfo_pointerxy()
        canvas_x = self.canvas.winfo_rootx()
        canvas_y = self.canvas.winfo_rooty()
        x -= canvas_x
        y -= canvas_y
        for index, image_item in enumerate(reversed(self.images), start=1):
            if index <= len(self.images) - 10:  # Only consider images beyond the first 10 pre-spawned
                coords = self.canvas.coords(image_item.item)
                if len(coords) == 2:
                    img_x, img_y = coords
                    if abs(img_x - x) < (self.ward_image.width // 2) and abs(img_y - y) < (self.ward_image.height // 2):
                        image_item.delete()
                        self.images.remove(image_item)
                        break


if __name__ == "__main__":
    app = Application()
    app.mainloop()
