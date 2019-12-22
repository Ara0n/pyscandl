from .. import excepts
import os, sys
import re
import pexpect
import requests
import secrets

class Fanfox:
	def __init__(self, link:str=None, manga:str=None, chapstart:int=1):
		self._header = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
						"Referer": "test"}
		self.standalone = False
		self.domain = ".fanfox.net"
		self._node = pexpect.spawn(f"node {os.path.dirname(sys.modules['modules.fetchers'].__file__)}/eval.js")
		# creating the chapter link
		if link is not None:
			if link[-1] == "/":
				self._link = link
			else:
				self._link = link + "/"
			self.manga_name = self._link.split("/")[-2].replace("_", " ").title()
		else:
			self._link = f"https://fanfox.net/manga/{manga.replace(' ', '_').lower()}/"
			self.manga_name = manga.replace("_", " ").title()

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
			raise excepts.MangaNotFound(self.manga_name)
		self.author = re.search(r"Author: <a href=.*? title=\"(.*?)\">", req.text).group(1)

		self.go_to_chapter(chapstart)

	def go_to_chapter(self, chap_num):
		self._image_list = []
		self.npage = 1
		self.chapter_number = str(chap_num).split(".")[0].zfill(3)
		if "." in str(chap_num):
			self.chapter_number += "." + str(chap_num).split(".")[1]

		url = f"{self._link}c{self.chapter_number}/1.html"
		self._req = requests.get(url, cookies={"isAdult": "1"})
		if "<title>404</title>" in self._req.text:
			raise excepts.MangaNotFound(f"{self.manga_name}, chapter {self.chapter_number}")
		if '<p class="detail-block-content">No Images</p>' in self._req.text:
			raise excepts.EmptyChapter(self.manga_name, self.chapter_number)

		self._mono = self._req.text.count("dm5_key") == 1
		self.chapter_name = self._c_chap_name.search(self._req.text).group("chap_name")

		if self._mono:
			self._mono_go_to_chap()
		else:
			self._multi_go_to_chap()

		self.image = self._image_list[0]
		self.ext = self.image.split(".")[-1]

	def _mono_go_to_chap(self):
		out = self._decode(self._req.text)
		self._image_list = [f"https:{page.split('?')[0]}" for page in self._c_mono_page_list.search(out).group("chaps").replace("'", "").split(",")]
		self._last_page = len(self._image_list)

	def _multi_go_to_chap(self):
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

	def _decode(self, ofuscated:str):
		args = list(self._c_eval_args.search(ofuscated).groups())
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
		self.image = self._image_list[self.npage]
		self.npage += 1
		self.ext = self.image.split(".")[-1]

	def is_last_image(self):
		return self.npage == len(self._image_list)-1

	def next_chapter(self):
		next = self._c_next_chap_num.search(self._req.text).group("next_chap")
		self.go_to_chapter(next)

	def is_last_chapter(self):
		return not bool(self._c_next_chap_num.search(self._req.text))

	def quit(self):
		self._node.terminate(force=True)
