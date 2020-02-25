from modules import Pyscandl, arg_parser
from modules.fetchers import fetcher_enum
from modules.install import updater
from modules.autodl import commands

if __name__ == "__main__":
	args = arg_parser.parse_arg()

	if args.update:
		updater.update()

	elif args.manga_list:
		list ="\n- ".join(commands.Controller().list_mangas())
		print(f"current mangas in the autodl db are:{list}")

	elif args.subparser == "manual":
		fetcher = fetcher_enum.Fetcher.get(args.fetcher)
		pyscandl = Pyscandl.Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, pdf=args.pdf, keep=args.keep, image=args.image, all=args.all, link=args.link, manga=args.manga, download_number=args.download_number, quiet=args.quiet, skip=args.skip, tiny=args.tiny)
		pyscandl.full_download()

	elif args.subparser == "manga":
		json = commands.Controller()

		if args.manga_subparser == "info":
			infos = commands.Controller().manga_info(args.name)
			if infos is None:
				print(f"manga '{args.name}' not in the list, you may consider adding it to it with manga add")
			elif infos.get("chapters"):
				print(f"{args.name}:\n",
					  f"\trss link: {infos.get('rss')}\n"
					  f"\tmanga link: {infos.get('link')}\n"
					  f"\tfetcher: {infos.get('fetcher').upper()}"
					  f"\tnumber of chapters already downloaded: {len(infos.get('chapters'))}\n"
					  f"\tlast chapter downloaded: {infos.get('chapters')[0]}")
			else:
				print(f"{args.name}:\n",
					  f"\trss link: {infos.get('rss')}\n"
					  f"\tmanga link: {infos.get('link')}\n"
					  f"\tfetcher: {infos.get('fetcher').upper()}"
					  f"\tnumber of chapters already downloaded: {len(infos.get('chapters'))}\n"
					  f"\tno chapter downloaded yet")

		elif args.manga_subparser == "add":
			json = commands.Controller()
			if args.chap:
				chaps = [float(chap) if "." in chap else int(chap) for chap in args.chap]
			else:
				chaps = []
			json.add(args.name, args.rss, args.link, args.fetcher, chaps)
			json.save()

		elif args.manga_subparser == "edit":
			json = commands.Controller()
			if args.chap:
				chaps = [float(chap) if "." in chap else int(chap) for chap in args.chap]
			else:
				chaps = None
			json.edit(args.name, args.rss, args.link, args.fetcher, chaps)
			json.save()

		elif args.manga_subparser == "chaplist":
			chaps = commands.Controller().manga_info(args.name).get("chapters")
			print(f"the already downloaded chapters for {args.name} are: {' '.join([str(chap) for chap in chaps])}")

		elif args.manga_subparser == "rmchaps":
			json = commands.Controller()
			if json.rm_chaps(args.name, args.chap):
				json.save()
				if not args.quiet:
					print(f"deletion of the chapters {', '.join(args.chap)} from {args.name} sucessfull")
			else:
				if not args.quiet:
					print(f"no chapters removed for {args.name}")

		elif args.manga_subparser == "delete":
			json = commands.Controller()
			if json.delete_manga(args.name):
				json.save()
				if not args.quiet:
					print(f"deletion of {args.name} successful")
			else:
				if not args.quiet:
					print(f"manga {args.name} not found")


	elif args.subparser == "autodl":
		autodl = commands.Controller(args.output, args.quiet, args.tiny)
		# to be sure to save progress done in case of interruption
		try:
			for name in autodl.db:
				autodl.scan(name)
				autodl.download(name, pdf=args.pdf, keep=args.keep, image=args.image)
		finally:
			autodl.save()
			if not args.quiet:
				print(f"{autodl.downloads} chapters downloaded")
