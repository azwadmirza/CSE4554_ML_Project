def get_module(name):
    """
    Return module or None. Absolute import is required.

    :param (str) name: Dot-separated module path. E.g., 'scipy.stats'.
    :raise: (ImportError) Only when exc_msg is defined.
    :return: (module|None) If import succeeds, the module will be returned.

    """
    if name not in _not_importable:
        try:
            return import_module(name)
        except ImportError:
            _not_importable.add(name)
        except Exception as e:
            _not_importable.add(name)
            msg = "Error importing optional module {}".format(name)
            logger.exception(msg)