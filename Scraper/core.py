from PIL import Image
import io, img2pdf, time, os, shutil
from PyPDF2 import PdfMerger
from pyvirtualdisplay import Display as VirtDisplay
import platform
from . import ui, config_handler, credential_handler, sites
from sites.base import InvalidLoginError

pdf_merger = PdfMerger()

def select_site():
    text_site_list = sites.TEXT_SITES
    i = ui.print_selector_table(text_site_list, header="Site")
    ui.clear_console()
    return sites.SITES[i]()

def get_img(cropping_rectangle):
    img = Image.open(io.BytesIO(web.take_screenshot()))
    if img.mode in ('RGBA', 'LA'):
        img = img.convert('RGB')
    return img.crop(cropping_rectangle)

def gen_pdf(img, x, temp_dir):
    try:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        pdf_bytes = img2pdf.convert(img_bytes)
        temp_pdf_path = f"{temp_dir}/temp_{x}.pdf"
        with open(temp_pdf_path, "wb") as temp_pdf:
            temp_pdf.write(pdf_bytes)
        pdf_merger.append(temp_pdf_path)  
    except Exception as e:
        print(f"\n{ui.color("ERR:  ", "red")}Failed to process image {x}: {e}")

def try_turn(trye):
    try:
        web.turn_page()
    except Exception as e:
        if trye > 5:
            raise Exception(e)
        time.sleep(3)
        try_turn(trye +1)

def startup():
    global web
    ui.clear_console()
    ui.rPrint("[#A7FC00]Welcome to BookScraper![/#A7FC00]\n")

    web = select_site()
    configs = config_handler.get_configs(web.name)
    ui.clear_console()
    username, password = credential_handler.get_credentials(web.name, configs["save_credentials"])
    while True:
        try:
            if web.can_run_headless:
                web.start(username, password, configs["resolution"])
            else:
                start_web_in_virtual_screen(web, username, password, configs["resolution"])
            break
        except InvalidLoginError:
            ui.clear_console()
            ui.print_warning("Password or username are incorrect, please retry. Restarting...")
            web.quit()
        except Exception as e:
            ui.display_err_and_stop(web, f"Unexpected error while starting: {e}")
            username, password = credential_handler.get_credentials(web.name, configs["save_credentials"], correct_old_credentials= True)

    ui.clear_console()
    page_number = ui.get_numeric_input("[#00E5FF]Enter number of pages for '[/#00E5FF]" + f"{web.book}" + "[#00E5FF]'[/#00E5FF]", min_val= 1)
    if not os.path.exists(configs["output_path"]):
        os.makedirs(configs["output_path"])
    ui.clear_console()
    return configs, page_number

def start_web_in_virtual_screen(web, username, password, resolution):
    width = resolution[0]
    height = resolution[1]
    system = platform.system()
    if system == "Linux":
        os.environ["REAL_DISPLAY"] = os.environ.get("DISPLAY", "")
        d = VirtDisplay(visible=False, size=(width, height))
        d.start()
        web.virtual_display = d
        web.start(username, password, resolution)
    elif system == "Windows":
        web.start(username, password, resolution, (-(width + 3000), -(height + 3000)))

def get_accurate_crop(default_crop):
    time.sleep(4)
    img = Image.open(io.BytesIO(web.take_screenshot())).convert('RGB')
    ui.clear_console()
    print("Please continue in the new window, select two opposite cornsers of the page. (the window is resizable)")
    time.sleep(1)

    real_display = os.environ.get("REAL_DISPLAY")
    virtual_display = os.environ.get("DISPLAY")
    if real_display:
        os.environ["DISPLAY"] = real_display

    accurrate_rect = ui.get_crop_selection(img)

    if real_display:
        os.environ["DISPLAY"] = virtual_display
        
    if accurrate_rect: return accurrate_rect
    ui.clear_console()
    return default_crop

def core_loop(num_of_pages, configs, cropping_rectangle):
    current_page = 0
    bar = configs["bar"]
    temp_dir = f"{configs["output_path"]}/{web.book}_tmp"
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    while current_page < num_of_pages:
        if os.path.exists(f"{temp_dir}/temp_{current_page}.pdf"):
            os.remove(f"{temp_dir}/temp_{current_page}.pdf")
        time.sleep(configs["sleep_page_seconds"])
        if web.name == "Zanichelli(Booktab)":  
            web.check_for_bullshit_popup()
        gen_pdf(get_img(cropping_rectangle) ,current_page, temp_dir)
        try:
            try_turn(0)
        except Exception:
            print(f"{ui.color("ERROR:  ", "red")}could not turn page, compiling up to page {current_page}")
            time.sleep(2)
            break
        current_page += 1
        bar = ui.progress_bar(bar, current_page, num_of_pages, web.name, configs["sleep_page_seconds"])
    ui.clear_console()

def save_pdf(configs):
    ui.clear_console()
    output_path = configs["output_path"]
    temp_path = f"{output_path}/{web.book}_tmp"
    output_file = f"{output_path}/{web.book}.pdf"
    if os.path.exists(output_file):
        if input(ui.color("WARNING: ", "red") + f" A file with the same name as the output already exists!: " + ui.color(f"'{output_file}'", "bold_white") +  "\ncontinuing would overwrite it. Do you wish to proceed? (y/n): ").lower() == "n":
            ui.display_err_and_stop(web)
        ui.clear_console()
    print("Merging PDFs...")
    with open(output_file, "wb") as file:
        pdf_merger.write(file)
    ui.clear_console()
    ui.rPrint(f"[#A7FC00]Succesfully saved pdf to: [/#A7FC00][bold white]{output_file}[/bold white]")
    pdf_merger.close()
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    input(f"Press {ui.color("ENTER", "bold_white")} to exit")

def main():
    web = None
    try:
        configs, page_number = startup()
        cropping_rect = get_accurate_crop(configs["cropping_rectangle"])
        core_loop(page_number, configs, cropping_rect)
        save_pdf(configs)
        ui.display_err_and_stop(web)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt by user.")
        ui.display_err_and_stop(web=web)
        exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        ui.display_err_and_stop(web, f"An unexpected error has occured: {e}")
