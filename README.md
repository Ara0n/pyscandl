# pyscandl
**DISCLAIMER:** This project is just a technical demo, don't download scans and get the mangas from official retailers when they are accessible in your country

This modular program to be able to download manga and webtoon scans from the internet, it'll use an image fetcher specific for each website while respecting an API.  
The API will enable you to create your own image fetchers for other websites not supported yet by the program.  
There is a `banlist/` folder where you can place the images you don't want to appear in your pdf.

## installation
### from source
1) check if you have `python3.7` installed

2) check if you have `pip` for python3.7 installed
3) clone the repository from source
4) install the dependencies for the program
```
cd path/to/project/root
pip3 install -r requirements.txt #might be pip instead of pip3 and need to be done as admin/sudo or in a venv
```
5) install the [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) for firefox
6) you can now use the program

**you can update it by running `python3 main.py -U`**

### from release
1) check if you have `python3.7` installed

2) check if you have `pip` for python3.7 installed
3) install the repository from the [latest release](https://github.com/Ara0n/pyscandl/release/latest)
4) install the dependencies for the program
```
cd path/to/project/root
pip3 install -r requirements.txt #might be pip instead of pip3 and need to be done as admin/sudo or in a venv
```
5) install the [geckodriver](https://github.com/mozilla/geckodriver/releases/latest) for firefox
6) you can now use the program  
**you'll need to download each release from the [release page](https://github.com/Ara0n/pyscandl/release), but it'll be lighter in comparison**

## dependence
This is a python3 program that uses:
- `argparse` for the main
- [`selenium`](https://selenium-python.readthedocs.io/installation.html) for some of the default parsers
- `requests` for some other parsers
- `img2pdf` to create the pdfs of the scans
- `os`, `re`, `GitPython` and `enum` are also needed

**for the full dependence list, check `requirments.txt`**

It is developed on a Debian 10 Buster computer so it is verified for Debian 10 and should work at least for the older debians and the debian-likes, provided that you have the dependencies listed up above.  
As for other linux distribution, windows and MacOSX I haven't tested the compatibility (windows will be tested later down the run) but it may work if you have all the dependencies.

## command line interface
`python3 main.py [--keep-images|-k] [--quiet|-q] <--fetcher|-f fname> <--link|-l link | --manga|-m mname> [--chapter-start|-c chapnumber] [--all|-a | --download-number|-n number] [--output|-o path] [--start|-s number] [-t|--tiny] [-U|--update]`
*might be only `python` for windows*

- `--output` or `-o` **required**: the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder `images` with inside one folder per chapter and the pdfs will be stored in a `pdf` subfolder 
- `--fetcher` or `-f` **required**: the name of the image links fetcher that will be used for the download
- `--link` or `-l` **required if not using `--manga` or `-m`**: gives the link to the page with all the chapter listed
- `--manga` or `-m` **required if not using `--link` or `-l`**: gives the manga name, the image fetcher will find the corresponding manga
- `--chapter-start` or `-c`: gives the chapter to start the download on (defaults at 1)
- `--download-number` or `-n`: gives the number of chapters to download (defaults at 1)
- `--all` or `-a`: downloads all the chapters from the starting point to the end
- `--keep-images` or `-k`: the images used for the pdf will be kept in their corresponding folder
- `--quiet` or `-q`: removes the verbose of the downloads
- `--skip` or `-s`: skips `n` images before starting to download the first chapter
- `--tiny` or `-t`: don't write the manga name in the title (useful if using collections)
- `--update` or `-U`: updates the program to the latest release on github, **you must have cloned the repo to use it**

## image fetcher API
- `.image` is a `string` with link to the image  
- `.next_image()` changes `.image` to the next in the chapter  
- `.next_chapter()` changes `.image` to the first in the next chapter
- `.is_last_image()` which returns `True` if it's the last page of the chapter
- `.is_last_chapter()` which returns `True` if it's the last chapter available 
- `.author` string with the name of the author, defaults to `"TBD"` if nothing is found
- `.ext` string with the image extention name
- `.manga_name` is a `string` with the complete name of the manga or the webtoon of the current `.image`
- `.author` string containing the name of the author (not the artist) if nothing is found it has a value of `"TBD"`
- `.ext` is a string containing the extension type of the image
- `.chapter_number` is an `int` (or a `float` if the chapter is an extra) containing the number of the chapter or the current `.image`
- `.chapter_name` is a `string` containing the title of the chapter of the current `.image` (the `string` is empty if no name is detected) 
- `.npage` is an `int` giving the current page of the fetcher
- `quit()` to close properly the fetcher
- needs to raise the `MangaNotFound` exception from `exceptions` if the manga is not found

## Pyscandl()
`Pyscandl(self, fetcher, chapstart:int=1, output:str=".", keepimage:bool=False, all:bool=False, link:str=None, manga:str=None, download_number:int=1, quiet:bool=False, start:int=0, tiny:bool=False)`

### args and kwargs
- `fetcher` will be the fetcher object used in this instance, there will be an `enum` with all the fetchers available (I strongly recommend if you make your own fetcher to place it in the enum too)
- `chapstart=` is an `int` (or a `float` in case of extra chapters) for the starting point of the fetching
- `output=` determines the output folder for the pdfs and the images (if kept)
- `keepimage=` determines if the images are downloaded instead of loaded into the RAM
- `all=` determines if you need to download all the available chapters or not
- `link=` **required if not using `manga=`**, is a `string` containing the link to the root page with the list of all the chapters
- `manga=` **required if not using `link=`**, is a `string` containing the complete manga name
- `download_number=` **required if `all=False`**, is an `int` containing the number of chapters we need to download
- `quiet=` deactivates the verbose while downloading

