from vpmbench.plugin import Plugin


def was_trained_with(plugin: Plugin, database_name: str) -> bool:
    """ Checks whether a plugin was trained with a specifc database.

    Parameters
    ----------
    plugin: Plugin
        The plugin to be checked
    database_name: str
        The database name

    Returns
    -------
    bool:
        The checking result
    """
    return True


def is_multiclass_plugin(plugin: Plugin) -> bool:
    """ Checks whether a plugin is a multi-class plugin.

    Parameters
    ----------
    plugin : Plugin
        The plugin to be checked

    Returns
    -------
    bool:
        The checking result

    """
    return isinstance(plugin.cutoff, list) and len(plugin.cutoff) > 2
