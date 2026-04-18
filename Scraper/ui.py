from PIL import Image
import tkinter as tk
import io
#local imports
from . import utils 

def get_crop_selection(image):
    """
    Opens a GUI to select cropping area from an image.
    
    Args:
        image: PIL Image object
        
    Returns:
        list: [left, top, right, bottom] crop coordinates, or None if cancelled (use default)
    """
 
    root = tk.Tk()
    root.title("Select Cropping Area")
    root.resizable(True, True)
    root.geometry("800x650")
    
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    canvas = tk.Canvas(main_frame, bg='white', cursor="crosshair") 
    canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    clicks = []
    rect_id = None
    crop_rectangle = None
    current_photo = None
    current_scale_factor = 1.0
    
    def update_image():
        nonlocal current_photo, current_scale_factor, rect_id
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return 
        
        current_scale_factor = min(canvas_width / image.width, canvas_height / image.height)
        display_size = (int(image.width * current_scale_factor), int(image.height * current_scale_factor))
        
        scaled_image = image.resize(display_size, Image.LANCZOS)
        
        img_bytes = io.BytesIO()
        scaled_image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        current_photo = tk.PhotoImage(data=img_bytes.getvalue())
        
        canvas.delete("all")
        rect_id = None 
        
        img_x = (canvas_width - display_size[0]) // 2
        img_y = (canvas_height - display_size[1]) // 2
        
        canvas.create_image(img_x, img_y, image=current_photo, anchor=tk.NW)
        
        clicks.clear()
        confirm_btn.config(state=tk.DISABLED)
        retry_btn.config(state=tk.DISABLED)
    
    def on_click(event):
        nonlocal clicks, rect_id
        
        if not current_photo:
            return
        
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        img_width = int(image.width * current_scale_factor)
        img_height = int(image.height * current_scale_factor)
        
        img_x = (canvas_width - img_width) // 2
        img_y = (canvas_height - img_height) // 2
        
        rel_x = event.x - img_x
        rel_y = event.y - img_y
        
        if rel_x < 0 or rel_x >= img_width or rel_y < 0 or rel_y >= img_height:
            return 
        
        if len(clicks) >= 2:
            update_image()
        
        clicks.append((event.x, event.y))
        
        canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill='red', outline='red')
        
        if len(clicks) == 2:
            x1, y1 = clicks[0]
            x2, y2 = clicks[1]
            
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            
            rect_id = canvas.create_rectangle(left, top, right, bottom, outline='red', width=2, fill='', stipple='gray50')
            confirm_btn.config(state=tk.NORMAL)
            retry_btn.config(state=tk.NORMAL)
    
    def confirm():
        nonlocal crop_rectangle
        if len(clicks) == 2:
            x1, y1 = clicks[0]
            x2, y2 = clicks[1]
            
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            img_width = int(image.width * current_scale_factor)
            img_height = int(image.height * current_scale_factor)
            img_x_offset = (canvas_width - img_width) // 2
            img_y_offset = (canvas_height - img_height) // 2

            orig_x1 = int((x1 - img_x_offset) / current_scale_factor)
            orig_y1 = int((y1 - img_y_offset) / current_scale_factor)
            orig_x2 = int((x2 - img_x_offset) / current_scale_factor)
            orig_y2 = int((y2 - img_y_offset) / current_scale_factor)
            
            left = max(0, min(orig_x1, orig_x2))
            top = max(0, min(orig_y1, orig_y2))
            right = min(image.width, max(orig_x1, orig_x2))
            bottom = min(image.height, max(orig_y1, orig_y2))
            
            crop_rectangle = [left, top, right, bottom]
            root.destroy()
    
    def use_default():
        nonlocal crop_rectangle
        crop_rectangle = None
        root.destroy()

    def retry():
        update_image()
        
    canvas.bind("<Button-1>", on_click)
    
    canvas.bind("<Configure>", lambda event: root.after_idle(update_image)) 
    
    instruction_label = tk.Label(root, text="Click two opposite corners to select cropping area")
    instruction_label.pack()
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=5)
    
    confirm_btn = tk.Button(button_frame, text="Confirm", command=confirm, state=tk.DISABLED)
    confirm_btn.pack(side=tk.LEFT, padx=5)

    retry_btn = tk.Button(button_frame, text="Retry", command=retry, state=tk.DISABLED)
    retry_btn.pack(side=tk.LEFT, padx=5)
    
    use_default_btn = tk.Button(button_frame, text="Use Default", command=use_default)
    use_default_btn.pack(side=tk.LEFT, padx=5)
    
    root.update_idletasks() 
    update_image()
    
    root.mainloop()
    
    return crop_rectangle


def progress_bar(bar, progress, total, web_name, sleep_page_seconds):
    max_icon = int((len(bar) * progress) / total)
    utils.clear_console()
    if web_name == "Zanichelli(Booktab)":
        print(f"{utils.color("WARNING:  ", "yellow")}Do not resize, close or minimize the browser window")
    for i in range(max_icon):
        bar[i] = utils.color("█", "purple")

    percentage = round((100 * progress) / total, 1)
    etc = sleep_page_seconds*(total -progress)
    if etc >= 3600:
        etc_str = f"{round(etc / 3600,1)} hours"
    elif etc >= 60:
        etc_str = f"{round(etc / 60,1)} minutes"
    else:
        etc_str = f"{round(etc,1)} seconds"
    print(
        f"{utils.color('Scanning:', 'blue')} {utils.color(f'{percentage}%', 'bold_green')}  "
        f"{''.join(bar)} "
        f"[ {utils.color(progress, 'yellow')} / {utils.color(total, 'yellow')} ] pages - {utils.color("ETC: ", "blue")}{utils.color(etc_str, "bold_white")}       ",
        end="\r"
    )
    return bar