Usage
*****

Command Line Interface
======================

.. note::
    Maintaining that section up-to-date might take longer that the releases can happen, in that case please refer to the built-in help command with ``-h``.

main command
------------

The program is divided in different subcommands, the root doesn't have any special actions except accessing the subcommands.

.. literalinclude:: ../CLI help/main.txt
    :language: none


manual command
--------------

This command allows you to manually download on or a set of chapters for a specific manga. For it to work you'll need to specify at least a link or an id to the manga, the save format for the downloaded scan and the corresponding :ref:`fetchers` to the chapter.

.. literalinclude:: ../CLI help/manual.txt
    :language: none


autodl command
--------------

This command allow you to automatically search for new scans that are out for a set of mangas that you previously added to the database with the `add sub-command`_. The mangas that will be searched are the ones not archived in the database.

.. literalinclude:: ../CLI help/autodl.txt
    :language: none


manga command
-------------

The manga command is the part that controls the database used by the `autodl command`_. it is itself composed of a subset of commands allowing different actions in the database such as adding, removing or editing the infos of an entry.

Each entry in the database consists of:

* the name of the manga
* a link the the manga's main page
* a link to the manga's rss feed
* the name of the fetcher used
* the list of all the downloaded chapters
* if the manga is archived or not

.. literalinclude:: ../CLI help/manga.txt
    :language: none


add sub-command
'''''''''''''''

The add sub-command allows you to add a new entry to the database for the `autodl command`_.

.. literalinclude:: ../CLI help/manga add.txt
    :language: none


edit sub-command
''''''''''''''''

The edit sub-command allows you to edit one of the already existing entries of the database.

.. literalinclude:: ../CLI help/manga edit.txt
    :language: none


info sub-command
''''''''''''''''

The info sub-command gives you the information available about the requested database entry.

The info consists of:

* the name of the manga
* a link the the manga's main page
* a link to the manga's rss feed
* the name of the fetcher used
* the list of all the downloaded chapters
* the number of last chapter downloaded
* the total of chapters downloaded
* if the manga is archived or not

.. literalinclude:: ../CLI help/manga info.txt
    :language: none


chaplist sub-command
''''''''''''''''''''

The chaplist sub-command gives you the list of all the chapters downloaded with the `autodl command`_ for this entry in the database.

.. literalinclude:: ../CLI help/manga chaplist.txt
    :language: none


delete sub-command
''''''''''''''''''

The delete sub-command deletes the specified entry from the database.

.. warning:: There is no trash so every use of this command cannot be undone, if you are unsure about the deletion, backup the database first !

.. literalinclude:: ../CLI help/manga delete.txt
    :language: none


rmchaps sub-command
'''''''''''''''''''

The rmchap sub-command deletes all the chapters listed from the entry of the database requested.

.. note:: if you delete the wrong chapters you will download them again the lext time you use the `autodl command`_ as they will no longer be seen as already downloaded.

.. literalinclude:: ../CLI help/manga rmchaps.txt
    :language: none
