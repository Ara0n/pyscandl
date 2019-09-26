import argparse
from fetchers import fetcher_enum


def parse_arg():
	parser = argparse.ArgumentParser()

	sauce = parser.add_mutually_exclusive_group(required=True)
	sauce.add_argument("-l", "--link", type=str, help="gives the link to the page with all the chapter listed")
	sauce.add_argument("-m", "--manga", type=str, help="gives the manga name, the image fetcher will find the corresponding manga")

	amount = parser.add_mutually_exclusive_group()
	amount.add_argument("-a", "--all", action="store_true", help="downloads all the chapters from the starting point to the end")
	amount.add_argument("-n", "--download-number", default=1, type=int, help="gives the number of chapters to download (defaults at 1)")

	parser.add_argument("-f", "--fetcher", type=str, required=True, help="the name of the image links fetcher that will be used for the download")
	parser.add_argument("-o", "--output", default=".", type=str, help="the path (absolute or relative) to the folder where to save the data, the images will be stored in a subfolder images with inside one folder per chapter and the pdfs will be stored in a pdf subfolder")
	parser.add_argument("-c", "--chapter-start", default=1, type=str, help="gives the chapter to start the download on (defaults at 1)")
	parser.add_argument("-k", "--keep-images", action="store_true", help="the images used for the pdf will be kept in their corresponding folder")
	parser.add_argument("-q", "--quiet", action="store_true", help="removes the verbose of the downloads")
	parser.add_argument("-s", "--start", default=0, type=int, help="skips n images before starting to download the first chapter")

	parser.epilog = "The current list of image fetcher is: " + ", ".join(fetcher_enum.Fetcher.list())

	return parser.parse_args()
