import parser
import Pyscandl
from fetchers import fetcher_enum

if __name__ == "__main__":
	args = parser.parse_arg()
	fetcher = fetcher_enum.Fetcher.get(args.fetcher).value

	pyscandl = Pyscandl.Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, keepimage=args.keep_images, all=args.all, link=args.link, manga=args.manga, download_number=args.download_number, quiet=args.quiet)

	pyscandl.full_download()
