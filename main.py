from modules import Pyscandl, arg_parser
from modules.fetchers import fetcher_enum
from modules.excepts import NoFetcherGiven
from modules.install import updater
from modules.autodl import commands

if __name__ == "__main__":
	args = arg_parser.parse_arg()

	if args.update:
		updater.update()

	elif args.manga_list:
		print(f"current mangas in the autodl db are: {', '.join(commands.Controller().list_mangas())}")

	elif args.subparser == "manual":
		if args.fetcher is None:
			raise NoFetcherGiven

		fetcher = fetcher_enum.Fetcher.get(args.fetcher)
		pyscandl = Pyscandl.Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, keepimage=args.keep_images, all=args.all, link=args.link, manga=args.manga, download_number=args.download_number, quiet=args.quiet, skip=args.start, tiny=args.tiny)
		pyscandl.full_download()

	elif args.subparser == "manga":
		json = commands.Controller()

		if args.add:
			json = commands.Controller()
			chaps = [float(chap) if "." in chap else int(chap) for chap in args.chapters]
			json.add(args.name, args.rss, args.link, args.fetcher, chaps)
			json.save()

		elif args.edit:
			json = commands.Controller()
			chaps = [float(chap) if "." in chap else int(chap) for chap in args.chapters]
			json.edit(args.name, args.rss, args.link, args.fetcher, chaps)
			json.save()

		elif args.info:
			infos = commands.Controller().manga_info(args.name)
			print(f"{infos.get('name')}:\n"
				  f"\trss link: {infos.get('rss')}\n"
				  f"\tmanga link: {infos.get('link')}\n"
				  f"\tfetcher: {infos.get('fetcher').upper()}"
				  f"\tnumber of chapters already downloaded: {len(infos.get('chapters'))}\n"
				  f"\tlast chapter downloaded: {infos.get('chapters')[0]}")

		elif args.chapter_list:
			chaps = commands.Controller().manga_info(args.name).get("chapters")
			print(f"the already downloaded chapters for {args.name} are: {', '.join([str(chap) for chap in chaps])}")

		elif args.delete:
			json = commands.Controller()
			if json.delete_manga(args.name):
				json.save()
				print(f"deletion of {args.name} successful")
			else:
				print(f"manga {args.name} not found")

	elif args.subparser == "autodl":
		autodl = commands.Controller(args.output, args.quiet, args.tiny)
		# to be sure to save progress done in case of interruption
		try:
			for name in autodl.db:
				autodl.scan(name)
				autodl.download(name)
		finally:
			autodl.save()
