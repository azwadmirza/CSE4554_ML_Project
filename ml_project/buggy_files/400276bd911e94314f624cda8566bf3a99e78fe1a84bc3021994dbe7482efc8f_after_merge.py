def print_version() -> None:
    """Prints version information of rasa tooling and python."""

    try:
        from rasax.community.version import __version__  # pytype: disable=import-error

        rasa_x_info = __version__
    except ModuleNotFoundError:
        rasa_x_info = None

    print(f"Rasa Version     : {version.__version__}")
    print(f"Rasa SDK Version : {rasa_sdk_version}")
    print(f"Rasa X Version   : {rasa_x_info}")
    print(f"Python Version   : {platform.python_version()}")
    print(f"Operating System : {platform.platform()}")
    print(f"Python Path      : {sys.executable}")