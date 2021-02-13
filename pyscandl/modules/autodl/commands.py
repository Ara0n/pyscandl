import os
from platform import system
import sqlite3
import shutil

import cfscrape
from ..excepts import IsStandalone, FetcherNotFound, EmptyChapter, DelayedRelease, MangaNotFound
from ..Pyscandl import Pyscandl
from ..fetchers import FetcherEnum
from ..fetchers.fetcher import StandaloneFetcher


class Controller:
	__doc__ = """
	Object responsible of the autodl part of the program, all the logic related to it passes here
	"""

	def __init__(self, output:str=".", quiet:bool=False, tiny:bool=False):
		"""
		Initializes this instance of the autodl controller.
		If there is no sqlite database for autodl currently in existence a new one is created at:

		- ``~/.local/share/pyscandl/`` for linux
		- ``%APPDATA%/pyscandl/` for windows
		- ``~/Library/Preferences/pyscandl/`` for mac

		:param output: location where the outputted scans should be stored
		:type output: str
		:param quiet: should the program not output any information about what it is doing in the console
		:type quiet: bool
		:param tiny: should the name of every downloaded scan be minified and only include the chapter number and the chapter title
		:type tiny: bool
		"""

		# as it's in the users folder now it's OS dependent
		platform = system()
		if platform == "Linux":
			folder_path = os.path.expanduser("~/.local/share/pyscandl/")
		elif platform == "Windows":
			folder_path = os.path.expandvars("%APPDATA%/pyscandl/")
		elif platform == "Darwin":
			folder_path = os.path.expanduser("~/Library/Preferences/pyscandl/")
		else:
			raise OSError("The OS couldn't be detected, the db don't have a place to be stored")

		try:
			self._conn = sqlite3.connect(folder_path + "db.sqlite")
			self._curs = self._conn.cursor()
		except sqlite3.OperationalError as e:
			if str(e) == "unable to open database file":
				os.makedirs(folder_path)
				self._conn = sqlite3.connect(folder_path + "db.sqlite")
				self._curs = self._conn.cursor()
		self.output = output
		self.quiet = quiet
		self.tiny = tiny
		self.scrapper = cfscrape.create_scraper()
		self.missing_chaps = []
		self.downloads = 0

	def save(self):
		"""
		Saves the current state of the database in the ``db.sqlite`` file and closes the connection.
		"""

		self._conn.commit()
		self._conn.close()

	def add(self, name:str, link:str, fetcher:str, chapters:list=None, archived=False):
		"""
		Adds a new scan entry to the ``db.sqlite`` file.

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

		self._curs.execute("""INSERT INTO manga("name", "fetcher", "link", "archived") VALUES (?, ?, ?, ?);""",
						   (
							   name,
							   fetcher.upper(),
							   link,
							   archived
						   ))
		self._curs.execute("""SELECT id FROM manga WHERE "name"=?""", (name,))
		manga_id = self._curs.fetchone()
		self._curs.executemany("""INSERT INTO chaplist("manga", "chapter") VALUES (?, ?);""", [(manga_id[0], chap) for chap in chapters])

	def edit(self, name:str, link:str=None, fetcher=None, chapters:list=None, archived=None):
		"""
		Edits an already existing entry in the ``db.sqlite`` file.
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
			self._curs.execute("""UPDATE manga SET link=? WHERE name=?;""", (link, name))
		if fetcher is not None:
			standalone_check = FetcherEnum.get(fetcher)
			if issubclass(standalone_check, StandaloneFetcher):
				raise IsStandalone(name)
			self._curs.execute("""UPDATE manga SET fetcher=? WHERE name=?;""", (fetcher, name))
		if chapters is not None:
			self._curs.execute("""INSERT INTO chaplist("manga", "chapter") VALUES ((SELECT id FROM manga WHERE name=?), ?);""", [(name, chap) for chap in chapters])
		if archived is not None:
			self._curs.execute("""UPDATE manga SET archived=? WHERE name=?;""", (archived, name))

	def scan(self, name:str):
		"""
		Scans the asked manga for new and non downloaded chapters and adds them to the controller queue.

		:param name: name of the manga
		:type name: str

		:raise MangaNotFound: the asked manga isn't in the db
		"""

		self.missing_chaps.clear()
		manga = self._curs.execute("""SELECT * FROM manga WHERE name=?""", (name,)).fetchone()
		if manga is None:
			raise MangaNotFound(name)

		manga_fetcher = FetcherEnum.get(manga[2])
		manga_chapters = set(manga_fetcher.scan(link=manga[3]))
		possessed_chaps = {row[0] for row in self._curs.execute(
			"""SELECT chapter FROM chaplist WHERE manga=(SELECT id FROM manga WHERE name=?)""", (name,)
		).fetchall()}
		self.missing_chaps = list(manga_chapters - possessed_chaps)

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

		manga = self._curs.execute("""SELECT * FROM manga WHERE name=?""", (name,)).fetchone()
		fetcher = FetcherEnum.get(manga[2])


		first = True
		chapter_id = 0
		while chapter_id < len(self.missing_chaps):
			try:
				if first:
					downloader = Pyscandl(fetcher, self.missing_chaps[chapter_id], self.output, link=manga[3], pdf=pdf, image=image, keep=keep, quiet=self.quiet, tiny=self.tiny)
					first = False
				else:
					downloader.go_to_chapter(self.missing_chaps[chapter_id])

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

				self._curs.execute("""
					INSERT INTO chaplist (manga, chapter) VALUES ((SELECT id FROM manga where name=?), ?)
				""", (name, self.missing_chaps[chapter_id]))
				self.downloads += 1
			except EmptyChapter:
				if not self.quiet:
					print(f"skipping {name} chapter {self.missing_chaps[chapter_id]}: empty, wont be added in the downloaded list")
			except DelayedRelease as e:
				if not self.quiet:
					print(e)
			finally:
				chapter_id += 1

		if self.missing_chaps:
			try:
				downloader.fetcher.quit()
			except UnboundLocalError:
				pass  # only available chapter was a delayed release or an empty chapter

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
		Gives the list of all the names of the mangas in the ``db.sqlite`` file. if the db is empty, returns None

		:param all: get also the archived mangas
		:type all: bool
		:param only: get only the archived mangas
		:type only: bool

		:rtype: list
		"""

		titles = []

		if all:
			manga = self._curs.execute("""SELECT * FROM manga ORDER BY name""").fetchall()
		elif only:
			manga = self._curs.execute("""SELECT * FROM manga WHERE archived=true ORDER BY name""").fetchall()
		else:
			manga = self._curs.execute("""SELECT * FROM manga WHERE archived=false ORDER BY name""").fetchall()

		max_len_title = len(max(manga, key=lambda x: len(x[1]))[1])
		fetchers = [row[2] for row in manga]
		max_len_fetcher = len(max(fetchers, key=lambda x: len(x)))
		for id, title, fetcher, link, archived in manga:
			if archived and (all or only):
				titles.append("{title:<{title_size}}|{fetcher:^{fetcher_size}}|{}".format(
					"    Archived",
					title=title,
					title_size=max_len_title + 4,
					fetcher=fetcher,
					fetcher_size=max_len_fetcher + 8
				))
			elif not archived and not only:
				titles.append("{title:<{title_size}}|{fetcher:^{fetcher_size}}|".format(
					title=title,
					title_size=max_len_title + 4,
					fetcher=fetcher,
					fetcher_size=max_len_fetcher + 8
				))
		return titles

	def manga_info(self, name):
		"""
		Fet the infos about a specific manga.

		:param name: name of the manga
		:type name: str

		:rtype: tuple
		:returns: name, fetcher, link, list[chapters]
		"""

		try:
			info = self._curs.execute("""SELECT * FROM manga WHERE name=?""", (name,)).fetchone()
			chaps = self._curs.execute("""SELECT chapter FROM chaplist WHERE manga=? ORDER BY chapter DESC""", (info[0],)).fetchall()
			return (*info[1:], [row[0] for row in chaps])
		except TypeError:
			return None

	def delete_manga(self, name):
		"""
		Deletes a manga from the ``db.sqlite`` file.

		:param name: name of the manga

		:return: confirms the deletion
		:rtype: bool
		"""
		if self._curs.execute("""SELECT * FROM manga where name=?;""", (name,)).fetchone():
			self._curs.execute("""DELETE from chaplist where manga=(SELECT id FROM manga where name=?);""", (name,))
			self._curs.execute("""DELETE FROM manga where name=?;""", (name,))
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

		vals = [(float(chap) if "." in chap else int(chap), name) for chap in rm_chaps[0]]
		return bool(self._curs.executemany("""DELETE FROM chaplist where chapter=? and manga=(SELECT id FROM manga WHERE name=?)""", vals).rowcount)

	def db_import(self, path:str):
		"""
		Takes an external sqlite file path and put its content as the new database for pyscandl.

		:param path: path to the .sqlite file to import as the database for autodl and manga
		:type path: str
		"""

		# as it's in the users folder now it's OS dependent
		platform = system()
		if platform == "Linux":
			folder_path = os.path.expanduser("~/.local/share/pyscandl/")
		elif platform == "Windows":
			folder_path = os.path.expandvars("%APPDATA%/pyscandl/")
		elif platform == "Darwin":
			folder_path = os.path.expanduser("~\Library\Preferences/pyscandl/")
		else:
			raise OSError("The OS couldn't be detected, the db don't have a place to be stored")

		shutil.copy(path, folder_path + "db.sqlite")

	def db_export(self, path:str):
		"""
		Saves a copy of the current database to the folder specified.

		:param path: path to the save folder location
		:type path: str
		"""

		# as it's in the users folder now it's OS dependent
		platform = system()
		if platform == "Linux":
			folder_path = os.path.expanduser("~/.local/share/pyscandl/")
		elif platform == "Windows":
			folder_path = os.path.expandvars("%APPDATA%/pyscandl/")
		elif platform == "Darwin":
			folder_path = os.path.expanduser("~\Library\Preferences/pyscandl/")
		else:
			raise OSError("The OS couldn't be detected, the db don't have a place to be stored")

		if not os.path.exists(path):
			os.makedirs(path)
		shutil.copy(folder_path + "db.sqlite", path)
