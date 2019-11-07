import argparse
from fetchers.fetcher_enum import Fetcher


def parse_arg():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	manual_pars = subparsers.add_parser("manual", help="manually download scans, it will not update the downloaded scans json, if you plan on setting up a manga with the automatic rss mode don't mix both commands")
	json = subparsers.add_parser("json", help="tool to modify, add and remove mangas from the automatic rss downloader mode list")

	options = parser.add_mutually_exclusive_group()
	options.add_argument("-U", "--update", action="store_true", help="updates the program")
	options.add_argument("-l", "--list", action="store_true", help="list all the current mangas in the auto downloader")
	options.add_argument("-m", "--manga", type=str, help="prints the info for the named manga in the auto updater")
	options.add_argument("-d", "--delete", type=str, help="deletes the corresponding manga from the auto downloader")

	# manual downloading parser
	sauce = manual_pars.add_mutually_exclusive_group()
	sauce.add_argument("-l", "--link", type=str, help="gives the link to the page with all the chapter listed")
	sauce.add_argument("-m", "--manga", type=str, help="gives the manga name, the image fetcher will find the corresponding manga")

	amount = manual_pars.add_mutually_exclusive_group()
	amount.add_argument("-a", "--all", action="store_true", help="downloads all the chapters from the starting point to the end")
	amount.add_argument("-n", "--download-number", default=1, type=int, help="gives the number of chapters to download (defaults at 1)")

	manual_pars.add_argument("-f", "--fetcher", type=str, help="the name of the image links fetcher that will be used for the download")
	manual_pars.add_argument("-o", "--output", default=".", type=str, help="the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder images with inside one folder per chapter and the pdfs will be stored in a pdf subfolder")
	manual_pars.add_argument("-c", "--chapter-start", default=1, type=str, help="gives the chapter to start the download on (defaults at 1)")
	manual_pars.add_argument("-k", "--keep-images", action="store_true", help="the images used for the pdf will be kept in their corresponding folder")
	manual_pars.add_argument("-q", "--quiet", action="store_true", help="removes the verbose of the downloads")
	manual_pars.add_argument("-s", "--start", default=0, type=int, help="skips n images before starting to download the first chapter")
	manual_pars.add_argument("-t", "--tiny", action="store_true", help="don't write the manga name in the title (useful if using ebook libraries)")


	# json modification parser
	json.add_argument("name", type=str, help="name for the stored manga")
	edit_mode = json.add_mutually_exclusive_group()
	edit_mode.add_argument("-a", "--add", action="store_true", help="add a new manga to the auto downloader")
	edit_mode.add_argument("-e", "--edit", action="store_true", help="modify infos for one of the already existing manga in the auo downloader")

	json.add_argument("-r", "--rss", type=str, help="rss link with the update notification of the manga")
	json.add_argument("-l", "--link", type=str, help="link of the manga")
	json.add_argument("-f", "--fetcher", type=str, help="name of the fetcher needed for the manga")
	json.add_argument("-c", "--chapters", nargs="*", help="list of all the chapters already downloaded to be added to the list for the autoupdater")

	parser.epilog = "The current list of image fetcher is: " + ", ".join(Fetcher.list())
	manual_pars.epilog = parser.epilog
	json.epilog = parser.epilog

	return parser.parse_args()
