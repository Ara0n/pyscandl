Changelog
=========


3.0.0-b2 (2021-02-23)
---------------------

New
~~~
- Added a GUI interface for pyscandl with pyQt, you can use it either with ``pyscandl gui`` or ``pyscandl-qt``, you have access to the same ``manual``, ``manga`` and ``autodl`` options.


Changes
~~~~~~~
- You can now use filter out StandaloneFetcher of FetcherEnum.list()

- Controller.save() no longer closes the connection.

- Added an option to only list the manga names without the additional info and formatting.


Fix
~~~
- No longer crashing when stopping ``pyscandl manga scan`` with ``Ctrl+C``

- Usr fixed db creation, duplicate chapters and chapter edit from beta, a script will be given at release to update from the beta 1 version db.


3.0.0-b1 (2021-02-13)
---------------------

New
~~~
- Added a ``manga scan [name]`` option to check if there are new chapter released without downloading them. Placing a name will make it search for that specific manga, otherwise it scans for all the non archived mangas in the db.

- Command option to migrate the db with ``pyscandl manga migrate``

- The pdf creation is now made with Wand and no longer img2pdf. `ImageMagick <https://imagemagick.org>`_ is now needed for the pdf creation instead.


Changes
~~~~~~~
- Updated the CLI help outputs.

- Scan will now throw MangaNotFound if the requested manga isn't in the db.

- ``autodl`` and ``manga`` now uses the new db.


Fix
~~~
- Removed outdated references to the rss and json.

- Fanfox download no longuer crashes on 504 errors.

- Issue with chapters being skipped with ``autodl`` when retrying in some cases.


2.10.0 (2021-02-01)
-------------------

New
~~~
- Added changelog to pyscandl, from now on commits will respect the format asked by https://github.com/vaab/gitchangelog.


Changes
~~~~~~~
- Added warning for future changes in the next major release.


2.9.0 (2021-01-24)
------------------
- Fanfox now uses bs4 instead of most regex to make it easier to maintain.

- Resolved the pb with the new TBE volumes on fanfox and added an exception for future situations.

- Typo and new  stuff on the roadmap and 4 space indents.

- Updated requirements.

- Updated to survive server error 522.

- ...


2.8.3 (2020-11-16)
------------------
- Now also lists the used fetcher.

- Ffs.


2.8.2 (2020-11-16)
------------------
- Fixed -e not supporting floats.

- Frscan now needs cfscrape.

  the current cfscrape can't handle the verification of couldflare it'll need updates, see https://github.com/Anorov/cloudflare-scrape/issues/394
- Fixed an issue with -k sometimes being funky when loading images back.

- Fixed initialisation for downloader.


2.8.0 (2020-10-06)
------------------
- Updated README.

- Added webtoons to the enum and the cli.

- Fixed naming problem.

- Fetchers can now ask the downloader to add stuff in the header when downloading the images like referrers.

- Added a fetcher for https://webtoons.com for french and english.

- Simplified mangadex fetcher.

- Updated gitignore for wheel building.

- Updated installation guide.

- Added a collapse template.

- Fixed image urls.

- Fixed standalone check.


2.7.1 (2020-09-07)
------------------
- Fixed and improved mangadex fetchers.


2.7.0 (2020-09-04)
------------------
- Updated README and tags.

- Proper title.

- Forgot dependence.

- Fixed adding to PYTHONPATH from autodoc.

- Added more use for __version__

- Added the fetcher for the french website frscan.me.

- Added the french version for mangadex.

- Forgot to list Naver.


2.6.0 (2020-09-01)
------------------
- Removed the need for node for the Fanfox fetcher.


2.5.2 (2020-08-27)
------------------
- Added more downed site interaction.

- Added exception if the website is downed.


2.5.0 (2020-08-19)
------------------
- Addressed issue #5 now illegal windows characters will be replaced by █ in the file and folder names.

- Added headers to scan.

- Better exception verbose.

- Updated README.rst.

- Removed the rss from the cli and the controller database as it's no longer needed for autodl.

- Added a dedicated exception for mangas that are visible but not available yet.

- Fixed scan if no chapters were found.

- Cleaner manual interruption in autodl.

- Added a scan method to fetchers to streamline and ease the implementation in autodl.


2.4.0 (2020-08-02)
------------------
- Fixed imports.

- Updated README.rst.

- Added naver doc.

- Added bs4 requirement.

- Added badges.

- Updtaed doc imports.

- Fixed imports.

- Added naver fetcher.

- Now with classes.

- Added stuff in init.py to help referencing, and changed the code adequately.

- Set self.chapter_number default correctly.

- Added fetcher for naver.

- Checked fetcher rework.

- Added badges.

- The current fetchers now use the ABC for fetchers.

- Added ABC for fetchers as a guidline to help their creation.

- Typo.

- Forgot to check this.


2.3.0 (2020-07-27)
------------------
- Fixed crash with an empty db.

- Added a way to import and export the db to the cli.

- Added a way to import and export the db.

- Added a new command to do.


2.2.2 (2020-07-27)
------------------
- Fixed requirements.


2.2.1 (2020-07-27)
------------------
- Typo in console entry-point.

- Added pypi badge.

- Fixed typo.


2.2.0 (2020-07-27)
------------------
- Restructured to be able to be built with a setup.py and a future pypi release.


2.1.0 (2020-07-20)
------------------
- Better format.

- Fixed warning.

- Changed README and added todo to the documentation.

- Added examples for the CLI usage and fixed some text issues.

- Forgot to specify the good master-doc name.

- Fresh restart, hopefully now works.

- Forgot gitkeep for folders.

- No pdf generation for the moment to cleanup the logs.

- Removed generate.

- Added suffix.

- Fix masterdoc.

- Should fix the readthedocs generation.

- Added the config for readthedocs.

- Small adjustments.

- Added the possibility to archive mangas in autodl.

- Full documentation of the code using reST.

- Future proofed the risk of circular imports.

- Added the -e option asked for in this issue https://github.com/Ara0n/pyscandl/issues/3.

- Cleanup requirements.txt and removed -U option.

- Updated requirements.

- Bandaid fix for the xml fetching problems.

- Don't crash if no chapters specified.

- Don't crash if data transmission is corrupted.

- More readable now.

- No longer crash if no author found.

- Better chapter number detection.


2.0.0 (2020-02-05)
------------------
- Removed deprecated fetcher.

- Updated README with the different download modes.

- Now has 3 download modes pdf only, image only and both.

- Updated README with the new cli.

- Now uniform arg for chapters for all the subparsers of manga.

- Standalone should be a class attribute and not an instance attribute.

- Reworked the parser and the cli.

- Fixed README.

- Optimised download process.

- Checks if the chapter is empty now.

- Removed old useless dependence used in tests.

- Fixed requirements.

- Indent level fixed.

- Mangadex back on the .org domain.

- Temporary change to the new temporary domain of mangadex.

- Updated requirements.

- Better error handling.

- Merge remote-tracking branch 'origin/fanfox_re-rework'

- Sorts json entries now.

- Pep8.

- Sanitized chapter and manga name.

- Typo.

- Typo.

- Now using pexpect for the node calls to make it faster.

- Better exception management.

- Easier to detect when the output stops now.

- New decode script.

- Don't crash if no chapters downloaded yet.

- Fixed verbose.

- Fixed if no author is given on the webpage.

- Added remove chapter option for json.

- Updated requirements.

- Quiet option for all the subparsers now.

- Remove the directory if there is no chapter.

- Don't crash now in case of heavy loaded server for mangadex.


1.1.0 (2019-11-18)
------------------
- Updated requirements.

- Added credit.

- Naming issue.

- Added sauce to the chap_name.

- Fixed chapter regex.

- Now raise EmptyChapter.

- Updated README.

- Made some variables protected.

- Made some methods and some variables protected and some public.

- Merging fanfox_rework.

- Complete fetcher rework.

- Helper for the reworked fanfox.

- Fixed if no chapter in the json autodl db when starting.

- Fixed if chapter is empty when adding a manga to the json autodl db.


1.0.1 (2019-11-11)
------------------
- Fixed image extension for the first image in `.go_to_chapter()`

- Fixed initialization.

- Fixed first image when using go_to_chapter.

- Fixed pdf path when using go_to_chapter.

- Removed "/" from chapter name.


1.0.0 (2019-11-10)
------------------
- Update issue templates.

- Create LICENSE.

- Updated requirements.

- Fixed fanfox empty chapter crash.

- Added got_to_chapter method.

- Fixes and improvements.

- No longer throws an error if the manga isn't in the json.

- Optimised download method.

- Made some methods public.

- Better download order.

- Improved add command.

- Renamed exception properly.

- Updated README.

- Fixes and improvements.

- Imporved Exception.

- Added chapter-list option.

- Remade to support the new arg_parser options.

- Fixes.

- Restructured options and subparsers.

- Added controller for the future autodl.

- Forgot __init__

- Added exception for future autodl.

- Restructured project and changed to relative imports.

- Modified parser to support the future auto updater.

- Fixed `-n` option and `fanfox_mono`

- Fixed regex for chapter numbers and removed unnecessary regex for chapter name.

- Fixed import name conflict.

- Added author support.


0.4.1 (2019-10-26)
------------------
- Remade image loading system.

- Silenced img2pdf and improved verbose and `quiet` option.

- Created headers for download requests and added `.domain` to fetchers.

- Added support for images with alpha-channel so you wont crash anymore because of images with alpha-channels.

- Removed comment.


0.4.0 (2019-10-14)
------------------
- Merge pull request #1 from Ara0n/nh_rework.

  fixed not getting the last image in mangadex
- Fixed not getting the last image in mangadex.

- Fixed not getting the last image in mangadex.

- Revert "fixed not getting the last image in mangadex"

  This reverts commit 445cd5b9
- Merge branch 'nh_rework'

- .standalone implemented.

- Improved image extention management.

- Removed _ext_check()

- Nhentai don't have a chapter in save path anymore.

- Reworked nhentai with the api.

- Now fetches last image of chapters.

- Remade updater.


0.3.1 (2019-10-12)
------------------
- Fixed chapter language filtering and sorting.

- Fixed not using the fetcher author.


0.3.0 (2019-10-12)
------------------
- Renamed to requirments.txt to have dependency graph on github.

- Fixed pdf metadata name to support the tiny option.

- Merge branch 'mangadex'

  # Conflicts:
  #	Pyscandl.py
- Updated requirements.

- Created mangadex fetcher with link and manga id support.

- Fixed pdf saving issue when changing to the next chapter with tiny option.

- Added tiny option to remove the manga name from the pdf name.

- Updated readme and preparing author support.

- Fixed naming issue when changing to the next chapter.

- Fixed naming issues with some chapters and improved general naming and numerotation.

- Fixed exception imports for inside python use.

- Fixed issue with badly formatted titles on the website.

- Fixed is_last_chapter() method returning wrong boolean.


0.2.1 (2019-09-27)
------------------
- Fixed repo path for the updater.


0.2.0 (2019-09-27)
------------------
- Added updater based on github releases.

- Layed ground for the creation of an updater.

- Now supports chapters with an xx.x number.

- Fixed issues in the image banning and the pdf creation.


0.1.0 (2019-09-23)
------------------
- Fixed naming for the first chapter of downloads.

- Added install process for linux.

- Fixed the non suppression of the `geckodriver.log` in case of manga not found.

- Nh supports MangaNotFound.

- Added custom exceptions.

- Fixed link editing.

- Fixed last chapter detection.

- Added requirements and created venv.

- Fixed the extensions for the non -k mode and cleaned code.

- Fixed and optimized extension for nh.py.

- Fixed if the extention for nh is .png.

- Now properly handles the extra chapters (.5, .1, .2 and co.)

- Added metadata for title and author of the pdf.

- Ctrl+C closes the fetcher before quitting now.

- Added a new fetcher for the single page mangas on fanfox.

- Added image to banlist.

- Fixed title regex.

- Added __pycache__ to the ignore list.

- Forgot first image fetch when changing chapter.

- Better naming for files and folder.

- Fixed naming of the chapters.

- Included with the `fix module name to avoid conflict with builtin modules old commit`

- Creating a banlist feature that removes from the pdf all the images in `banlist/`

- Fix module name to avoid conflict with builtin modules.

- Added the adult check for fanfox.

- Changed the pdf conversion from `convert` to `img2pdf`, added a fetch mode that keeps all the image data in ram without copying the images on the disk if not using `-k` and renamed `start` to `skip`

- Added the start option.

- Verbose now works.

- Headless again now that the fixes have been done.

- Added link for info about the selenium installation process.

- Added fanfox multipage to the fetchers (last commit failed)

- Added quiet support.

- Few fixes and added the quit method.

- Added on term to the API.

- Fixed problem with page order.

- Added missing / in path.

- Using fstring now.

- PEP8 space.

- Now command line shown is correct.

- Added command line support.

- Added the pycandl.

- CamelCase class now.

- Updated API removing `.next()`

- Fixed variable scope and added and extention var.

- Added epilogue to the help message with all the available fetchers in the enum and added a return for the args.

- ORDER reeee.

- Created the first image fetcher from nh.

- Createdthe enumeration that'll be used for the fetcher selection.

- Added command line parser.

- Added dependencies and installation references, some more API settings for the fetcher and written down the interface of the constructor.

- README now has the command line interface and the image fetcher API.

- Added .gitignore.


