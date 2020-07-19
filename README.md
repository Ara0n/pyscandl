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
python3 -m pip install -r requirements.txt
```
5) install `nodejs`
6) you can now use the program

### from release
1) check if you have `python3.7` installed

2) check if you have `pip` for python3.7 installed
3) install the repository from the [latest release](https://github.com/Ara0n/pyscandl/release/latest)
4) install the dependencies for the program
```
cd path/to/project/root
python3 -m pip install -r requirements.txt
```
5) install `nodejs`
6) you can now use the program  
**you'll need to download each release from the [release page](https://github.com/Ara0n/pyscandl/release)**

## requirements
This is a python3 program that uses:
- the dependencies in `requirements.txt`
- `nodejs` for `fanfox` and `cfscrape`

It is developed on a Debian testing (currently Bullseye) computer so it is verified for Debian and should work at least for the older debians and the debian-likes, provided that you have the dependencies listed up above.  
As for other linux distribution, windows and MacOSX I haven't tested the compatibility *(windows may be tested later down the run)* but it should work if you have all the dependencies.

## command line interface
***The `README` info about the commands is currently outdated, please use the `-h` argument to find the uses of the commands if you have a doubt***

*might be only `python` for windows*
### default
`python3 main.py [-h] [-U] [-ml] [-q] {autodl,manga,manual}`

- `--help` or `-h`: shows the help for this mode
- `--update` or `-U`: updates the program to the latest release on github, **you must have cloned the repo to use it**
- `--manga-list` or `-ml`: lists all the mangas in the auto-downloader

### manual
`python3 main.py manual [-h] (-l LINK | -m MANGA) -f FETCHER [-o OUTPUT] [-c CHAPTER_START] [-a | -n DOWNLOAD_NUMBER] [-t] [-q] [-s SKIP] (-p | -k | -i)`

- `--help` or `-h`: shows the help for this mode
- `--link` or `-l` **required if not using `--manga` or `-m`**: gives the link to the page with all the chapter listed
- `--manga` or `-m` **required if not using `--link` or `-l`**: gives the manga name, the image fetcher will find the corresponding manga
- `--fetcher` or `-f` **required**: the name of the image links fetcher that will be used for the download
- `--output` or `-o` **required**: the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder `images` with inside one folder per chapter and the pdfs will be stored in a `pdf` subfolder 
- `--chapter-start` or `-c`: gives the chapter to start the download on (defaults at 1)
- `--all` or `-a`: downloads all the chapters from the starting point to the end
- `--download-number` or `-n`: gives the number of chapters to download (defaults at 1)
- `--tiny` or `-t`: don't write the manga name in the title (useful if using ebook libraries)
- `--quiet` or `-q`: removes the verbose of the downloads
- `--skip` or `-s`: skips `n` images before starting to download the first chapter
- `--pdf` or `-p`: downloads only the pdf
- `--keep` or `-k`: downloads the pdf but also keep the images in a chapter subfolder
- `--image` or `-i`: downloads only the images in a chapter subfolder and don't create the pdf

### manga
`python3 main.py manga [-h] {add,edit,info,chaplist,delete,rmchaps}`
- `--help` or `-h`: shows the help for this mode

#### add
`python3 main.py manga add [-h] -r RSS -l LINK -f FETCHER [-c[CHAP[CHAP...]]] name`
- `name`: name of the manga in the autodl json that will be used
- `--rss` or `-r`: rss link of the `name` manga
- `--rss` or `-r`: rss link of the `name` manga
- `--link` or `-l`: link of the `name` manga
- `--fetcher` or `-f`: fetcher name for the `name` manga
- `--chap` or `-c`: list already downloaded chapters for the `NAME` manga separated by a space *(example: 2 5.5 3 7 50.1)*

#### edit
`python3 main.py manga edit [-h] [-r RSS] [-l LINK] [-f FETCHER] [-c[CHAP[CHAP...]]] name`
- `name`: name of the manga in the autodl json that will be used
- `--rss` or `-r`: rss link of the `name` manga
- `--rss` or `-r`: rss link of the `name` manga
- `--link` or `-l`: link of the `name` manga
- `--fetcher` or `-f`: fetcher name for the `name` manga
- `--chap` or `-c`: list already downloaded chapters for the `NAME` manga separated by a space *(example: 2 5.5 3 7 50.1)*

#### info
`python3 main.py manga info [-h] name`
- `name`: name of the manga in the autodl json that will be used

#### chaplist
`python3 main.py manga chaplist [-h] name`
- `name`: name of the manga in the autodl json that will be used

#### delete
`python3 main.py manga delete [-h] name`
- `name`: name of the manga in the autodl json that will be used

#### rmchaps
`python3 main.py manga rmchaps [-h] name [chap [chap ...]]`
- `name`: name of the manga in the autodl json that will be used

### autodl
`python3 main.py autodl [-h] [-o OUTPUT] [-t] [-q] (-p | -k | -i)`

- `--help` or `-h`: shows the help for this mode
- `--output` or `-o`: the path (absolute or relative) to the folder where to save the data
- `--tiny` or `-t`: don't write the manga name in the title (useful if using ebook libraries)
- `--quiet` or `-q`: removes the verbose of the autodl
- `--pdf` or `-p`: downloads only the pdf
- `--keep` or `-k`: downloads the pdf but also keep the images in a chapter subfolder
- `--image` or `-i`: downloads only the images in a chapter subfolder and don't create the pdf

## image fetcher API
`fetcher(self, link:str=None, manga:str=None, chapstart:int=1):`
### args
- `link=`: link to the manga you initialize the fetcher to
- `manga=`: manga name used to initialize to
- `chapstart=`: chapter on which the fetcher is initialized on
**you MUST give either a `link` or `manga` when initializing**

### API usage
- `.next_image()` changes `.image` to the next in the chapter  
- `.go_to_chapter(chap)` goes to the chapter `chap`
- `.next_chapter()` changes `.image` to the first in the next chapter
- `.is_last_image()` which returns `True` if it's the last page of the chapter
- `.is_last_chapter()` which returns `True` if it's the last chapter available 
- `quit()` to close properly the fetcher
- `.author` string with the name of the author, defaults to `"TBD"` if nothing is found
- `.chapter_number` is an `int` (or a `float` if the chapter is an extra) containing the number of the chapter or the current `.image`
- `.chapter_name` is a `string` containing the title of the chapter of the current `.image` (the `string` is empty if no name is detected) 
- `.domain` a `string` with the website domain, format is: `.domname.ext`
- `.ext` string with the image extension name
- `.image` is a `string` with link to the image  
- `.manga_name` is a `string` with the complete name of the manga or the webtoon of the current `.image`
- `.npage` is an `int` giving the current page of the fetcher
- `standalone` is a `bool` signaling if true that it doesn't support multiple chapters (the verbose and save paths/names wont have mentions of chapters) **/!\\ it's a class attribute /!\\**
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

### API usage
- `.create_pdf()` creates the pdf of the last chapter where `.full_chapter()` or `.keep_full_chapter()` was used
- `.full_download()` does the full download with the specified parameters when initialising
- `.full_chapter()` fetches the complete chapter
- `.go_to_chapter(chap)` goes to the chapter `chap`
- `.keep_full_chapter()` download the images of the chapter (like with the `-k` option)
- `.next_chapter()` goes to the next available chapter
- `.fetcher` where the corresponding fetcher is stored, usefull if conversing with it directly

## credits
- Roméo for the help with the rework of fanfox, especially for the reverse engineering of fanfox.net
