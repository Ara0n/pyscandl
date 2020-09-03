.. _fetchers:

Fetchers
********

In this section you will be able to see more about how fetchers work in general but also some specifics about them.


What is a fetcher ?
===================

Fetchers are the tools used by pyscandl to get the manga's information on the website. For each website and/or API there is a fetcher that is dedicated to it.

Because website can or not archive their scans as chapters of a manga or treat all the scans as standalones, the fetcher type used will have to be different.


Can I make my own fetchers too ?
================================

Yes you can, and quite easily. Once you have determined which if the scans are treated as standalones or not, you just need to use the right abstract fetcher class to make your fetcher and follow the documentation bellow about what is mandatory to include in your fetcher.


The 2 types of Fetchers
=======================

Standard fetcher
----------------

This will be the abstract fetcher class used for the fetchers of websites treating their scans in chapters.

Just bellow you will have the specification about the abstract class.
All the methods here are required for you to implement for your fetcher to work with the exception of ``.quit()`` that is already here.
*(but if your fetcher needs some things to close safely you can place it in the ``.quit()`` method)*

All the required attributes of you fetcher are also listed here.

.. autoclass:: pyscandl.modules.fetchers.fetcher.Fetcher
    :members:
    :special-members: __init__


Standalone fetcher
------------------

This will be the abstract fetcher class used for the fetchers of websites treating their scans as standalone entries.

Just bellow you will have the specification about the abstract class.
All the methods here are required for you to implement for your fetcher to work with the exception of ``.quit()`` that is already here.
*(but if your fetcher needs some things to close safely you can place it in the ``.quit()`` method)*

All the required attributes of you fetcher are also listed here.

.. autoclass:: pyscandl.modules.fetchers.fetcher.StandaloneFetcher
    :members:
    :special-members: __init__


Already implemented fetchers and fetcher listing
================================================

.. toctree::
    :maxdepth: 2
    :glob:

    fetchers/fetcher_enum
    fetchers/*