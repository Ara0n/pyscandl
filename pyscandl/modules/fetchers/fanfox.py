import re
import secrets
import requests
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from bs4 import BeautifulSoup

from ..excepts import MangaNotFound, EmptyChapter, DownedSite
from .fetcher import Fetcher


class Fanfox(Fetcher):
    __doc__ = """
    This is the fetcher in charge of https://fanfox.net/ 
    """

    def __init__(self, link:str=None, manga:str=None, chapstart=1):
        """
        Initializes the instance of the fanfox fetcher, it needs either manga or link to work.

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

        req = requests.get(self._link)
        soup = BeautifulSoup(req.text, "html.parser")
        if req.url != self._link:
            raise MangaNotFound(self.manga_name)
        try:
            self.author = soup.find("p", class_="detail-info-right-say").findChild("a").text
        except AttributeError:
            self.author = "unknown"

        # regex i can't get rid of... :/
        self._c_eval_args = re.compile(r"eval\(function\(p,a,c,k,e,d\).+?p;}\('(?P<pattern>.+?)',(?P<counter1>\d+?),(?P<counter2>\d+?),'(?P<str_table>.+?)'\.split")
        self._c_decode_word_replacer = re.compile(r"\b\w+\b")

        self.go_to_chapter(chapstart)

    def _decode(self, obfuscated:str):
        """
        Method used to de-obfuscate the web-pages of the scan to get the image info

        :param obfuscated: html code of the web-page of the scan
        :type obfuscated: str

        :return decoded: de-obfuscated image info that was contained in the page
        :rtype decoded: str
        """

        match = self._c_eval_args.search(obfuscated)
        pattern = match.group("pattern").replace("\\", "")
        counter1 = int(match.group("counter1"))
        counter2 = int(match.group("counter2"))
        str_table = match.group("str_table").split("|")
        pattern_dict = {}

        def calc_dict_indices(iter_number):
            if iter_number < counter1:
                prefix = ""
            else:
                prefix = calc_dict_indices(int(iter_number / counter1))

            remainder = iter_number % counter1

            if remainder > 35:
                return prefix + chr(remainder + 29)
            else:
                return prefix + "0123456789abcdefghijklmnopqrstuvwxyz"[remainder]

        for i in range(counter2 - 1, -1, -1):
            dict_index = calc_dict_indices(i)
            pattern_dict[dict_index] = str_table[i] if str_table[i] else dict_index

        return self._c_decode_word_replacer.sub(repl=lambda word: pattern_dict[word.group()], string=pattern)

    def go_to_chapter(self, chap):
        """
        Go to the specified chapter.

        :param chap: number of the specified chapter

        :raises MangaNotFound: the asked chapter doesn't exist
        :raises EmptyChapter: the chapter exists but is void of images
        """

        self._image_list = []
        self.npage = 1
        self.chapter_number = str(chap).split(".")[0].zfill(3)
        if "." in str(chap):
            self.chapter_number += "." + str(chap).split(".")[1]

        url = f"{self._link}c{self.chapter_number}/1.html"
        self._req = requests.get(url, cookies={"isAdult": "1"})
        if "<title>404</title>" in self._req.text:
            raise MangaNotFound(f"{self.manga_name}, chapter {self.chapter_number}")
        if '<p class="detail-block-content">No Images</p>' in self._req.text:
            raise EmptyChapter(self.manga_name, self.chapter_number)
        self._soup = BeautifulSoup(self._req.text, "html.parser")

        self._mono = self._req.text.count("dm5_key") == 1
        self.chapter_name = " ".join(self._soup.find("p", class_="reader-header-title-2").text.split("Ch.")[-1].split(" ")[1:])

        if self._mono:
            self._mono_go_to_chap()
        else:
            self._multi_go_to_chap()

        self.image = self._image_list[0]

        if requests.get(self.image).status_code == 404:  # if a chapter has TBE as a volume it doesn't work without stating vTBE to redo but with it
            self._image_list = []
            self.npage = 1
            self.chapter_number = str(chap).split(".")[0].zfill(3)
            if "." in str(chap):
                self.chapter_number += "." + str(chap).split(".")[1]

            url = f"{self._link}vTBE/c{self.chapter_number}/1.html"
            self._req = requests.get(url, cookies={"isAdult": "1"})
            if "<title>404</title>" in self._req.text:
                raise MangaNotFound(f"{self.manga_name}, chapter {self.chapter_number}")
            if '<p class="detail-block-content">No Images</p>' in self._req.text:
                raise EmptyChapter(self.manga_name, self.chapter_number)
            self._soup = BeautifulSoup(self._req.text, "html.parser")

            self._mono = self._req.text.count("dm5_key") == 1
            self.chapter_name = " ".join(
                self._soup.find("p", class_="reader-header-title-2").text.split("Ch.")[-1].split(" ")[1:])

            if self._mono:
                self._mono_go_to_chap()
            else:
                self._multi_go_to_chap()

            self.image = self._image_list[0]

    def _mono_go_to_chap(self):
        """
        Method used to get the obfuscated image info in mono type scan chapters.
        *mono type chapters are characterized by having all the images displayed one after another in a single page*
        """

        out = self._decode(self._req.text)
        self._image_list = [f"https:{page.split('?')[0]}" for page in out.split("=[")[1].split("];")[0].replace("'", "").split(",")]  # get the inside of the js list of images and transforms it onto the proper python list of image
        self._last_page = len(self._image_list)

    def _multi_go_to_chap(self):
        """
        Method used to get obfuscated image info in multi type scan chapters.
        *multi type chapters are characterized by having one image per page*
        """

        cid = self._req.text.split("var chapterid =")[1].split(";")[0]
        self._last_page = max([int(i.text) for i in self._soup.find_all(lambda x: x.has_attr("data-page") and x.text.isdigit())])

        for page in range(1, self._last_page+1):
            if page > len(self._image_list):
                req2 = requests.get(f"https://fanfox.net/chapterfun.ashx?cid={cid}&page={page}&key={secrets.token_hex(8)}", headers=self._header)
                out = self._decode(req2.text)
                root = out.split("(){")[1].split('pix="')[1].split('";')[0]
                chaps = [i.split("?")[0] for i in out.split("pvalue=[")[1].split("];")[0].split('"') if i != "" and i != ","]

                for i in chaps:
                    if i[0] != "/":
                        i = "/" + i
                    self._image_list.append(f"https:{root + i}")

    def next_image(self):
        self.image = self._image_list[self.npage]
        self.npage += 1
        self.ext = self.image.split(".")[-1]

    def is_last_image(self):
        # automatically ignoring the last page of add
        return self.npage == len(self._image_list)-1

    def next_chapter(self):
        self.go_to_chapter(self._soup.find("a", class_="reader-main-next").get("href").split("/")[-2][1:])

    def is_last_chapter(self):
        try:
            self._soup.find("a", class_="reader-main-next").get("href").split("/")[-2][1:]
            return False
        except AttributeError:
            return True

    @classmethod
    def scan(cls, link:str=None, manga:str=None):
        if link is not None:
            manga_id = link.split("manga/")[1].split("/")[0]
        elif manga is not None:
            manga_id = manga.replace(" ", "_")

        rss_url = f"https://fanfox.net/rss/{manga_id}.xml"

        try:
            req = requests.get(rss_url)
            if req.status_code == 522:
                raise DownedSite("https://fanfox.net")
            xml_root = ET.fromstring(req.text)
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


