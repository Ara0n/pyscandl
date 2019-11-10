import os, sys
import json
import requests
import cfscrape
import re
from xml.etree import ElementTree
from ..excepts import IsStandalone, FetcherNotFound, EmptyChapter
from ..Pyscandl import Pyscandl
from ..fetchers.fetcher_enum import Fetcher


class Controller:
	def __init__(self, output:str=".", quiet:bool=False, tiny:bool=False):
		try:
			with open(f"{os.path.dirname(sys.modules['modules.autodl'].__file__)}/db.json", "r") as data:
				self.db = json.load(data)
		except FileNotFoundError:
			self.db = {}
		self.output = output
		self.quiet = quiet
		self.tiny = tiny
		self._re_mgdex_scan = re.compile(r"(?:Chapter \d+, )?(Chapter \d+)")
		self.manga = {}
		self.missing_chaps = []

	def save(self):
		with open(f"{os.path.dirname(sys.modules['modules.autodl'].__file__)}/db.json", "w") as data:
			json.dump(self.db, data, indent=4)

	def add(self, name:str, rss:str, link:str, fetcher:str, chapters:list=[]):
		if fetcher.upper() not in [i.name for i in Fetcher]:
			raise FetcherNotFound(fetcher)
		if fetcher.lower() in ["nhentai"]:
			raise IsStandalone(name)
		self.db[name] = {
			"rss": rss,
			"link": link,
			"fetcher": fetcher.upper(),
			"chapters": sorted(chapters, reverse=True)
		}

	def edit(self, name:str, rss:str=None, link:str=None, fetcher=None, chapters:list=None):
		if rss is not None:
			self.db.get(name)["rss"] = rss
		if link is not None:
			self.db.get(name)["link"] = link
		if fetcher is not None:
			standalone_check = Fetcher.get(fetcher)
			if standalone_check.standalone:
				raise IsStandalone(name)
			self.db.get(name)["fetcher"] = fetcher
		if chapters is not None:
			self.db.get(name)["chapters"] = sorted(chapters, reverse=True)

	# each website/fetcher can have differently made xml from their rss so we need to treat them separately if need be
	def scan(self, name:str):
		self.missing_chaps.clear()
		manga = self.db.get(name)
		if manga.get("fetcher").lower() in ["fanfox", "fanfox_mono"]:
			xml = ElementTree.fromstring(requests.get(manga.get("rss")).content)
			for chapter in xml.iter("item"):
				nb = chapter.find("link").text.split("/")[-2][1:]
				if "." in nb:
					nb = float(nb)
				else:
					nb = int(nb)
				if nb not in manga.get("chapters"):
					self.missing_chaps.append(nb)
		elif manga.get("fetcher").lower() == "mangadex":
			xml = ElementTree.fromstring(cfscrape.create_scraper().get(manga.get("rss")).content)
			for chapter in xml.iter("item"):
				if chapter.find("description").text.split(" - ")[-1] == "Language: English":
					# check if it's a chapter
					if self._re_mgdex_scan.search(chapter.find("title").text):
						nb = chapter.find("title").text.split()[-1]
						if "." in nb:
							nb = float(nb)
						else:
							nb = int(nb)
						if nb not in manga.get("chapters"):
							self.missing_chaps.append(nb)
		self.missing_chaps.sort()
		if not self.quiet:
			if self.missing_chaps:
				print(f"new chapter(s) for {name}: {', '.join(map(str, self.missing_chaps))}")
			else:
				print(f"no new chapter for {name}")

	def download(self, name:str):
		manga = self.db.get(name)
		fetcher = Fetcher.get(manga.get("fetcher"))
		if self.missing_chaps:
			downloader = Pyscandl(fetcher, 1, self.output, link=manga.get("link"), quiet=self.quiet, tiny=self.tiny)
			for chapter in self.missing_chaps:
				try:
					downloader.go_to_chapter(chapter)
					downloader.full_chapter()
					downloader.create_pdf()
					self.db.get(name).get("chapters").append(chapter)
				except EmptyChapter:
					if not self.quiet:
						print(f"skipping {name} chapter {chapter}: empty, wont be added in the downloaded list")
			downloader.fetcher.quit()
			self.db.get(name).get("chapters").sort(reverse=True)

	def list_mangas(self):
		return self.db.keys()

	def manga_info(self, name):
		return self.db.get(name)

	def delete_manga(self, name):
		if name in self.db:
			del self.db[name]
			return True
		else:
			return False
