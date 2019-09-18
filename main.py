import arg_parser
import Pyscandl
from fetchers import fetcher_enum

if __name__ == "__main__":
	args = arg_parser.parse_arg()
	fetcher = fetcher_enum.Fetcher.get(args.fetcher).value

	pyscandl = Pyscandl.Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, keepimage=args.keep_images, all=args.all, link=args.link, manga=args.manga, download_number=args.download_number, quiet=args.quiet, skip=args.start)

	pyscandl.full_download()
