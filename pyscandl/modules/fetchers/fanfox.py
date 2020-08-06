from ..excepts import MangaNotFound, EmptyChapter
from .fetcher import Fetcher
import os, sys
import re
import pexpect
import requests
import secrets
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


class Fanfox(Fetcher):
	__doc__ = """
	This is the fetcher in charge of https://fanfox.net/ 
	"""

	def __init__(self, link:str=None, manga:str=None, chapstart=1):
		"""
		Initializes the instance of the nhentai fetcher, it needs either manga or link to work.

		:param link: link of the scan wanted
		:type link: str
		:param manga: manga name with all the non alpha numeric characters with "_", ex: fullmetal_alchemist
		:type manga: str
		:param chapstart: number of the chapter that the download is supposed to start
		:type chapstart: int/float/str

		:raises MangaNotFound: the scan asked for can't be found
		"""

		super().__init__(link, manga, chapstart)
		self._header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
						"Referer": "test"}

		self.domain = ".fanfox.net"
		self._node = pexpect.spawn(f"node {os.path.dirname(sys.modules['pyscandl.modules.fetchers'].__file__)}/eval.js")
		# creating the chapter link
		if link is not None:
			if link[-1] == "/":
				self._link = link
			else:
				self._link = link + "/"
			self.manga_name = self._link.split("/")[-2].replace("_", " ").title()
		else:
			self._link = f"https://fanfox.net/manga/{manga.replace(' ', '_').lower()}/"
			self.manga_name = manga.replace("_", " ").title().replace("/", "_")

		# regex used
		self._c_eval_args = re.compile(r"eval\(function\(p,a,c,k,e,d\).*?p;}\('(?P<arg1>.*?;)',(?P<arg2>\d+),(?P<arg3>\d+),'(?P<arg4>.*?)'.split")
		self._c_chap_name = re.compile(r"<p class=\"reader-header-title-2\">(?:Vol\.(?:\d+|TBD) )?Ch\.\d+(?:\.\d+)? ?(?P<chap_name>.*?)</p>")
		self._c_multi_max_page = re.compile(r"(?:data-page=\")(?P<page_num>\d+)")
		self._c_multi_cid = re.compile(r"(?:var chapterid =)(?P<cid>\d+)(?:;)")
		self._c_multi_page_list = re.compile(r"(?:var pix=\")(?P<link>.*?)\".*?\[(?P<chaps>\".*?\")\]")
		self._c_mono_page_list = re.compile(r"=\[(?P<chaps>'.*?')];")
		self._c_next_chap_num = re.compile(f"reader-main-next\" href=\"/manga/{self.manga_name.replace(' ', '_').lower()}" + r"/(?:v(?:TBD|\d+)/)?c(?P<next_chap>\d+(?:\.\d+)?)/1\.html\" title=.*?>Next Chapter</a>")

		req = requests.get(self._link)
		if req.url != self._link:
			raise MangaNotFound(self.manga_name)
		try:
			self.author = re.search(r"Author: <a href=.*? title=\"(.*?)\">", req.text).group(1)
		except AttributeError:
			self.author = "unknown"

		self.go_to_chapter(chapstart)

	def go_to_chapter(self, chap_num):
		"""
		Make the fetcher go to the asked chapter.

		:param chap_num: chapter number that was asked for
		:type chap_num: int/str/float

		:raises MangaNotFound: the asked chapter doesn't exist
		:raises EmptyChapter: the chapter exists but is void of images
		"""

		self._image_list = []
		self.npage = 1
		self.chapter_number = str(chap_num).split(".")[0].zfill(3)
		if "." in str(chap_num):
			self.chapter_number += "." + str(chap_num).split(".")[1]

		url = f"{self._link}c{self.chapter_number}/1.html"
		self._req = requests.get(url, cookies={"isAdult": "1"})
		if "<title>404</title>" in self._req.text:
			raise MangaNotFound(f"{self.manga_name}, chapter {self.chapter_number}")
		if '<p class="detail-block-content">No Images</p>' in self._req.text:
			raise EmptyChapter(self.manga_name, self.chapter_number)

		self._mono = self._req.text.count("dm5_key") == 1
		self.chapter_name = self._c_chap_name.search(self._req.text).group("chap_name").replace("/", "_")

		if self._mono:
			self._mono_go_to_chap()
		else:
			self._multi_go_to_chap()

		self.image = self._image_list[0]
		self.ext = self.image.split(".")[-1]

	def _mono_go_to_chap(self):
		"""
		Method used to get the obfuscated image info in mono type scan chapters.
		*mono type chapters are characterized by having all the images displayed one after another in a single page*
		"""

		out = self._decode(self._req.text)
		self._image_list = [f"https:{page.split('?')[0]}" for page in self._c_mono_page_list.search(out).group("chaps").replace("'", "").split(",")]
		self._last_page = len(self._image_list)

	def _multi_go_to_chap(self):
		"""
		Method used to get obfuscated image info in multi type scan chapters.
		*multi type chapters are characterized by having one image per page*
		"""

		cid = self._c_multi_cid.search(self._req.text).group("cid")
		self._last_page = max([int(i) for i in self._c_multi_max_page.findall(self._req.text)])

		for page in range(1, self._last_page+1):
			if page > len(self._image_list):
				req2 = requests.get(f"https://fanfox.net/chapterfun.ashx?cid={cid}&page={page}&key={secrets.token_hex(8)}", headers=self._header)
				out = self._decode(req2.text)
				root = self._c_multi_page_list.search(out).group("link")
				chaps = [i.split("?")[0] for i in self._c_multi_page_list.search(out).group("chaps").split('"') if i != "" and i != ","]

				for i in chaps:
					if i[0] != "/":
						i = "/" + i
					self._image_list.append(f"https:{root + i}")

	def _decode(self, obfuscated:str):
		"""
		Method used to de-obfuscate the web-pages of the scan to get the image info

		:param obfuscated: html code of the web-page of the scan
		:type obfuscated: str

		:return decoded: de-obfuscated image info that was contained in the page
		:rtype decoded: str
		"""

		args = list(self._c_eval_args.search(obfuscated).groups())
		args[0] = args[0].replace("\\", "")
		args = args[0] + "£" + args[1] + "£" + args[2] + "£" + args[3]
		self._node.sendline(args)

		decoded = b""
		self._node.readline()
		temp = self._node.readline()
		while temp != b"EOF\r\n":
			decoded += temp
			temp = self._node.readline()
		decoded = decoded.replace(b"\r\n", b"").decode()

		return decoded

	def next_image(self):
		"""
		Goes to the next image in the scan being fetched.
		"""

		self.image = self._image_list[self.npage]
		self.npage += 1
		self.ext = self.image.split(".")[-1]

	def is_last_image(self):
		"""
		Checks if it's the last image in the current chapter.
		:rtype: bool
		"""

		# automatically ignoring the last page of add
		return self.npage == len(self._image_list)-1

	def next_chapter(self):
		"""
		Goes to the next chapter
		"""

		next = self._c_next_chap_num.search(self._req.text).group("next_chap")
		self.go_to_chapter(next)

	def is_last_chapter(self):
		"""
		Checks if the current chapter is the last available one

		:rtype: bool
		"""

		return not bool(self._c_next_chap_num.search(self._req.text))

	@classmethod
	def scan(cls, link:str=None, manga:str=None):
		if link is not None:
			manga_id = link.split("manga/")[1].split("/")[0]
		elif manga is not None:
			manga_id = manga.replace(" ", "_")

		rss_url = f"https://fanfox.net/rss/{manga_id}.xml"

		try:
			xml_root = ET.fromstring(requests.get(rss_url).text)
		except ParseError:
			raise MangaNotFound(manga_id)

		chap_list = []

		for item in xml_root.iter("item"):
			chap_nb = item.find("link").text.split("/")[-2][1:]
			if "." in chap_nb:
				chap_nb = float(chap_nb)
			else:
				chap_nb = int(chap_nb)

			chap_list.append(chap_nb)

		return list(set(chap_list))


	def quit(self):
		"""
		Method used to close everything that was used after finishing to use the fetcher
		"""

		self._node.terminate(force=True)
