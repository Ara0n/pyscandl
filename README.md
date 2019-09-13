# pyscandl
**DISCLAIMER:** This project is just a technical demo, don't download scans and get the mangas from official retailers when they are accessible in your country

This modular program to be able to download manga and webtoon scans from the internet, it'll use an image fetcher specific for each website while respecting an API.  
The API will enable you to create your own image fetchers for other websites not supported yet by the program.  

## command line interface
`pyscandl [--keep-images] <--fetcher|-f fname> <--link|-l link | --manga|-m mname> [--chapter-start|-c chapnumber] [--all|-a | --download-number|-n number] <--output|-o path>`

- `--output` or `-o` **required**: the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder `images` with inside one folder per chapter and the pdfs will be stored in a `pdf` subfolder 
- `--fetcher` or `-f` **required**: the name of the image links fetcher that will be used for the download
- `--link` or `-l` **required if not using `--manga` or `-m`**: gives the link to the page with all the chapter listed
- `--manga` or `-m` **required if not using `--link` or `-l`**: gives the manga name, the image fetcher will find the corresponding manga
- `--chapter-start` or `-c`: gives the chapter to start the download on (defaults at 1)
- `--download-number` or `-n`: gives the number of chapters to download (defaults at 1)
- `--all` or `-a`: downloads all the chapters from the starting point to the end
- `--keep-images`: the images used for the pdf will be kept in their corresponding folder

## image fetcher API
- `.image` is a string with link to the image  
- `.next_image()` changes `.image` to the next in the chapter  
- `.next_chapter()` changes `.image` to the first in the next chapter
- `.next()` changes to the next image of the chapter and to the first of the next chapter if you finnished the current chapter
- `is_last_image()` which returns `True` if it's the last page of the chapter
- `is_last_chapter()` which returns `True` if it's the last chapter available  
