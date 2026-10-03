from PIL import Image
import io, img2pdf, time, os, shutil
from PyPDF2 import PdfMerger
from pyvirtualdisplay import Display as VirtDisplay
import platform, re
from rich.markup import escape
from . import ui, config_handler, credential_handler, sites
from .sites.base import InvalidLoginError

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
        img.save(img_bytes, format="JPEG", quality=95, subsampling=0, optimize=True)
        img_bytes.seek(0)
        pdf_bytes = img2pdf.convert(img_bytes)
        temp_pdf_path = f"{temp_dir}/temp_{x:05d}.pdf" 
        with open(temp_pdf_path, "wb") as temp_pdf:
            temp_pdf.write(pdf_bytes)
    except Exception as e:
        ui.print_error(f"Failed to process image {x}: {e}", sleep_seconds=1.5)

def try_turn(trye):
    try:
        web.turn_page()
    except sites.macmillan.MacmillanFailedPageExeption:
        raise sites.macmillan.MacmillanFailedPageExeption
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
            ui.print_warning("Username or Password is incorrect, please retry.\n")
            web.quit()
            username, password = credential_handler.get_credentials(web.name, configs["save_credentials"], correct_old_credentials= True)
        except Exception as e:
            ui.display_err_and_stop(web, f"Unexpected error while starting: {e}")
            

    ui.clear_console()
    page_number = ui.get_numeric_input("[#00E5FF]Enter number of pages for '[/#00E5FF]" + escape(web.book) + "[#00E5FF]'[/#00E5FF]",min_val=1,)
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
        real_wayland = os.environ.pop("WAYLAND_DISPLAY", None)
        try:
            d = VirtDisplay(visible=False, size=(width, height))
            d.start()
            web.virtual_display = d
            web.start(username, password, resolution)
        finally:
            if real_wayland:
                os.environ["WAYLAND_DISPLAY"] = real_wayland
        
    else:
        web.start(username, password, resolution, (-(width + 3000), -(height + 3000)))

def get_accurate_crop(default_crop):
    time.sleep(4)
    img = Image.open(io.BytesIO(web.take_screenshot())).convert('RGB')
    ui.clear_console()
    print("Please continue in the new window and select two opposite corners of the page. (the window is resizable)")
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
    book_name = sanitize_filename(web.book)
    temp_dir = os.path.join(configs["output_path"], f"{book_name}_tmp")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.mkdir(temp_dir)
    
    if web.name == "Macmillan":
        web.cropping_rectangle = cropping_rectangle
    print("\033[?25l", end="")

    while current_page < num_of_pages:
        time.sleep(configs["sleep_page_seconds"])

        if web.name == "Zanichelli(Booktab)":  
            web.check_for_bullshit_popup()

        gen_pdf(get_img(cropping_rectangle) ,current_page, temp_dir)

        is_last_page = current_page == num_of_pages - 1
        if not is_last_page:
            try:
                try_turn(0)
            except Exception:
                print(f"{ui.color("ERROR:  ", "red")}could not turn page, compiling up to page {current_page + 1}")
                time.sleep(2)
                break

        current_page += 1
        bar = ui.progress_bar(bar, current_page, num_of_pages, web.loading_reminder, configs["sleep_page_seconds"])
    
    print("\033[?25h", end="")
    ui.clear_console()

def sanitize_filename(name, max_len=120):
    name = " ".join(str(name).split())
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    name = name.strip(" .")
    return name[:max_len].rstrip(" .") or "book"

def save_pdf(configs):
    ui.clear_console()
    output_path = configs["output_path"]
    book_name = sanitize_filename(web.book)
    temp_path = os.path.join(output_path, f"{book_name}_tmp")
    output_file = os.path.join(output_path, f"{book_name}.pdf")
    
    if not os.path.exists(temp_path):
        ui.display_err_and_stop(web, "Failed to locate temp dir.")

    if os.path.exists(output_file):
        value = 1
        while True:
            output_file = os.path.join(output_path, f"{book_name}({value}).pdf")
            if not os.path.exists(output_file): break
            value +=1
            if value > 500:
                ui.display_err_and_stop(web, "You really have 500 files with the same name? Just what are you doing...")

    print("Merging PDFs...")

    merger = PdfMerger()
    
    pdf_files = sorted([f for f in os.listdir(temp_path) if f.endswith(".pdf")])
    if not pdf_files:
        ui.display_err_and_stop(web, "No temp pdf files found in temp dir. Did the scan fail?")
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)

    for pdf_file in pdf_files:
        full_path = os.path.join(temp_path, pdf_file)
        with open(full_path, "rb") as f:
            merger.append(f)

    with open(output_file, "wb") as file:
        merger.write(file)

    merger.close()

    ui.clear_console()
    ui.rPrint(f"[#A7FC00]Successfully saved pdf to: [/#A7FC00][bold white]{escape(output_file)}[/bold white]")
    
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    input(f"Press {ui.color('ENTER', 'bold_white')} to exit")

def main():
    global web
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
