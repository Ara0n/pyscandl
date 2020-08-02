Naver
*****

.. warning::
    This fetcher was made following an issue request for it, i personally don't speak korean at all so i id it all while using the source-code and google translate to get website specific info. As a result, the fetcher might not be free of bugs and it will be hard for me to debug ths kind of issue as i'm not a korean reader. If you ever encounter some while using it, please report them so i can address the issue as soon as possible.

`Naver comics <https://comic.naver.com>`_ is a popular korean website to consult and read webtoons. It devides the entries in 3 categories depending on the quality, Webtoon being the highest, followed by bestChallenge and finally Challenge. The more detailed explanation about the 3 different tiers can be found here: https://kubera.fandom.com/wiki/Naver

You normally should know this already if you use this site but just in case you can see in which category the webtoon belongs with the url of the webtoon, it is the second part of the url juste after ``https://comic.naver.com/`` with either ``webtoon``, ``bestChallenge`` or ``challenge``.

To download the webtoon, just use the fetcher corresponding to the right category.

.. note:: The manga id is what follows ``titleId=`` and the chapter number what follows ``no=``.


Naver webtoon collection
========================

.. autoclass:: modules.fetchers.NaverWebtoon
    :members:
    :inherited-members:
    :special-members: __init__


Naver bestChallenge collection
==============================

.. autoclass:: modules.fetchers.NaverBestChallenge
    :members:
    :inherited-members:
    :special-members: __init__


Naver challenge collection
==========================

.. autoclass:: modules.fetchers.NaverChallenge
    :members:
    :inherited-members:
    :special-members: __init__
