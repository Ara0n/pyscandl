import setuptools
from setuptools import setup
from pyscandl import __version__

with open("README.rst", "r") as f:
    readme = f.read()

requires = [
    "requests~=2.25.1",
    "wand~=0.6.5",
    "Pillow~=8.1.0",
    "cfscrape~=2.1.1",
    "beautifulsoup4~=4.9.3",
    "PyQt5~=5.15.2",
]

setup(
    name='pyscandl',
    version=__version__,
    packages=setuptools.find_packages(),
    url='https://pyscandl.readthedocs.io/',
    license='BSD 3-Clause License',
    author='Thomas MONTERO | Ara0n',
    author_email='thomas99.montero@gmail.com',
    description='a scan downloader in python',
    keywords="scraping web scan download manga comics mangadex webtoon nhentai fanfox naver frscan english french cli gui qt",
    project_urls={
        "Documentation": "https://pyscandl.readthedocs.io",
        "Source Code": "https://github.com/Ara0n/pyscandl",
        "Bug Tracker": "https://github.com/Ara0n/pyscandl/issues",
    },
    python_requires=">=3.7",
    entry_points={"console_scripts": ["pyscandl = pyscandl.__main__:main", "pyscandl-qt = pyscandl.__main__:main_gui"]},
    long_description=readme,
    long_description_content_type='text/x-rst',
    install_requires=requires,
    package_data={
        "pyscandl": ["banlist/*"],
        "": ["README.rst", "CHANGELOG.rst"]
    }
)
