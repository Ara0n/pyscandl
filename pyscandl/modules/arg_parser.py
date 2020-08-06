import argparse
from .fetchers import FetcherEnum


def get_parser():
	"""
	Function used to parse the arguments in the command line interface

	:return: object containing the parse results
	"""

	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(dest="subparser")
	autodl = subparsers.add_parser("autodl", help="auto downloader using the mangas in the json")
	manga = subparsers.add_parser("manga", help="tool to modify, add and remove mangas from the automatic rss downloader mode list")
	manual_pars = subparsers.add_parser("manual", help="manually download scans, it will not update the downloaded scans json, if you plan on setting up a manga with the automatic rss mode don't mix both commands")

	parser.add_argument("-q", "--quiet", action="store_true", help="removes the verbose")


	# manual downloading subparser
	sauce = manual_pars.add_mutually_exclusive_group(required=True)
	sauce.add_argument("-l", "--link", type=str, help="gives the link to the page with all the chapter listed")
	sauce.add_argument("-m", "--manga", type=str, help="gives the manga name, the image fetcher will find the corresponding manga")

	manual_pars.add_argument("-f", "--fetcher", type=str, required=True, help="the name of the image links fetcher that will be used for the download")
	manual_pars.add_argument("-o", "--output", default=".", type=str, help="the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder images with inside one folder per chapter and the pdfs will be stored in a pdf subfolder")
	manual_pars.add_argument("-c", "--chapter-start", default=1, type=str, help="gives the chapter to start the download on (defaults at 1)")

	amount = manual_pars.add_mutually_exclusive_group()
	amount.add_argument("-a", "--all", action="store_true", help="downloads all the chapters from the starting point to the end")
	amount.add_argument("-n", "--download-number", default=1, type=int, help="gives the number of chapters to download (defaults at 1)")
	amount.add_argument("-e", "--chapter-end", default=0, type=int, help="gives the ending chapter number, if the chapter doesn't exists the program will stop once it's surpassed")

	manual_pars.add_argument("-t", "--tiny", action="store_true", help="don't write the manga name in the title (useful if using ebook libraries)")
	manual_pars.add_argument("-s", "--skip", default=0, type=int, help="skips n images before starting to download the first chapter")

	content = manual_pars.add_mutually_exclusive_group(required=True)
	content.add_argument("-p", "--pdf", action="store_true", help="downloads only the pdf of the manga")
	content.add_argument("-k", "--keep", action="store_true", help="downloads the pdf but also keep the images in a chapter subfolder")
	content.add_argument("-i", "--image", action="store_true", help="downloads only the images in a chapter subfolder and don't create the pdf")


	# json interaction subparser
	list_type = manga.add_mutually_exclusive_group()
	list_type.add_argument("-l", "--list", action="store_true", help="list all the non-archived mangas for autodl")
	list_type.add_argument("-la", "--list-all", action="store_true", help="list all the mangas for autodl")
	list_type.add_argument("-lo", "--list-only", action="store_true", help="list only the archived mangas for autodl")

	db_management = manga.add_mutually_exclusive_group()
	db_management.add_argument("-e", "--export-db", type=str, help="exports the current database into a json file")
	db_management.add_argument("-i", "--import-db", type=str, help="imports a new database from a json file")
	manga_subparser = manga.add_subparsers(dest="manga_subparser")

	## add subparser
	add = manga_subparser.add_parser("add", help="add a new manga to the auto downloader")
	add.add_argument("name", type=str, help="name for the stored manga")
	add.add_argument("-l", "--link", type=str, help="link of the manga", required=True)
	add.add_argument("-f", "--fetcher", type=str, help="name of the fetcher needed for the manga", required=True)
	add.add_argument("-c", "--chap", type=str, nargs="*", help="list of all the chapters already downloaded to be added to the list for the auto-updater")
	add.add_argument("-a", "--archived", action="store_true", help="create the manga as archived")

	## edit subparser
	edit = manga_subparser.add_parser("edit", help="modify infos for one of the already existing manga in the auto downloader")
	edit.add_argument("name", type=str, help="name for the stored manga")
	edit.add_argument("-l", "--link", type=str, help="link of the manga")
	edit.add_argument("-f", "--fetcher", type=str, help="name of the fetcher needed for the manga")
	edit.add_argument("-c", "--chap", type=str, nargs="*", help="list of all the chapters already downloaded to be added to the list for the auto-updater")

	archiving = edit.add_mutually_exclusive_group()
	archiving.add_argument("-a", "--archive", action="store_true", help="makes the edited manga archived")
	archiving.add_argument("-u", "--unarchive", action="store_true", help="unarchives the edited manga")


	## info subparser
	info = manga_subparser.add_parser("info", help="prints the info for the named manga in the auto updater")
	info.add_argument("name", type=str, help="name for the stored manga")

	## chapter list subparser
	chaplist = manga_subparser.add_parser("chaplist", help="lists all the dowloaded chapters (warning: can be huge)")
	chaplist.add_argument("name", type=str, help="name for the stored manga")

	## delete subparser
	delete = manga_subparser.add_parser("delete", help="deletes the corresponding manga from the auto downloader")
	delete.add_argument("name", type=str, help="name for the stored manga")

	## remove chapters subparser
	rmchaps = manga_subparser.add_parser("rmchaps", help="remove the listed chapters for this manga from the database")
	rmchaps.add_argument("name", type=str, help="name for the stored manga")
	rmchaps.add_argument("chap", type=str, nargs="*", help="remove the listed chapters for this manga from the database")


	# autodl subparser
	autodl.add_argument("-o", "--output", type=str, default=".", help="the path (absolute or relative) to the folder where to save the data")
	autodl.add_argument("-t", "--tiny", action="store_true", help="don't write the manga name in the title (useful if using ebook libraries)")
	content = autodl.add_mutually_exclusive_group(required=True)
	content.add_argument("-p", "--pdf", action="store_true", help="downloads only the pdf of the manga")
	content.add_argument("-k", "--keep", action="store_true", help="downloads the pdf but also keep the images in a chapter subfolder")
	content.add_argument("-i", "--image", action="store_true", help="downloads only the images in a chapter subfolder and don't create the pdf")


	manual_pars.epilog = "The current list of image fetcher is: " + ", ".join(FetcherEnum.list())
	manga.epilog = manual_pars.epilog

	return parser
