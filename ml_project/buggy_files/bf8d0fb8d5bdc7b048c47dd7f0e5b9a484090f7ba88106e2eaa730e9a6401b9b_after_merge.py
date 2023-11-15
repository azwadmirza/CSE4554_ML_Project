def init_subparser(cli):
    """ Initializes the parser for convert-specific args. """
    import argparse

    cli.set_defaults(entrypoint=main)

    cli.add_argument("--palette", default="50500", help="palette number")
    cli.add_argument("--interfac", type=argparse.FileType('rb'),
                     help=("drs archive where palette "
                           "is contained (interfac.drs). "
                           "If not set, assumed to be in same "
                           "directory as the source drs archive"))
    cli.add_argument("drs", type=argparse.FileType('rb'),
                     help=("drs archive filename that contains the slp "
                           "e.g. path ~/games/aoe/graphics.drs"))
    cli.add_argument("slp", help=("slp filename inside the drs archive "
                                  "e.g. 326.slp"))
    cli.add_argument("output", help="image output path name")