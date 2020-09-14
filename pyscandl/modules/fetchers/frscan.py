from bs4 import BeautifulSoup
import requests
import re

from pyscandl.modules.fetchers.fetcher import Fetcher
from pyscandl.modules.excepts import MangaNotFound, DryNoSauceHere, DelayedRelease

class FRScan(Fetcher):
    def __init__(self, link: str = None, manga: str = None, chapstart=1):
        # getting the manga id
        super().__init__(chapstart=chapstart)
        if manga is not None:
            self._link = f"https://www.frscan.me/manga/{manga}"
            manga_id = manga
        elif link is not None:
            if link[-1] == "/":
                link = link[:-1]
            manga_id = link.split("/")[-1]
            self._link = link
        else:
            raise DryNoSauceHere()

        req = requests.get(self._link)
        if req.status_code == 404:
            raise MangaNotFound(manga_id)

        manga_soup = BeautifulSoup(req.text, "html.parser")
        chap_tags = manga_soup.find("ul", class_="chapters")

        chap_nb = []
        chap_name = []
        for chap in chap_tags.find_all("a", href=re.compile(rf"{self._link}/\d+(?:\.\d+)?")):
            nb = chap.get("href").split("/")[-1]
            if "." in nb:
                chap_nb.append(float(nb))
            else:
                chap_nb.append(int(nb))

            if chap.find_next_sibling("span").text:
                chap_name.append(-1)
            else:
                chap_name.append(chap.find_next_sibling("em").text)

        self._chaps = dict(zip(chap_nb, chap_name))

        self.author:str = manga_soup.find("dt", string="Auteur(s)").find_next_sibling("dd").findChild("a").text.strip()  #: name of the author of the manga default to TBD if none is found
        self.manga_name:str = manga_soup.find("h2", class_="widget-title").text.strip()  #: name of the manga currentl in the fetcher
        self.domain:str = ".frscan.me"  #: domain of the website the fetcher is currently on looks like: .domname.ext
        self.go_to_chapter(chapstart)

    def go_to_chapter(self, chap):
        self.chapter_number = int(chap)
        self.chapter_name:str = self._chaps.get(self.chapter_number)
        if self.chapter_name is None:
            raise MangaNotFound(f"{self.manga_name}, chapter {self.chapter_number}")
        if self.chapter_name == -1:
            raise DelayedRelease(f"{self.manga_name}, chapter {self.chapter_number}", "later")

        req = requests.get(f"{self._link}/{self.chapter_number}/1")
        self._chap_soup = BeautifulSoup(req.text, "html.parser")

        self.image: str = self._chap_soup.find(class_="img-responsive scan-page").get("src").strip()  #: url to the image currently in the fetcher
        if "http" not in self.image.split("/")[0]:
            self.image = "http:" + self.image
        self.ext: str = self.image.split(".")[-1]  #: extention of the image currently in the fetcher
        self.npage: int = 1  #: number of the page the fetcher is currently on

    def next_image(self):
        self.npage += 1
        req = requests.get(f"{self._link}/{self.chapter_number}/{self.npage}")
        self._chap_soup = BeautifulSoup(req.text, "html.parser")

        self.image: str = self._chap_soup.find(class_="img-responsive scan-page").get("src").strip()  #: url to the image currently in the fetcher
        if "http" not in self.image.split("/")[0]:
            self.image = "http:" + self.image
        self.ext: str = self.image.split(".")[-1]  #: extention of the image currently in the fetcher

    def next_chapter(self):
        for i in sorted(self._chaps):
            if i > self.chapter_number:
                self.go_to_chapter(i)
                break

    def is_last_image(self):
        options = self._chap_soup.find(id="page-list").find_all("option")
        return self.npage == int(max(options, key=lambda option: int(option.get("value"))).get("value"))

    def is_last_chapter(self):
        return self.chapter_number == max(self._chaps.keys())

    @classmethod
    def scan(cls, link: str = None, manga: str = None):
        if manga is not None:
            link = f"https://www.frscan.me/manga/{manga}"
            manga_id = manga
        elif link is not None:
            if link[-1] == "/":
                link = link[:-1]
            manga_id = link.split("/")[-1]
            link = link
        else:
            raise DryNoSauceHere()

        req = requests.get(link)
        if req.status_code == 404:
            raise MangaNotFound(manga_id)

        manga_soup = BeautifulSoup(req.text, "html.parser")
        chap_tags = manga_soup.find("ul", class_="chapters")
        chap_nb = []
        for chap in chap_tags.find_all("a", href=re.compile(rf"{link}/\d+(?:\.\d+)?")):
            nb = chap.get("href").split("/")[-1]
            if "." in nb:
                chap_nb.append(float(nb))
            else:
                chap_nb.append(int(nb))

        return chap_nb