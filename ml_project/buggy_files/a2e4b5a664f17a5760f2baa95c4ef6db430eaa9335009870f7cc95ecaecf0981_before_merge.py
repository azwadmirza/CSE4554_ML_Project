def main(args, error):
    """
    Makes sure that the assets have been converted,
    and jumps into the C++ main method.
    """
    del error  # unused

    # we have to import stuff inside the function
    # as it depends on generated/compiled code
    from .main_cpp import run_game
    from .. import config
    from ..assets import get_asset_path
    from ..convert.main import conversion_required, convert_assets
    from ..cppinterface.setup import setup as cpp_interface_setup
    from ..cvar.location import get_config_path
    from ..util.fslike.union import Union

    # initialize libopenage
    cpp_interface_setup(args)

    info("launching openage {}".format(config.VERSION))
    info("compiled by {}".format(config.COMPILER))

    if config.DEVMODE:
        info("running in DEVMODE")

    # create virtual file system for data paths
    root = Union().root

    # mount the assets folder union at "assets/"
    root["assets"].mount(get_asset_path(args))

    # mount the config folder at "cfg/"
    root["cfg"].mount(get_config_path(args))

    # ensure that the assets have been converted
    if conversion_required(root["assets"], args):
        if not convert_assets(root["assets"], args):
            err("game asset conversion failed")
            return 1

    # start the game, continue in main_cpp.pyx!
    return run_game(args, root)