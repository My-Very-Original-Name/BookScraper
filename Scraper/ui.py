from PIL import Image
import tkinter as tk
import io
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import print as rPrint
from rich.prompt import IntPrompt
import os
#local imports

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
    raw_fill = (len(bar) * progress) / total
    max_icon = int(raw_fill)
    decimal_part = raw_fill % 1
    clear_console() 
    if web_name == "Zanichelli(Booktab)":
        print_reminder("Zanichelli does not work in headless mode, if you see a browser window do not resize, close or minimize it.")
    for i in range(max_icon):
        bar[i] = color("█", "purple")
    if decimal_part >= 0.5 and max_icon < len(bar):
        bar[max_icon] = color("▒", "bold_white")
    percentage = round((100 * progress) / total, 1)
    etc = sleep_page_seconds * (total - progress)
    if etc >= 3600:
        etc_str = f"{round(etc / 3600, 1)} hours"
    elif etc >= 60:
        etc_str = f"{round(etc / 60, 1)} minutes"
    else:
        etc_str = f"{round(etc, 1)} seconds"
    print(
        f"{color('Scanning:', 'blue')} {color(f'{percentage}%', 'bold_green')}  "
        f"{''.join(bar)} "
        f"[ {color(progress, 'yellow')} / {color(total, 'yellow')} ] pages - "
        f"{color('ETC: ', 'blue')}{color(etc_str, 'bold_white')}       ",
        end="\r"
    )
    return bar

def print_selector_table(values_list:list[str], header="Title", ask_selection = True):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta",row_styles=["on grey11", "on grey15"])
    table.add_column("Index", style="#FF0000", width=5, justify="center")
    table.add_column(header)
    for i, title in enumerate(values_list):
        table.add_row(
            f"{i}",
            f"{title}"
        )
    console.print(table)
    if not ask_selection: return
    choice = Prompt.ask(f"[#00E5FF]Insert {header.lower()}[/#00E5FF][#FF0000] index[/#FF0000]", choices=[str(choice) for choice in range(len(values_list))], show_choices=False)
    return int(choice)

def print_reminder(message:str):
    if not message: return
    rPrint(f"[bold purple]REMINDER:[/bold purple] {message}")

def print_warning(message:str):
    if not message: return
    rPrint(f"[bold yellow]WARNING:[/bold yellow] {message}")

def generic_user_prompt(prompt:str, choices:list, show_choices = False, default_choice:str = None):
    choices_text = [str(choice) for choice in choices]
    if default_choice:
        if default_choice not in choices_text: raise ValueError(f"The default_choice '{default_choice}' must be one of the provided choices: {choices_text}")
        if show_choices:
            i = choices_text.index(default_choice)
            choices_text[i] = choices_text[i].capitalize()
        return Prompt.ask(prompt=f"[#00E5FF]{prompt}[/#00E5FF]", choices=choices_text, show_choices=show_choices, default=default_choice, show_default=False, case_sensitive=False).lower()
    return Prompt.ask(prompt=f"[#00E5FF]{prompt}[/#00E5FF]", choices=choices_text, show_choices=show_choices, case_sensitive=False).lower()

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
    rPrint("[bold purple]" + r"""    ____                 __   _____                                      
   / __ ) ____   ____   / /__/ ___/ _____ _____ ____ _ ____   ___   _____
  / __  |/ __ \ / __ \ / //_/\__ \ / ___// ___// __ `// __ \ / _ \ / ___/
 / /_/ // /_/ // /_/ // ,<  ___/ // /__ / /   / /_/ // /_/ //  __// /    
/_____/ \____/ \____//_/|_|/____/ \___//_/    \__,_// .___/ \___//_/     
                                                   /_/                   """ + "[/bold purple]")
    print("\n")

def get_numeric_input(prompt, min_val=0, max_val=None):
    while True:
        value = IntPrompt.ask(prompt)
        
        if value >= min_val and (max_val is None or value <= max_val):
            return value
            
        if max_val is not None:
            rPrint(f"[bold red]Invalid input:[/bold red] Please enter a value between {min_val} and {max_val}.")
        else:
            rPrint(f"[bold red]Invalid input:[/bold red] Please enter a value greater than or equal to {min_val}.")

def color(string:str, color:str):
    """
    Available colors: black, red, green, yellow, blue, purple, cyan, white. Prefix with `bold_` for bold version
    """
    ansi_colors = {
        # Reset
        "reset": "\033[0m",

        # Standard Colors (Normal)
        "black": "\033[0;30m",
        "red": "\033[0;31m",
        "green": "\033[0;32m",
        "yellow": "\033[0;33m",
        "blue": "\033[0;34m",
        "purple": "\033[0;35m",
        "cyan": "\033[0;36m",
        "white": "\033[0;37m",

        # bold Colors
        "bold_black": "\033[1;30m",
        "bold_red": "\033[1;31m",
        "bold_green": "\033[1;32m",
        "bold_yellow": "\033[1;33m",
        "bold_blue": "\033[1;34m",
        "bold_purple": "\033[1;35m",
        "bold_cyan": "\033[1;36m",
        "bold_white": "\033[1;37m",
    }
    if color not in ansi_colors.keys():
        raise ValueError("Invalid color")
    return ansi_colors[color] + str(string) + ansi_colors["reset"]

def display_err_and_stop(web, error_text:str =None):
    try:
        if web:
            web.quit()
    except Exception:
        clear_console()
        print(color("ERROR:  ", "red") + f"Failed to stop web component correctly")
    if error_text:
        clear_console()
        print(color("ERROR:  ", "red") + f"A critical error has occured, {error_text}")
        input(f"Quitting... press {color("ENTER", "bold_white")} to exit")
        exit(1)
    exit(0)