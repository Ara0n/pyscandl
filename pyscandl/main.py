from sys import stderr, modules
from platform import system
from os import path, makedirs, remove
import sqlite3
import json

from pyscandl.modules import arg_parser, Pyscandl
from pyscandl.modules.fetchers import FetcherEnum
from pyscandl.modules.autodl import Controller
from pyscandl.modules.excepts import DownedSite, MangaNotFound
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
		print("Warning: the current db will be replaced wy a new system in the next major release (3.0.0). Please do not forget the migration at that time", file=stderr)

		if args.list or args.list_all or args.list_only:
			ml = Controller().list_mangas(all=args.list_all, only=args.list_only)
			if ml:
				list = "\n- " + "\n- ".join(ml)
				print(f"current mangas in the autodl db are:{list}")
			else:
				print("there are currently no mangas in autodl, you may consider adding some to it with manga add")

		elif args.import_db:
			controller = Controller()
			controller.db_import(args.import_db)
			controller.save()

		elif args.export_db:
			Controller().db_export(args.export_db)

		elif args.manga_subparser == "scan":
			infos = Controller()
			if args.name:
				try:
					infos.scan(args.name)
				except MangaNotFound as e:
					print(e)
			else:
				mangas = [row[0] for row in infos._curs.execute("""SELECT name FROM manga WHERE archived=false ORDER BY name""").fetchall()]
				for manga in mangas:
					infos.scan(manga)

		elif args.manga_subparser == "info":
			infos = Controller().manga_info(args.name)
			if infos is None:
				print(f"manga '{args.name}' not in the list, you may consider adding it to it with manga add")
			elif infos[4]:
				print(f"{args.name}:\n",
					  f"\tmanga link: {infos[2]}\n",
					  f"\tfetcher: {infos[1]}\n",
					  f"\tnumber of chapters already downloaded: {len(infos[4])}\n",
					  f"\tlast chapter downloaded: {infos[4][0]}\n",
					  f"\tarchived: {bool(infos[3])}")
			else:
				print(f"{args.name}:\n",
					  f"\tmanga link: {infos[2]}\n",
					  f"\tfetcher: {infos[1]}\n",
					  f"\tno chapter downloaded yet\n",
					  f"\tarchived: {bool(infos[3])}")

		elif args.manga_subparser == "add":
			controller = Controller()
			if args.chap:
				chaps = [float(chap) if "." in chap else int(chap) for chap in args.chap]
			else:
				chaps = []
			controller.add(args.name, args.link, args.fetcher, chaps, args.archived)
			controller.save()

		elif args.manga_subparser == "edit":
			controller = Controller()
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

			controller.edit(args.name, args.link, args.fetcher, chaps, archive)
			controller.save()

		elif args.manga_subparser == "chaplist":
			info = Controller().manga_info(args.name)
			if info is not None:
				chaps = info[4]
				if chaps:
					if not args.quiet:
						print(f"the already downloaded chapters for '{args.name}' are:", end=" ")
					print(' '.join([str(chap) for chap in chaps]))
				else:
					print(f"no chapter downloaded yet for '{args.name}'")
			elif not args.quiet:
				print(f"manga '{args.name}' not in the list, you may consider adding it to it with manga add")

		elif args.manga_subparser == "rmchaps":
			controller = Controller()
			if controller.rm_chaps(args.name, args.chap):
				controller.save()
				if not args.quiet:
					print(f"deletion of the chapters {', '.join(args.chap)} from {args.name} sucessfull")
			else:
				if not args.quiet:
					print(f"no chapters removed for {args.name}")

		elif args.manga_subparser == "delete":
			controller = Controller()
			if controller.delete_manga(args.name):
				controller.save()
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
						old_db = json.load(data)
				except FileNotFoundError:
					old_db = {}

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
			for name in [row[0] for row in autodl._curs.execute("SELECT name FROM manga WHERE archived=false ORDER BY name").fetchall()]:
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
