import requests

from .fetcher import Fetcher
from ..excepts import DownedSite, MangaNotFound


class Mangadex(Fetcher):
    __doc__ = """this is the new fetcher for mangadex using their new v5 api, the api is still in beta so all of this fetcher is subject to changes quickly"""

    def __init__(self, link:str=None, manga:str=None, chapstart=1, lang=""):
        """
        Initializes the instance of the mangadex fetcher, it needs either manga or link to work.

        :param link: link of the wanted scan
        :type link: str
        :param manga: id of the wanted scan
        :type manga: str
        :param chapstart: chapter on which to start
        :param lang: language used
        :type lang: str

        :raises MangaNotFound: couldn't find the manga that was asked for with the id or the link
        """
        super().__init__(link, manga, chapstart)

        # language stuff to fetch for specific locales
        if lang:
            self._lang = lang
        self.domain = ".mangadex.org"

        # init some api stuff that will be useful later
        self._api_base = "https://api.mangadex.org"
        self._api_manga_feed = self._api_base + "/manga/{uuid}/feed?limit=500&locales[]={locale}&order[chapter]=asc&offset={offset}"

        # getting the legacy id from the links
        # TODO: change that when the new links are out while giving a tool to do the change
        if manga is not None:
            legacy_id = int(manga)
        elif link is not None:
            if link[-1] == "/":
                link = link[:-1]
            legacy_id = int(link.split("/")[-2])

        # getting the new id from the legacy ones
        req = requests.post(self._api_base + "/legacy/mapping", json={"type": "manga", "ids": [legacy_id]})
        if req.status_code != 200:
            raise MangaNotFound(f" legacy id {legacy_id}")
        id = req.json()[0]["data"]["attributes"]["newId"]

        # getting the manga title name (either english or romanji)
        manga_req = requests.get(self._api_base + f"/manga/{id}")
        if manga_req.status_code != 200:
            raise MangaNotFound(f"id {id}")
        manga = manga_req.json()
        self.manga_name = list(manga["data"]["attributes"]["title"].values())[0]

        # getting the author name
        author_id = next((relation["id"] for relation in manga["relationships"] if relation["type"]=="author"), None)
        author_req = requests.get(self._api_base + f"/author/{author_id}")
        if author_req.status_code == 200:
            self.author = author_req.json()["data"]["attributes"]["name"]

        # getting the chapter info from the feed
        feed_req = requests.get(self._api_manga_feed.format(uuid=id, locale=self._lang, offset=0))
        feed = feed_req.json()
        self._chapinfo = [chap["data"] for chap in feed["results"] if chap["data"]["attributes"]["chapter"] is not None]
        for i in range(500, int(feed["total"]), 500):
            feed_req = requests.get(self._api_manga_feed.format(uuid=id, locale=self._lang, offset=i))
            self._chapinfo.extend([chap["data"] for chap in feed_req.json()["results"] if chap["data"]["attributes"]["chapter"] is not None])

        # checking if there are no duplicate numbers for chapters
        unique_chaps = {chap["attributes"]["chapter"] for chap in self._chapinfo}
        if len(self._chapinfo) != len(unique_chaps):
            new_chap_list = []
            for i in unique_chaps:
                new_chap_list.append(next(chap for chap in self._chapinfo if chap["attributes"]["chapter"]==i))
            self._chapinfo = sorted(new_chap_list, key=lambda x: float(x["attributes"]["chapter"]))

        self.go_to_chapter(next((chapter["attributes"]["chapter"] for chapter in self._chapinfo if chapter["attributes"]["chapter"] == str(chapstart))))

    def go_to_chapter(self, chap):
        """
        Go to the specified chapter.

        :param chap: number of the specified chapter

        :raises MangaNotFound: the asked chapter doesn't exist
        :raises DownedSite: the md@h service is down
        """

        try:
            self._current_chap = next((chapter for chapter in self._chapinfo if chapter["attributes"]["chapter"] == str(chap)))
        except StopIteration:
            raise MangaNotFound(f"{self.manga_name}, chapter {chap}")

        self.chapter_number = self._current_chap["attributes"]["chapter"]
        self.chapter_name = self._current_chap["attributes"]["title"]

        # get md@h corresponding server
        md_at_h_server = requests.get(self._api_base + f"/at-home/server/{self._current_chap['id']}")
        if md_at_h_server.status_code != 200:
            raise DownedSite(self.domain)
        self._server_url = md_at_h_server.json()["baseUrl"]

        self.npage = 1
        # creating first image url
        self.image = f"{self._server_url}/data/{self._current_chap['attributes']['hash']}/{self._current_chap['attributes']['data'][0]}"

    def is_last_chapter(self):
        return self._chapinfo.index(self._current_chap)+1 == len(self._chapinfo)

    def is_last_image(self):
        return self.npage == len(self._current_chap["attributes"]["data"])

    def next_chapter(self):
        next_index = self._chapinfo.index(self._current_chap) + 1
        self.go_to_chapter(self._chapinfo[next_index]["attributes"]["chapter"])

    def next_image(self):
        self.image = f"{self._server_url}/data/{self._current_chap['attributes']['hash']}/{self._current_chap['attributes']['data'][self.npage]}"
        self.npage += 1

    @classmethod
    def scan(cls, link:str=None, manga:str=None, lang=""):
        # language stuff to fetch for specific locales
        if lang:
            cls._lang = lang

        # init some api stuff that will be useful later
        api_base = "https://api.mangadex.org"
        api_manga_feed = api_base + "/manga/{uuid}/feed?limit=500&locales[]={locale}&order[chapter]=asc&offset={offset}"

        # getting the legacy id from the links
        # TODO: change that when the new links are out while giving a tool to do the change
        if manga is not None:
            legacy_id = int(manga)
        elif link is not None:
            if link[-1] == "/":
                link = link[:-1]
            legacy_id = int(link.split("/")[-2])

        # getting the new id from the legacy ones
        req = requests.post(api_base + "/legacy/mapping", json={"type": "manga", "ids": [legacy_id]})
        if req.status_code != 200:
            raise MangaNotFound(f" legacy id {legacy_id}")
        id = req.json()[0]["data"]["attributes"]["newId"]

        # getting the chapter info from the feed
        feed_req = requests.get(api_manga_feed.format(uuid=id, locale=cls._lang, offset=0))
        feed = feed_req.json()
        chapinfo = [float(chap["data"]["attributes"]["chapter"]) if "." in chap["data"]["attributes"]["chapter"] else int(chap["data"]["attributes"]["chapter"]) for chap in feed["results"] if chap["data"]["attributes"]["chapter"] is not None]
        for i in range(500, int(feed["total"]), 500):
            feed_req = requests.get(api_manga_feed.format(uuid=id, locale=cls._lang, offset=i))
            chapinfo.extend([float(chap["data"]["attributes"]["chapter"]) if "." in chap["data"]["attributes"]["chapter"] else int(chap["data"]["attributes"]["chapter"]) for chap in feed_req.json()["results"]])

        # checking if there are no duplicate numbers for chapters
        unique_chaps = {chap for chap in chapinfo}
        if len(chapinfo) != len(unique_chaps):
            new_chap_list = []
            for i in unique_chaps:
                new_chap_list.append(next(chap for chap in chapinfo if chap==i))
            chapinfo = sorted(new_chap_list)


        return chapinfo


class MangadexEN(Mangadex):
    _lang = "en"


class MangadexFR(Mangadex):
    _lang = "fr"
