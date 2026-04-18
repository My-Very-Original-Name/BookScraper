import os
import tabulate

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

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
    print(color(r"""    ____                 __   _____                                      
   / __ ) ____   ____   / /__/ ___/ _____ _____ ____ _ ____   ___   _____
  / __  |/ __ \ / __ \ / //_/\__ \ / ___// ___// __ `// __ \ / _ \ / ___/
 / /_/ // /_/ // /_/ // ,<  ___/ // /__ / /   / /_/ // /_/ //  __// /    
/_____/ \____/ \____//_/|_|/____/ \___//_/    \__,_// .___/ \___//_/     
                                                   /_/                   """, "bold_purple"))
    print("\n\n")

def get_numeric_input(prompt, min_val=0, max_val=None):
    while True:
        try:
            value = int(input(color(prompt, "blue")))
            if min_val <= value and (max_val is None or value <= max_val):
                return value
            print(color(f"Invalid input:", "red") + f"Please enter a value between {min_val} and {max_val}.")
        except ValueError:
            print(color("Invalid input:") + "Please insert a numeric value.")

def selector_table(items, header:str = "Name"):
    print(tabulate.tabulate(items, headers=['Index', header], tablefmt='pipe', colalign=("center", "center")))

def stop(web, error_text:str =None):
    clear_console()
    try:
        web.quit()
    except Exception:
        print(color("ERROR:  ", "red") + f"Failed to stop web component correctly")
    if error_text:
        print(color("ERROR:  ", "red") + f"A critical error has occured, {error_text}")
        input("Quitting... press ENTER to exit")
        exit(1)
    exit(0)