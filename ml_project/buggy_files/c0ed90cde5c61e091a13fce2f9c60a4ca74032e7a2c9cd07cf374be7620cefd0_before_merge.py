def main(cliargs=None):
    """Entry point for the application script

    :param list cliargs: Arguments to parse or None (=use :class:`sys.argv`)
    :return: error code
    :rtype: int
    """
    try:
        parser = createparser()
        args = parser.parse_args(args=cliargs)
        # args.parser = parser
        result = process(args)
        print(result)
        return 0

    except (ValueError, TypeError) as err:
        print("ERROR", err, file=sys.stderr)
        return 2