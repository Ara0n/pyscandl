from pyscandl.modules import arg_parser, Pyscandl
from pyscandl.modules.fetchers import FetcherEnum
from pyscandl.modules.autodl import Controller
import xml.etree.ElementTree


def main():
	args = arg_parser.get_parser().parse_args()

	if args.subparser == "manual":
		fetcher = FetcherEnum.get(args.fetcher)
		pyscandl = Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, pdf=args.pdf,
									 keep=args.keep, image=args.image, all=args.all, link=args.link, manga=args.manga,
									 download_number=args.download_number, chapend=args.chapter_end, quiet=args.quiet,
									 skip=args.skip, tiny=args.tiny)
		pyscandl.full_download()

	elif args.subparser == "manga":

		if args.list or args.list_all or args.list_only:
			ml = Controller().list_mangas(all=args.list_all, only=args.list_only)
			if ml:
				list = "\n- " + "\n- ".join(ml)
				print(f"current mangas in the autodl db are:{list}")
			else:
				print("there are currently no mangas in autodl, you may consider adding some to it with manga add")

		elif args.import_db:
			json = Controller()
			json.db_import(args.import_db)
			json.save()

		elif args.export_db:
			Controller().db_export(args.export_db)

		elif args.manga_subparser == "info":
			infos = Controller().manga_info(args.name)
			if infos is None:
				print(f"manga '{args.name}' not in the list, you may consider adding it to it with manga add")
			elif infos.get("chapters"):
				print(f"{args.name}:\n",
					  f"\tmanga link: {infos.get('link')}\n",
					  f"\tfetcher: {infos.get('fetcher').upper()}\n",
					  f"\tnumber of chapters already downloaded: {len(infos.get('chapters'))}\n",
					  f"\tlast chapter downloaded: {infos.get('chapters')[0]}\n",
					  f"\tarchived: {infos.get('archived')}")
			else:
				print(f"{args.name}:\n",
					  f"\tmanga link: {infos.get('link')}\n",
					  f"\tfetcher: {infos.get('fetcher').upper()}\n",
					  f"\tno chapter downloaded yet\n",
					  f"\tarchived: {infos.get('archived')}")

		elif args.manga_subparser == "add":
			json = Controller()
			if args.chap:
				chaps = [float(chap) if "." in chap else int(chap) for chap in args.chap]
			else:
				chaps = []
			json.add(args.name, args.link, args.fetcher, chaps, args.archived)
			json.save()

		elif args.manga_subparser == "edit":
			json = Controller()
			if args.chap:
				chaps = [float(chap) if "." in chap else int(chap) for chap in args.chap]
			else:
				chaps = None

			if args.archive:
				archive = True
			elif args.unarchive:
				archive = False
			else:
				archive = None

			json.edit(args.name, args.link, args.fetcher, chaps, archive)
			json.save()

		elif args.manga_subparser == "chaplist":
			chaps = Controller().manga_info(args.name).get("chapters")
			print(f"the already downloaded chapters for {args.name} are: {' '.join([str(chap) for chap in chaps])}")

		elif args.manga_subparser == "rmchaps":
			json = Controller()
			if json.rm_chaps(args.name, args.chap):
				json.save()
				if not args.quiet:
					print(f"deletion of the chapters {', '.join(args.chap)} from {args.name} sucessfull")
			else:
				if not args.quiet:
					print(f"no chapters removed for {args.name}")

		elif args.manga_subparser == "delete":
			json = Controller()
			if json.delete_manga(args.name):
				json.save()
				if not args.quiet:
					print(f"deletion of {args.name} successful")
			else:
				if not args.quiet:
					print(f"manga {args.name} not found")

	elif args.subparser == "autodl":
		autodl = Controller(args.output, args.quiet, args.tiny)
		# to be sure to save progress done in case of interruption
		try:
			for name in autodl.db:
				# checking if the manga is archived
				if not autodl.db[name]["archived"]:
					# currently having problems with the xml tree fetching sometimes so giving a retry possibility to happen
					tries_left = 3
					while tries_left > 0:
						try:
							autodl.scan(name)
							success = True
							tries_left = 0
						except xml.etree.ElementTree.ParseError:
							if not args.quiet:
								print(f"problem with the xml fetching for {name}, retrying...")
							success = False
							tries_left -= 1
					if success:
						autodl.download(name, pdf=args.pdf, keep=args.keep, image=args.image)
					elif not args.quiet:
						print(f"can't access the xml for {name}, please retry it later")
		except KeyboardInterrupt:
			if not args.quiet:
				print("\nmanual interruption")
		finally:
			autodl.save()
			if not args.quiet:
				print(f"{autodl.downloads} chapters downloaded")


if __name__ == "__main__":
	main()
