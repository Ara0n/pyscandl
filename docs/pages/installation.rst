Installation
************


From source
===========

1. check if you have ``python3.7`` or above installed *(modern installations normally have it installed by default now)*
2. check if you have the corresponding ``pip`` installed
3. clone the repository

.. code-block::

    git clone https://github.com/Ara0n/pyscandl.git

4. install the dependencies of ``pyscandl``

.. code-block:: bash

    cd pyscandl
    python3 -m pip install -r requirements.txt

.. note::
    the name of the python used might differ depending on your OS and or pythons installed, just be sure to use one with ``pip`` and that is ``python3.7`` or higher

5. install ``nodejs``
    * windows installer can be found `here <https://nodejs.org/en/download>`_
    * for linux use your distributions package manager
    * for mac either do like windows or use homebrew

.. code-block:: bash

    brew install node

The program is now ready to be used, don't forget from time to time to check if new code and features were added and if yes do a ``git pull``


From release
============

1. check if you have ``python3.7`` or above installed *(modern installations normally have it installed by default now)*
2. check if you have the corresponding ``pip`` installed
3. download the `latest release <https://github.com/Ara0n/pyscandl/release/latest>`_ here
4. install the dependencies of ``pyscandl``

.. code-block:: bash

    cd pyscandl
    python3 -m pip install -r requirements.txt

.. note::
    the name of the python used might differ depending on your OS and or pythons installed, just be sure to use one with ``pip`` and that is ``python3.7`` or higher

5. install ``nodejs``
    * windows installer can be found `here <https://nodejs.org/en/download>`_
    * for linux use your distributions package manager
    * for mac either do like windows or use homebrew

.. code-block:: bash

    brew install node

The program is now ready to be used, don't forget from time to time to check if a new release is out `here <https://github.com/Ara0n/pyscandl/release/latest>`_ and if yes download it.

Requirements
============

The current python requirements are:

.. literalinclude:: ../../pyscandl/requirements.txt

Nodejs is also needed.
