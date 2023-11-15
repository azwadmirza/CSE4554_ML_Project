def cli_convert(infile, outfile, silent, verbosity, **options):
    """
    canmatrix.cli.convert [options] import-file export-file

    import-file: *.dbc|*.dbf|*.kcd|*.arxml|*.json|*.xls(x)|*.sym
    export-file: *.dbc|*.dbf|*.kcd|*.arxml|*.json|*.xls(x)|*.sym|*.py

    \n"""

    root_logger = canmatrix.log.setup_logger()

    if silent is True:
        # only print error messages, ignore verbosity flag
        verbosity = -1
        options["silent"] = True

    canmatrix.log.set_log_level(root_logger, verbosity)
    if options["ignoreEncodingErrors"]:
        options["ignoreEncodingErrors"] = "ignore"
    else:
        options["ignoreEncodingErrors"] = ""

    canmatrix.convert.convert(infile, outfile, **options)
    return 0