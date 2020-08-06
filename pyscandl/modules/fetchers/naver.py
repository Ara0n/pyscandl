import requests
from bs4 import BeautifulSoup
from .fetcher import Fetcher
from ..excepts import MangaNotFound


class Naver(Fetcher):
    def __init__(self, link:str=None, manga:str=None, chapstart=1, collection=""):
        super().__init__(link, manga, chapstart)
        if collection:
            self._collection = collection
        self.domain = ".comic.naver.com"

        if link is not None:
            self._manga_id = link.partition("titleId=")[-1]
        elif str(manga).isdigit():
            self._manga_id = manga
        else:
            raise MangaNotFound(manga)

        self._set_current_chap_info(self.chapter_number)

    def _set_current_chap_info(self, chap_id):
        self.npage = 1
        self.chapter_number = int(chap_id)
        self._chap_url = f"https://comic.naver.com/{self._collection}/detail.nhn?titleId={self._manga_id}&no={self.chapter_number}"
        self._chap_req = requests.get(self._chap_url)

        if self._chap_req.url == "https://comic.naver.com/main.nhn":
            raise MangaNotFound(self._manga_id)

        self._bs4 = BeautifulSoup(self._chap_req.text, "html.parser")

        if self._chap_req.url == f"https://comic.naver.com/{self._collection}/list.nhn?titleId={self._manga_id}" or int(self._chap_req.url.partition("&no=")[-1]) != int(self.chapter_number):
            raise MangaNotFound(f"{self._manga_id}, chapter {self.chapter_number}")

        self.author = self._bs4.find("div", class_="comicinfo").findChild("span", class_="wrt_nm").text.strip()
        self.chapter_name = self._bs4.find("div", class_="tit_area").findChild("h3").text
        self.manga_name = self._bs4.find("div", class_="comicinfo").findChild("div", class_="detail").findChild("h2").contents[0]

        self._img_list = self._bs4.find(class_="wt_viewer").findChildren("img")

        self.image = self._img_list[0].get("src")
        self.ext = self.image.split(".")[1]

    def next_image(self):
        self.image = self._img_list[self.npage].get("src")
        self.ext = self.image.split(".")[1]
        self.npage += 1

    def go_to_chapter(self, chap):
        self._set_current_chap_info(chap)

    def next_chapter(self):
        self._set_current_chap_info(self.chapter_number + 1)

    def is_last_image(self):
        return self.npage == len(self._img_list)

    def is_last_chapter(self):
        return self.chapter_number == int(self._bs4.find("div", class_="pg_area").findChild("span", class_="total").text)

    @classmethod
    def scan(cls, link:str=None, manga:str=None):
        if link is not None:
            manga_id = link.partition("titleId=")[-1]
        elif str(manga).isdigit():
            manga_id = manga
        else:
            raise MangaNotFound(manga)

        req = requests.get(f"https://comic.naver.com/webtoon/detail.nhn?titleId={manga_id}")

        if req.url == "https://comic.naver.com/main.nhn":
            raise MangaNotFound(manga_id)

        last_chap = int(req.url.split("&no=")[-1])

        return list(range(1, last_chap + 1))


class NaverWebtoon(Naver):
    _collection = "webtoon"  # set at class level for the scan method

    def __init__(self, link:str=None, manga:str=None, chapstart=1):
        super().__init__(link, manga, chapstart)


class NaverBestChallenge(Naver):
    _collection = "bestChallenge"  # set at class level for the scan method

    def __init__(self, link:str=None, manga:str=None, chapstart=1):
        super().__init__(link, manga, chapstart)


class NaverChallenge(Naver):
    _collection = "challenge"  # set at class level for the scan method

    def __init__(self, link:str=None, manga:str=None, chapstart=1):
        super().__init__(link, manga, chapstart)
