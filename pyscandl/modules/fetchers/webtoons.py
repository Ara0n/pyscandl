import requests
from bs4 import BeautifulSoup

from pyscandl.modules.excepts import DryNoSauceHere, MangaNotFound
from pyscandl.modules.fetchers.fetcher import Fetcher


class Webtoons(Fetcher):
    def __init__(self, link: str = None, manga: str = None, chapstart=1, lang=""):
        super().__init__(chapstart=chapstart)

        if lang:
            self._lang = lang

        if manga is not None:
            self._manga_id = manga
        elif link is not None:
            self._manga_id = link.split("=")[1]
        else:
            raise DryNoSauceHere()

        self._cookies = {"ageGatePass": "true"}
        self.headers = {
            "referer": "http://www.webtoons.com/",
            "contentLanguage": self._lang
        }
        self.domain = ".webtoons.com"

        req = requests.get(f"https://webtoons.com/LANG/CATEGORY/NAME/list?title_no={self._manga_id}",
                           cookies=self._cookies, headers=self.headers)
        if req.status_code == 404:
            raise MangaNotFound(self._manga_id)
        soup = BeautifulSoup(req.text, features="html.parser")

        self.author = soup.find("meta", property="com-linewebtoon:webtoon:author").get("content")
        if not self.author:
            self.author = "TBD"

        self.manga_name = soup.find("meta", property="og:title").get("content")
        self._last_chap = int(soup.find(id="_listUl").findChild("li").get("data-episode-no"))

        self.go_to_chapter(chapstart)

    def next_image(self):
        self.image = self._imgs[self.npage]
        self.npage += 1
        self.ext = self.image.split(".")[-1]

    def is_last_image(self):
        return self.npage == len(self._imgs)

    def go_to_chapter(self, chapter_no):
        self.npage = 1
        self.chapter_number = chapter_no
        req = requests.get(
            f"https://www.webtoons.com/LANG/CATEGORY/NAME/CHAPTITLE/viewer?title_no={self._manga_id}&episode_no={self.chapter_number}",
            cookies=self._cookies,
            headers=self.headers
        )

        if req.status_code == 404:
            raise MangaNotFound(f"{self._manga_id}, chapter {chapter_no}")
        self._chap_soup = BeautifulSoup(req.text, features="html.parser")

        self.chapter_name = self._chap_soup.find("h1", class_="subj_episode").get("title")

        img_tags = self._chap_soup.find(id="_imageList").findChildren("img")
        self._imgs = [img.get("data-url").split("?")[0] for img in img_tags]
        self.image = self._imgs[self.npage - 1]
        self.ext = self.image.split(".")[-1]

    def next_chapter(self):
        self.go_to_chapter(self.chapter_number + 1)

    def is_last_chapter(self):
        return self.chapter_number == self._last_chap

    @classmethod
    def scan(cls, link: str = None, manga: str = None, lang: str = ""):
        if lang:
            cls._lang = lang

        if manga is not None:
            _manga_id = manga
        elif link is not None:
            _manga_id = link.split("=")[1]
        else:
            raise DryNoSauceHere()

        _cookies = {"ageGatePass": "true"}
        headers = {
            "referer": "http://www.webtoons.com/",
            "contentLanguage": cls._lang
        }

        req = requests.get(f"https://webtoons.com/LANG/CATEGORY/NAME/list?title_no={_manga_id}",
                           cookies=_cookies, headers=headers)
        if req.status_code == 404:
            raise MangaNotFound(_manga_id)
        soup = BeautifulSoup(req.text, features="html.parser")

        _last_chap = int(soup.find(id="_listUl").findChild("li").get("data-episode-no"))

        return [chap for chap in range(1, _last_chap + 1)]


class WebtoonsEN(Webtoons):
    _lang = "en"


class WebtoonsFR(Webtoons):
    _lang = "fr"
