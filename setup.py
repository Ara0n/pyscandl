from setuptools import setup

with open("README.rst", "r") as f:
    readme = f.read()

with open("requirements.txt", "r") as f:
    requires = f.readlines()

setup(
    name='pyscandl',
    version='2.2.1',
    packages=['pyscandl', 'pyscandl.modules', 'pyscandl.modules.autodl', 'pyscandl.modules.fetchers'],
    url='https://pyscandl.readthedocs.io/',
    license='BSD-3-Clause License',
    author='Thomas MONTERO | Ara0n',
    author_email='thomas99.montero@gmail.com',
    description='a scan downloader in python',
    keywords=" scraping web scan download manga comics mangadex webtoon nhentai fanfox",
    project_urls={
        "Documentation": "https://pyscandl.readthedocs.io",
        "Source Code": "https://github.com/Ara0n/pyscandl"
    },
    python_requires=">=3.7",
    entry_points={"console_scripts": ["pyscandl = pyscandl.main:main"]},
    long_description=readme,
    long_description_content_type='text/x-rst',
    install_requires=requires,
    package_data={
        "pyscandl.modules.fetchers": ["eval.js"],
        "pyscandl": ["banlist/*"]
    }
)
