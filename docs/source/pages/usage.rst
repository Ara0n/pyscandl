Usage
*****

.. warning:: The database will migrate and be changed during the next major release. There will be a command to do the migration on release, don't forget to do it.

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

Example
"""""""

The following command downloads to the ``books/`` folder the chapters from 10 to 20 for the manga fullmetal alchemist on https://mangadex.org in a pdf format:

.. code-block:: none

    pyscandl -l https://mangadex.org/title/286/fullmetal-alchemist -f mangadex -o books/ -c 10 -e 20 -p


autodl command
--------------

This command allow you to automatically search for new scans that are out for a set of mangas that you previously added to the database with the `add sub-command`_. The mangas that will be searched are the ones not archived in the database.

.. literalinclude:: ../CLI help/autodl.txt
    :language: none

Example
"""""""

The following command will launch the auto download in a tiny mode to the folder ``book/autodl/`` in pdf format:

.. code-block:: none

    pyscandl -o books/autodl/ -t -p


manga command
-------------

The manga command is the part that controls the database used by the `autodl command`_. It is itself composed of a subset of commands allowing different actions in the database such as adding, removing or editing the infos of an entry.

.. note:: An archived manga wont be checked when using ``-l`` or with the ``autodl`` subcommand.

You can also use this command to list all the current manga in the database and to import or export a database.

Each entry in the database consists of:

* the name of the manga
* a link the the manga's main page
* a link to the manga's rss feed
* the name of the fetcher used
* the list of all the downloaded chapters
* if the manga is archived or not

.. literalinclude:: ../CLI help/manga.txt
    :language: none

Listing database entries
""""""""""""""""""""""""

You can use the ``pyscandl manga`` command to list the current mangas that are in the database

Example
'''''''

The following command lists all the names of the non-archived mangas in the database:

.. code-block:: none

    pyscandl manga -l

The following command lists all the names of the archived mangas in the database:

.. code-block:: none

    pyscandl manga -lo

The following command lists all the names of the mangas in the database, even the archived ones:

.. code-block:: none

    pyscandl manga -la


Importing and exporting the database
""""""""""""""""""""""""""""""""""""

It is possible to import and export databases with the ``pyscandl manga`` command. It can be usefull to make backups or install already existing databases in a new pyscandl installation.

Example
'''''''

The following command exports your current database into a ``db.json`` file in ``Documents/pyscandl/``

.. code-block:: none

    pyscandl manga -e Documents/pyscandl

The following command imports the file at ``Documents/pyscandl/backup/db.json`` to the current database of pyscandl

.. code-block:: none

    pyscandl manga -i Documents/pyscandl/backup/db.json


add sub-command
"""""""""""""""

The add sub-command allows you to add a new entry to the database for the `autodl command`_.

.. literalinclude:: ../CLI help/manga add.txt
    :language: none

Example
'''''''

The following command adds the manga fullmetal alchemist from the website https://mangadex.og to the database under the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga add "fullmetal alchemist" -r https://mangadex.org/rss/wApuURnPsDZ92gX7Th4BySW8dqcVeaCM/manga_id/286 -l https://mangadex.org/title/286/fullmetal-alchemist -f mangadex


edit sub-command
""""""""""""""""

The edit sub-command allows you to edit one of the already existing entries of the database.

.. literalinclude:: ../CLI help/manga edit.txt
    :language: none

Example
'''''''

The following command archives the manga saved under the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga edit "fullmetal alchemist" -a


info sub-command
""""""""""""""""

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

Example
'''''''

The following command gets the info about the database entry saved with the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga info "fullmetal alchemist"


chaplist sub-command
""""""""""""""""""""

The chaplist sub-command gives you the list of all the chapters downloaded with the `autodl command`_ for this entry in the database.

.. literalinclude:: ../CLI help/manga chaplist.txt
    :language: none

Example
'''''''

The following command gets the list of chapters downloaded for the database entry saved with the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga chaplist "fullmetal alchemist"


delete sub-command
""""""""""""""""""

The delete sub-command deletes the specified entry from the database.

.. warning:: There is no trash so every use of this command cannot be undone, if you are unsure about the deletion, backup the database first !

.. literalinclude:: ../CLI help/manga delete.txt
    :language: none

Example
'''''''

The following command gets deletes the database entry saved with the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga delete "fullmetal alchemist"


rmchaps sub-command
"""""""""""""""""""

The rmchap sub-command deletes all the chapters listed from the entry of the database requested.

.. note:: if you delete the wrong chapters you will download them again the lext time you use the `autodl command`_ as they will no longer be seen as already downloaded.

.. literalinclude:: ../CLI help/manga rmchaps.txt
    :language: none

Example
'''''''

The following command removes the chapters 10, 25, 42 and 6.9 from the list of downloaded chapters for the manga saved under the name "fullmetal alchemist":

.. code-block:: none

    pyscandl manga rmchaps "fullmetal alchemist" 10 25 42 6.9
