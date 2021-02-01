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

Welcome to Pyscandl's documentation!
************************************

.. csv-table::
    :stub-columns: 1
    :widths: 10, 30

    "Documentation", |doc_status|
    "PyPI", |pypi_version| |wheel| |release_date|
    "GitHub", |nb_gh_commits| |nb_issues| |license| |source_code|

Introduction
============

Pyscandl is a python program made to be able to download scans of mangas and webtoons on multiple different websites without the need for `selenium <https://www.selenium.dev/>`_ and its `python version <https://selenium-python.readthedocs.io/>`_.

The currently supported websites are:

* `Fanfox <https://fanfox.net>`_ who also own the mangazone app
* `Mangadex <https://mangadex.com>`_ with EN and FR scans (if more languages are needed, juste ask and they'll be added in the next possible release)
* `NHentai <https://nhentai.net>`_
* `Naver <https://comic.naver.com>`_ with the Webtoon, BestChallenge and Challenge collections.
* `FRScan <https://www.frscan.me/>`_ **currently not working because of a change in cloudflare.**
* `Webtoons <https://webtoons.com>`_ with EN and FR scans (if more languages are needed, juste ask and they'll be added in the next possible release)


.. warning::
   | *Don't overuse this tool.*
   | *Support the developers of those websites by disabling your adblock on their site. Advertisments pay for the website servers.*
   | *Get the mangas from official retailers when they are accessible in your country !*

.. toctree::
   :maxdepth: 2
   :caption: Table of content:
   :glob:

   pages/installation
   pages/usage
   pages/pyscandl
   pages/fetcher
   pages/autodl
   pages/exceptions
   pages/CHANGELOG





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
