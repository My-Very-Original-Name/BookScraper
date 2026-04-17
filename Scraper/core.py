from PIL import Image
import io, img2pdf, time, os, shutil
from PyPDF2 import PdfMerger
from . import utils, ui, config_handler, credential_handler, sites

pdf_merger = PdfMerger()

def select_site(text_site_list):
    print("\nSelect a site")
    sites_list = sites.SITES
    for i, class_ in enumerate(sites_list):
        print(f" {utils.color(sites_list.index(class_), "red")}: {utils.color(text_site_list[i], "yellow")}", end = "")
    selected = utils.get_numeric_input(utils.color("\nEnter site index: ", "blue"), 0, len(sites_list)-1)
    utils.clear_console()
    return sites.SITES[int(selected)]()

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
        print(f"\n{utils.color("ERR:  ", "red")}Failed to process image {x}: {e}")

def try_turn(trye):
    try:
        web.turn_page()
    except Exception:
        if trye > 5: raise Exception
        time.sleep(3)
        try_turn(trye +1)

def startup():
    global web
    utils.clear_console()
    print(f"{utils.color("Welcome to BookScraper!\n", "green")}")
    web = select_site(config_handler.load_site_list())
    configs = config_handler.get_configs(web.name)
    print("Starting...")
    username, password = credential_handler.get_credentials(web.name, configs["save_credentials"])
    try:
        web.start(username, password, configs["resolution"])
    except Exception as e:
        utils.stop(web, f"Unexpected error while starting: {e}")
    page_number = utils.get_numeric_input(utils.color(f"Enter number of pages for '{web.book}': ", "blue"), min_val= 1)
    if not os.path.exists(configs["output-path"]):
        os.makedirs(configs["output-path"])
    utils.clear_console()
    return configs, page_number

def get_accurate_crop(default_crop):
    time.sleep(4)
    img = Image.open(io.BytesIO(web.take_screenshot())).convert('RGB')
    utils.clear_console()
    print("Please continue in the new window, select two opposite cornsers of the page. (the window is resizable)")
    time.sleep(1)
    accurrate_rect = ui.get_crop_selection(img)
    if accurrate_rect: return accurrate_rect
    utils.clear_console()
    return default_crop

def core_loop(num_of_pages, configs, cropping_rectangle):
    current_page = 0
    bar = configs["bar"]
    temp_dir = f"{configs["output_path"]}/{web.book}_tmp"
    while current_page <= num_of_pages:
        time.sleep(configs["sleep_page_seconds"])
        if web.name == "Zanichelli(Booktab)":  
            web.check_for_bullshit_popup()
        gen_pdf(get_img(cropping_rectangle) ,current_page, temp_dir)
        try:
            try_turn(0)
        except Exception:
            print(f"{utils.color("ERROR:  ", "red")}could not turn page, compiling up to page {current_page}")
            break
        ui.progress_bar(bar, current_page, num_of_pages, web.name, configs["sleep_page_seconds"])
        current_page += 1
    utils.clear_console()

def save_pdf(configs):
    utils.clear_console()
    output_path = configs["output-path"]
    temp_path = f"{output_path}/{web.book}_temp"
    output_file = f"{output_path}/{web.book}.pdf"
    if os.path.exists(output_file):
        if input(utils.color("WARNING:  ", "red") + f" A file with the same name as the output already exists!: " + utils.color(f"{output_file}", "yellow") +  "\ncontinuing would overwrite it. Do you wish to proceed? (y/n): ").lower() == "n":
            utils.stop(web)
        utils.clear_console()
    print("Merging PDFs...")
    with open(output_file, "wb") as file:
        pdf_merger(file)
    
    pdf_merger.close()
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

def main():
    configs, page_number = startup()
    cropping_rect = get_accurate_crop(configs["cropping_rectangle"])
    core_loop(page_number, configs, cropping_rect)
    save_pdf(configs)
    utils.stop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        utils.stop(web, f"An unexpected error has occured: {e}")
