def clean_ini(path, section, parameter):
    """Delete sections and parameters (aka option) in the file"""

    def write(parser, ini_file):
        """
        Reimplementation of the original RowConfigParser write function.

        This function is 99% same as its origin. The only change is
        removing a cast to str. This is needed to handle unicode chars.
        """
        if parser._defaults:
            ini_file.write("[%s]\n" % "DEFAULT")
            for (key, value) in parser._defaults.items():
                ini_file.write("%s = %s\n" %
                               (key, str(value).replace('\n', '\n\t')))
            ini_file.write("\n")
        for section in parser._sections:
            ini_file.write("[%s]\n" % section)
            for (key, value) in parser._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (parser._optcre == parser.OPTCRE):
                    # The line bellow is the only changed line of the original function.
                    # This is the orignal line for reference:
                    # key = " = ".join((key, str(value).replace('\n', '\n\t')))
                    key = " = ".join((key, value.replace('\n', '\n\t')))
                ini_file.write("%s\n" % (key))
            ini_file.write("\n")

    encoding = detect_encoding(path) or 'utf_8_sig'

    # read file to parser
    config = bleachbit.RawConfigParser()
    config.optionxform = lambda option: option
    config.write = write
    with open(path, 'r', encoding=encoding) as fp:
        config.read_file(fp)

    # change file
    changed = False
    if config.has_section(section):
        if parameter is None:
            changed = True
            config.remove_section(section)
        elif config.has_option(section, parameter):
            changed = True
            config.remove_option(section, parameter)

    # write file
    if changed:
        from bleachbit.Options import options
        fp.close()
        if options.get('shred'):
            delete(path, True)
        with open(path, 'w', encoding=encoding, newline='') as fp:
            config.write(config, fp)