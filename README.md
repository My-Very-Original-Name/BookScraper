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
- **Linux**
    - (only manual installation)
### Dependencies
- Python 3.7 or higher
- Python packages: full list in *requirements.txt*
- A supported browser (Firefox)

### Installing

**DIRECT INSTALLATION**
* Download the executable (or zip folder for older versions) from the latest relase
-------
**MANUAL INSTALLATION**
* Clone the repo
```
git clone https://github.com/My-Very-Original-Name/BookScraper.git
```
* Install Dependencies 
``` 
pip install -r requirements.txt
```


### Executing program

**MANUAL INSTALLATION**: run main.py 

windows
```
python main.py
``` 
Linux
```
python3 main.py
``` 
**DIRECT INSTALLATION**

run BookScraper.exe
## Common issues
* Not all Cambridge go books are Supported
* Some sites require to manually reset the book page to 1 before running the program
* The program might open a browser window when interacting with some websites, Do not close, resize or in some cases minimize it (occasionally breaks the rendering) 



## License

This project is licensed under the MIT License - see the LICENSE.md file for details


