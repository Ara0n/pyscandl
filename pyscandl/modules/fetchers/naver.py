import requests
from bs4 import BeautifulSoup
from pyscandl.modules.fetchers.fetcher import Fetcher
from pyscandl.modules.excepts import MangaNotFound


class Naver(Fetcher):
    def __init__(self, collection,  link: str = None, manga: str = None, chapstart=1):
        super().__init__(link, manga, chapstart)
        self._collection = collection
        self.domain = ".comic.naver.com"

        if link is not None:
            self._manga_id = link.partition("titleId=")[1]
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


def create_naver_webtoon_fetcher(link: str = None, manga: str = None, chapstart=1):
    return Naver("webtoon", link, manga, chapstart)


def create_naver_bestchallenge_fetcher(link: str = None, manga: str = None, chapstart=1):
    return Naver("bestChallenge", link, manga, chapstart)


def create_naver_challenge_fecher(link: str = None, manga: str = None, chapstart=1):
    return Naver("challenge", link, manga, chapstart)
