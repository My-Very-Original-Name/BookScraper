# BookScraper

BookScraper is Python script that automates the prosess of downloading and converting **Pre-Owned** digital books from varius, mostly italian educational sites

## Features
- **Automatic login:** Uses saved credentials or propts for user input
- **Page scraping:** Automatically navigates through the book and generates a PDF
- **Customisable settings:** Scan resolutio, cropping and predefined loading times can be cunfigured per sites
- **PDF generation:** each page is converted to an image and then merged to a final PDF

### Supported Sites

- Cambridge go
- Zanchelli E-reader (Booktab)
- Hub scuola
- Loescher(Mylim)
- Sanoma
- Bsmart


## Getting Started
### Supported platforms
- **Windows**
    - Windows 10+ (Fully supported)
    - Windows 7/8/8.1 (untested)
### Dependencies
- Python 3.7 or higher
- Python packages: full list in *requirements.txt*
- A supported browser (Firefox)

### Installing

* Clone the repo
```
git clone https://github.com/My-Very-Original-Name/BookScraper.git
```
* Install Dependencies 
``` 
pip install -r requirements.txt
```
* Add an "output" folder

**If using the pre-compiled exe**
* Download the latest relase
* Add am "output" folder
* Run the exe
### Executing program

* Run *run.bat* or *Bookscraper.exe*

## Common issues
* Not all Cambridge go books are Supported
* Some sites require to manually reset the book page to 1 before running the program



## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Future plans
* Linux/mac Os support
* Improved error handling

