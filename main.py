import arg_parser
import Pyscandl
from fetchers import fetcher_enum
from exceptions import NoFetcherGiven
from install import updater

if __name__ == "__main__":
	args = arg_parser.parse_arg()

	if args.update:
		updater.update()
		pass

	if args.fetcher is None:
		raise NoFetcherGiven

	fetcher = fetcher_enum.Fetcher.get(args.fetcher).value

	pyscandl = Pyscandl.Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, keepimage=args.keep_images, all=args.all, link=args.link, manga=args.manga, download_number=args.download_number, quiet=args.quiet, skip=args.start)

	pyscandl.full_download()
