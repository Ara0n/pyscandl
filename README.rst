.. unicode definitions

.. |check| unicode:: U+2611 .. checked box
.. |uncheck| unicode:: U+2610 .. unchecked box

.. badges
.. |doc_status| image:: https://readthedocs.org/projects/pyscandl/badge/?version=latest
    :target: https://pyscandl.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. |pypi_version| image:: https://img.shields.io/pypi/v/pyscandl
    :target: https://pypi.org/project/pyscandl/
    :alt: Latest PyPI version
.. |wheel| image:: https://img.shields.io/pypi/wheel/pyscandl
   :alt: PyPI - Wheel
.. |nb_gh_commits| image:: https://img.shields.io/github/commits-since/Ara0n/pyscandl/latest
    :alt: GitHub commits since latest release (by SemVer)
.. |release_date| image:: https://img.shields.io/github/release-date/Ara0n/pyscandl
    :alt: Release Date
.. |nb_issues| image:: https://img.shields.io/github/issues/Ara0n/pyscandl
   :target:  https://github.com/Ara0n/pyscandl/issues
   :alt: GitHub issues
.. |source_code| image:: https://img.shields.io/badge/Source-GitHub-success
   :target: https://github.com/Ara0n/pyscandl
   :alt: GitHub source code
.. |license| image:: https://img.shields.io/github/license/Ara0n/pyscandl
    :alt: software license

Welcome to Pyscandl
*******************

.. csv-table::
    :stub-columns: 1
    :widths: 10, 30

    "Documentation", |doc_status|
    "PyPI", |pypi_version| |wheel| |release_date|
    "GitHub", |nb_gh_commits| |nb_issues| |license| |source_code|

Pyscandl is a tool to download Mangas and Webtoons from various Manga and Webtoon sites easily.

    | *Don't overuse this tool.*
    | *Support the developers of those websites by disabling your adblock on their site. Advertisments pay for the website servers.*
    | *Get the mangas from official retailers when they are accessible in your country !*

It is also built to be lightweight and to not require external tools like selenium, to be used you only need python 3.7 or higher and nodejs installed.

You can download manually one or a set of chapters from a manga or setup an auto downloader that will check for you if a new chapter is out and if yes download it.

A full documentation of the project is available at https://pyscandl.readthedocs.io with:

* an `installation guide <https://pyscandl.readthedocs.io/en/latest/pages/installation.html>`_
* a `usage guide <https://pyscandl.readthedocs.io/en/latest/pages/usage.html>`_
* and a full code documentation


Websites sutported
==================

The list of currently supported websites is:

* `Mangadex <https://mangadex.org>`_ (english and french, if you want more languages, just ask and I'll add them)
* `Fanfox <https://fanfox.net>`_
* `NHentai <https://nhentai.net>`_
* `Naver comics <https://comic.naver.com>`_
* `FRScan <https://www.frscan.me/>`_

Pyscandl is far from its end stage so other websites can be added if needed, don't hesitate to ask in the issues about a new website to add.

Planned for future releases
===========================

| |check| readthedocs documentation
| |check| pypi release
| |check| import and export the ``autodl`` database
| |uncheck| text user interface
| |check| fetchers rework
| |check| remove node dependence for fanfox
