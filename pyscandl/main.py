from sys import stderr, modules
from platform import system
from os import path, makedirs, remove
import sqlite3
import json as json_lib

from pyscandl.modules import arg_parser, Pyscandl
from pyscandl.modules.fetchers import FetcherEnum
from pyscandl.modules.autodl import Controller
from pyscandl.modules.excepts import DownedSite
from pyscandl import __version__
import xml.etree.ElementTree


def main():
	args = arg_parser.get_parser().parse_args()

	if args.version:
		print(f" The current version of pyscandl is {__version__}")

	elif args.subparser == "manual":
		fetcher = FetcherEnum.get(args.fetcher)
		pyscandl = Pyscandl(fetcher, chapstart=args.chapter_start, output=args.output, pdf=args.pdf,
									 keep=args.keep, image=args.image, all=args.all, link=args.link, manga=args.manga,
									 download_number=args.download_number, chapend=args.chapter_end, quiet=args.quiet,
									 skip=args.skip, tiny=args.tiny)
		pyscandl.full_download()

	elif args.subparser == "manga":
		print("Warning: the current db will be replaced wy a new system in the next major release (3.0.0). Please do not forget the migration at that time", file=stderr)

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

		elif args.manga_subparser == "migrate":
			if not args.quiet:
				print("WARNING: if there is already a database that was migrated before it will be erased in the process !")
			if args.quiet or input("Continue ? [y/N]").lower() == "y":
				if not args.quiet:
					print("Creating new db file...", end=" ")

				# as it's in the users folder now it's OS dependent
				platform = system()
				if platform == "Linux":
					folder_path = path.expanduser("~/.local/share/pyscandl/")
					# removing the old db if it exists
					try:
						remove(folder_path+"db.sqlite")
					except FileNotFoundError:
						pass

					# creating the new db
					makedirs(folder_path, exist_ok=True)
					conn = sqlite3.connect(folder_path + "db.sqlite")
				elif platform == "Windows":
					folder_path = path.expandvars("%APPDATA%/pyscandl/")
					# removing the old db if it exists
					try:
						remove(folder_path+"db.sqlite")
					except FileNotFoundError:
						pass

					# creating the new db
					makedirs(folder_path, exist_ok=True)
					conn = sqlite3.connect(folder_path + "db.sqlite")
				elif platform == "Darwin":
					folder_path = path.expanduser("~\Library\Preferences/pyscandl/")
					# removing the old db if it exists
					try:
						remove(folder_path+"db.sqlite")
					except FileNotFoundError:
						pass

					# creating the new db
					makedirs(folder_path, exist_ok=True)
					conn = sqlite3.connect(folder_path + "db.sqlite")
				else:
					raise OSError("The OS couldn't be detected, the db don't have a place to be stored")
				curs = conn.cursor()

				if not args.quiet:
					print("Loading the old db file...")
				try:
					with open(f"{path.dirname(modules['pyscandl.modules.autodl'].__file__)}/db.json", "r") as data:
						old_db = json_lib.load(data)
				except FileNotFoundError:
					old_db.db = {}

				if not args.quiet:
					print("Creating new tables...", end=" ")
				curs.execute("""
				CREATE TABLE IF NOT EXISTS "manga" (
					"id" INTEGER PRIMARY KEY,
					"name" TEXT UNIQUE,
					"fetcher" TEXT,
					"link" TEXT,
					"archived" BOOL DEFAULT FALSE
				);
				""")

				curs.execute("""
				CREATE TABLE IF NOT EXISTS "chaplist" (
					"manga" INTEGER REFERENCES manga(id),
					"chapter" BLOB
				);
				""")

				if not args.quiet:
					print("Transfering data...")
				for key, value in old_db.items():
					if not args.quiet:
						print(f"{key}: autodl data...", end=" ")
					curs.execute("""INSERT INTO manga("name", "fetcher", "link", "archived") VALUES (?, ?, ?, ?);""",
								 (
									 key,
									 value.get("fetcher").upper(),
									 value.get("link"),
									 value.get("archived")
								 ))
					if not args.quiet:
						print("already downloaded chapters...")
					curs.execute("""SELECT id FROM manga WHERE "name"=?""", (key,))
					manga_id = curs.fetchone()
					curs.executemany("""INSERT INTO chaplist("manga", "chapter") VALUES (?, ?);""", [(manga_id[0], chap) for chap in value.get("chapters")])

				conn.commit()
				conn.close()
			else:
				print("Cancelling migration")

	elif args.subparser == "autodl":
		print("Warning: the current db will be replaced wy a new system in the next major release (3.0.0). Please do not forget the migration at that time", file=stderr)

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
								print(f"problem with the fetching for {name}, retrying...")
							success = False
							tries_left -= 1
						except DownedSite:
							# the website can't be accessed for the time being so no retrying
							success = False
							tries_left = 0
					if success:
						try:
							autodl.download(name, pdf=args.pdf, keep=args.keep, image=args.image)
						except DownedSite:
							print(f"can't access {name}, please retry it later")
					elif not args.quiet:
						print(f"can't access {name}, please retry it later")
		except KeyboardInterrupt:
			if not args.quiet:
				print("\nmanual interruption")
		finally:
			autodl.save()
			if not args.quiet:
				print(f"{autodl.downloads} chapters downloaded")


if __name__ == "__main__":
	main()
