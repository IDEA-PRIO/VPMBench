"""
The config modules defines the following variables:

.. data:: DEFAULT_PLUGIN_PATH

    The default plugin path where vpmbench searches for plugins.

    :type: :py:class:`pathlib.Path`
    :value: The directory VPMBench-Plugins in the home directory of the current user, e.g, ``/home/user/VPMBench-Plugins``.

"""
from pathlib import Path

DEFAULT_PLUGIN_PATH = (Path.home() / "VPMBench-Plugins").resolve()
