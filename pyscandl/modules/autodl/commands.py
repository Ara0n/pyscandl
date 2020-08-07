import os, sys
import json
import requests
import cfscrape
import re
from xml.etree import ElementTree
from ..excepts import IsStandalone, FetcherNotFound, EmptyChapter, DelayedRelease
from ..Pyscandl import Pyscandl
from ..fetchers import FetcherEnum


class Controller:
	__doc__ = """
	Object responsible of the autodl part of the program, all the logic related to it passes here
	"""

	def __init__(self, output:str=".", quiet:bool=False, tiny:bool=False):
		"""
		Initializes this instance of the autodl controller.
		If there is no json database for autodl currently in existence a new one is created at ``pyscandl/modules/autodl/db.json``.

		:param output: location where the outputted scans should be stored
		:type output: str
		:param quiet: should the program not output any information about what it is doing in the console
		:type quiet: bool
		:param tiny: should the name of every downloaded scan be minified and only include the chapter number and the chapter title
		:type tiny: bool
		"""

		try:
			with open(f"{os.path.dirname(sys.modules['pyscandl.modules.autodl'].__file__)}/db.json", "r") as data:
				self.db = json.load(data)
		except FileNotFoundError:
			self.db = {}
		self.output = output
		self.quiet = quiet
		self.tiny = tiny
		self._re_mgdex_scan = re.compile(r"(?:Chapter \d+, )?Chapter (?P<chap>\d+(\.\d+)?)")
		self.scrapper = cfscrape.create_scraper()
		self.missing_chaps = []
		self.downloads = 0

	def save(self):
		"""
		Saves the current state of the database in the ``db.json`` file.
		"""

		with open(f"{os.path.dirname(sys.modules['pyscandl.modules.autodl'].__file__)}/db.json", "w") as data:
			json.dump(self.db, data, indent=4, sort_keys=True)

	def add(self, name:str, link:str, fetcher:str, chapters:list=None, archived=False):
		"""
		Adds a new scan entry to the ``db.json`` file.

		:param name: name of the manga
		:type name: str
		:param link: link to the page of the manga *(same link that is used for the -l arg in other uses of pyscandl)*
		:type link: str
		:param fetcher: name of the associated fetcher
		:type fetcher: str
		:param chapters: list of the already possessed chapters that wont be downloaded again *(Optional)*
		:type chapters: list[int/float/str]
		:param archived: tell if the chapter is considered archived and if it'll be downloaded with autodl
		:type archived: bool

		:raises FetcherNotFound: the specified fetcher doesn't exist
		:raises IsStandalone: the specified fetcher is a standalone fetcher
		"""

		if chapters is None:
			chapters = []

		if fetcher.upper() not in [i.name for i in FetcherEnum]:
			raise FetcherNotFound(fetcher)
		if fetcher.lower() in ["nhentai"]:
			raise IsStandalone(name)
		self.db[name] = {
			"link": link,
			"fetcher": fetcher.upper(),
			"chapters": sorted(chapters, reverse=True),
			"archived": archived
		}

	def edit(self, name:str, link:str=None, fetcher=None, chapters:list=None, archived=None):
		"""
		Edits an already existing entry in the ``db.json`` file.
		The :param name: is mandatory to find the correct entry and every other parameter specified will overwrite the existing values.

		:param name: name of the manga
		:type name: str
		:param link: link to the page of the manga *(same link that is used for the -l arg in other uses of pyscandl)*
		:type link: str
		:param fetcher: name of the associated fetcher
		:type fetcher: str
		:param chapters: list of the already possessed chapters that wont be downloaded again
		:type chapters: list[int/float/str]
		:param archived: tell if the chapter is considered archived and if it'll be downloaded with autodl
		:type archived: bool

		:raises IsStandalone: the specified fetcher is a standalone fetcher
		"""

		if link is not None:
			self.db.get(name)["link"] = link
		if fetcher is not None:
			standalone_check = FetcherEnum.get(fetcher)
			if standalone_check.standalone:
				raise IsStandalone(name)
			self.db.get(name)["fetcher"] = fetcher
		if chapters is not None:
			self.db.get(name)["chapters"] = sorted(self.db.get(name)["chapters"] + chapters, reverse=True)
		if archived is not None:
			try:
				self.db.get(name)["archived"] = archived
			except TypeError:
				print(f"\"{name}\" isn't a manga in the database, you may consider adding it with manga add")

	# each website/fetcher can have differently made xml from their rss so we need to treat them separately if need be
	def scan(self, name:str):
		"""
		Scans the asked manga for new and non downloaded chapters and adds them to the controller queue.

		:param name: name of the manga
		:type name: str
		"""

		self.missing_chaps.clear()
		manga = self.db.get(name)

		manga_fetcher = FetcherEnum.get(manga.get("fetcher"))
		manga_chapters = manga_fetcher.scan(link=manga.get("link"))

		self.missing_chaps = list(set(manga_chapters) - set(manga.get("chapters")))

		self.missing_chaps.sort()
		if not self.quiet:
			if self.missing_chaps:
				print(f"new chapter(s) for {name}: {', '.join(map(str, self.missing_chaps))}")
			else:
				print(f"no new chapter for {name}")

	def download(self, name:str, pdf:bool=True, keep:bool=False, image:bool=False):
		"""
		Start the download of the chapters of the asked manga that have their number in the scan results.

		:param name: name of the manga
		:type name: str
		:param pdf: tell if the result should be kept as a pdf
		:type pdf: bool
		:param keep: tell if the result should be kept as a pdf and as a collection of images
		:type keep: bool
		:param image: tell if the result should be kept as a collection of images
		:type image: bool
		"""

		manga = self.db.get(name)
		fetcher = FetcherEnum.get(manga.get("fetcher"))

		# initialize to the first downloadable chapter and download it
		ok = False
		for chapter_id in range(len(self.missing_chaps)):
			try:
				downloader = Pyscandl(fetcher, self.missing_chaps[chapter_id], self.output, link=manga.get("link"), quiet=self.quiet, tiny=self.tiny)

				bad_image = True
				while bad_image:  # protect against bad downloads
					try:
						if keep or image:
							downloader.keep_full_chapter()
						elif pdf:
							downloader.full_chapter()
						if not image:
							downloader.create_pdf()
						bad_image = False
					except IOError:
						print(f"problem during download, retrying {name} chapter {self.missing_chaps[chapter_id]}")
						downloader.go_to_chapter(self.missing_chaps[chapter_id])

				self.db.get(name).get("chapters").append(self.missing_chaps[chapter_id])
				self.downloads += 1

				self.missing_chaps = self.missing_chaps[chapter_id+1:]
				ok = True
				break
			except EmptyChapter:
				if not self.quiet:
					print(f"skipping {name} chapter {self.missing_chaps[chapter_id]}: empty, wont be added in the downloaded list")
			except DelayedRelease as e:
				if not self.quiet:
					print(e)

		# if chapters are left to doawnload proceeds with it
		if ok:
			for chapter_id in range(len(self.missing_chaps)):
				try:
					bad_image = True
					while bad_image:  # protect against bad downloads
						try:
							downloader.go_to_chapter(self.missing_chaps[chapter_id])

							if keep or image:
								downloader.keep_full_chapter()
							else:
								downloader.full_chapter()
							if not image:
								downloader.create_pdf()
							bad_image = False
						except IOError:
							print(f"problem during download, retrying {name} chapter {self.missing_chaps[chapter_id]}")

					self.db.get(name).get("chapters").append(self.missing_chaps[chapter_id])
					self.downloads += 1
				except EmptyChapter:
					if not self.quiet:
						print(f"skipping {name} chapter {self.missing_chaps[chapter_id]}: empty, wont be added in the downloaded list")
				except DelayedRelease as e:
					if not self.quiet:
						print(e)

			downloader.fetcher.quit()
			self.db.get(name).get("chapters").sort(reverse=True)

		# remove the directory if there is no chapter
		try:
			folders = list(os.walk(self.output))[1:]
			for folder in folders:
				if not folder[2]:
					os.rmdir(folder[0])
		except OSError:
			pass

	def list_mangas(self, all=False, only=False):
		"""
		Gives the list of all the names of the mangas in the ``db.json`` file. if the db is empty, returns None

		:param all: get also the archived mangas
		:type all: bool
		:param only: get only the archived mangas
		:type only: bool

		:rtype: list
		"""

		titles = []

		if not self.db:
			return None

		max_len = len(max(self.db.keys(), key=lambda x: len(x)))
		for title in self.db.keys():
			if self.db[title]["archived"] and (all or only):
				titles.append("{title:<{size}}|{}".format("    Archived", title=title, size=max_len + 4))
			elif not self.db[title]["archived"] and not only:
				titles.append("{title:<{size}}|".format(title=title, size=max_len + 4))
		return titles

	def manga_info(self, name):
		"""
		Fet the infos about a specific manga.

		:param name: name of the manga
		:type name: str

		:rtype: dict
		"""

		return self.db.get(name)

	def delete_manga(self, name):
		"""
		Deletes a manga from the ``db.json`` file.

		:param name: name of the manga

		:return: confirms the deletion
		:rtype: bool
		"""
		if name in self.db:
			del self.db[name]
			return True
		else:
			return False

	def rm_chaps(self, name, *rm_chaps):
		"""
		Remove the listed chapters from the asked manga

		:param name: name of he manga
		:type name: str
		:param rm_chaps: list of all the chapters that have to be removed
		:type rm_chaps: str

		:return: confirms the deletion
		:rtype: bool
		"""
		if name in self.db:
			self.db.get(name)["chapters"] = [chap for chap in self.db.get(name)["chapters"] if not chap not in rm_chaps]
			return True
		else:
			return False

	def db_import(self, path:str):
		"""
		Takes an external json file path and put its content as the new database for pyscandl.

		:param path: path to the .json file to import as the database for autodl and manga
		:type path: str
		"""

		with open(path, "r") as data:
			self.db = json.load(data)

	def db_export(self, path:str):
		"""
		Saves a copy of the current database to the file path specified.

		:param path: path to the save location, may be either a file or a folder, if it is a folder the filename will be db.json
		:type path: str

		:raises TypeError: if you specify the file name in the destination, the file extension must be .json
		"""

		if os.path.splitext(path)[1]:  # check if the path includes the filename
			if os.path.splitext(path)[1] != ".json":
				raise TypeError("the file must be a .json file !")

			path, filename = os.path.split(path)

		else:
			filename = "db.json"

		if not os.path.exists(path):
			os.makedirs(path)

		with open(os.path.join(path, filename), "w") as data:
			json.dump(self.db, data, indent=4, sort_keys=True)
