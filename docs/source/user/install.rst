.. _installGuide:

Installation
============

This installation guide describes the installation of VPMBench for Linux.
We currently do not support Windows.

Getting the Source
------------------

You can download the current version of the VPMBench source from GitHub:

.. code-block:: console

    $ git clone git@github.com:IDEA-PRIO/VPMBench.git


Dependencies
------------

Python Version
^^^^^^^^^^^^^^

We recommend using the latest version of Python 3.
VPMBench supports Python 3.6 or newer.

You can check your Python version by running the following command in your terminal:

.. code-block:: console

    $ python --version
    Python 3.9.1

These Python libraries will be installed automatically when installing VPMBench:

* `Pandas`_ implements a tabular data-structure.
* `Pandera`_ provides schema-based validations for Pandas
* `PyYaml`_ implements a YAML-Parser
* `Docker-SDK`_ lets you do anything ``docker`` command does
* `Scikit-learn`_ implements a bunch of machine-learning algorithms
* `Numpy`_ provides a large collection of mathematical functions
* `PyVCF`_ implement a parser for VCF-files

.. _Pandas: https://pandas.pydata.org/
.. _Pandera: https://pandera.readthedocs.io/en/stable/
.. _PyYaml: https://pyyaml.org/
.. _Docker-SDK: https://docker-py.readthedocs.io/en/stable/
.. _Scikit-learn: https://scikit-learn.org/stable/
.. _Numpy: https://numpy.org/
.. _PyVCF: https://pyvcf.readthedocs.io/en/latest/

Docker
^^^^^^

VPMBench requires `Docker`_ to run the variant prioritization methods.
Therefore, you have to ensure that you have the proper rights to run Docker commands as the current user.
You can easily check this by running:

.. code-block:: console

    $ docker run hello-world

    Hello from Docker!
    This message shows that your installation appears to be working correctly.

    To generate this message, Docker took the following steps:
     1. The Docker client contacted the Docker daemon.
     2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
        (amd64)
     3. The Docker daemon created a new container from that image which runs the executable that produces the output you are currently reading.
     4. The Docker daemon streamed that output to the Docker client, which sent it to your terminal.

    To try something more ambitious, you can run an Ubuntu container with:
     $ docker run -it ubuntu bash

    Share images, automate workflows, and more with a free Docker ID:
     https://hub.docker.com/

    For more examples and ideas, visit:
     https://docs.docker.com/get-started/

If an error occurs check the `Docker Documentation`_ and try again.

.. _Docker: https://www.docker.com/
.. _Docker Documentation: https://docs.docker.com/engine/install/linux-postinstall/


Automatic Installation
----------------------

In the repository, we provide an installation script ``install.sh``.
Using the installation script, you have to answer questions, e.g., for the plugin directory.
Currently, we support the automatic installation of CADD and fathmm-MKL.
Please make sure that Docker is installed and that enough disk space is available to install the plugin.
If you want to install fathmm-MKL, tabix needs to be installed on your machine:

.. code-block:: console

    $ sudo apt install tabix
    $ tabix --version
    tabix (htslib) 1.10.2-3
    Copyright (C) 2019 Genome Research Ltd.

After answering the questions, you will see an overview of the selected files before the download and installation starts.

.. code-block:: console

    $ chmod +x install.sh
    $ ./install.sh

The complete installation with the two provided plugins for CADD and fathmm-MKL might take 2-3h and uses about 300GB of your disk space.
So it's enough time to drink a coffee or two.

Manual Installation
-------------------

While we recommend using the automatic installation procedure, you can also install VPMBench following the following steps.

Step 1 - Create a plugin directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By :mod:`default <vpmbench.config>` VPMBench expects the plugins to be installed in the ``VPMBench`` directory in the home directory of the current user.
You can create the directory via:

.. code-block:: console

    $ mkdir ~/VPMBench-Plugins

Step 2 - Install VPMBench
^^^^^^^^^^^^^^^^^^^^^^^^^

To install VPMBench, simply run this simple command in your terminal after entering ``VPMBench`` directory:

.. code-block:: console

    $ cd VPMBench
    $ pip install .

We recommend installing VPMBench in its own `virtual environment`_ to prevent any conflicts with already installed Python libraries.

.. _`virtual environment`: https://docs.python.org/3/library/venv.html

After the installation you should be able to run the following command without errors:

.. code-block:: console

    $ python -c "import vpmbench"

Congratulations, you now can use VPMBench in your projects.
You now might have a look at the :ref:`Quickstart Guide <quickstart>` or the :ref:`API Documentation <api>`.

.. _installPlugins:

Step 3 - Copy and install plugins  (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The currently provided plugins can be found in the ``/plugin`` directory for the repository.
To use these plugins you have to copy them to your plugin directory from Step 1.
The following copies all plugins to the default plugin directory:

.. code-block:: console

    $ cp plugins/* ~/VPMBench-Plugins

After this, the plugins have to be installed.
Therefore, each plugin directory contains its installation script ``install.sh`` which builds the Docker image and downloads the required files.
After this, the plugins are ready to be used in VPMBench.

Step 4 - Test the installed plugins (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test the installed plugins you can run the script ``bin/after_install.py``.
Therefore, you have to provide a VCF-file as input and specify your plugin-path.

.. code-block:: console

    $ python /bin/after_install.py tests/resources/test_grch37.vcf ~/VPMBench-Plugins

During the execution of the script logging information is written to your terminal.
The output should look like this:

.. code-block:: console

    $ python /bin/after_install.py tests/resources/test_grch37.vcf ~/VPMBench-Plugins
    .....
    .....
    .....
