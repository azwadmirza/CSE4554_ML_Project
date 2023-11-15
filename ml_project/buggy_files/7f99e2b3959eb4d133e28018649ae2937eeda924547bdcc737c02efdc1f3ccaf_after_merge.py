def get_string_resources(args):
    """ reads the (language) string resources """
    from .stringresource import StringResource
    stringres = StringResource()

    srcdir = args.srcdir
    count = 0

    # AoK:TC uses .DLL PE files for its string resources,
    # HD uses plaintext files
    if GameVersion.age2_fe in args.game_versions:
        from .hdlanguagefile import read_hd_language_file

        for lang in srcdir["resources"].list():
            try:
                if lang == b'_common':
                    continue
                langfilename = ["resources", lang.decode(), "strings", "key-value",
                                "key-value-strings-utf8.txt"]

                with srcdir[langfilename].open('rb') as langfile:
                    stringres.fill_from(read_hd_language_file(langfile, lang))

                count += 1
            except FileNotFoundError:
                # that's fine, there are no language files for every language.
                pass
    elif GameVersion.age2_hd_3x in args.game_versions:
        from .hdlanguagefile import read_hd_language_file

        # HD Edition 3.x and below store language .txt files in the Bin/ folder.
        # Specific language strings are in Bin/$LANG/*.txt.
        for lang in srcdir["bin"].list():
            dirname = ["bin", lang.decode()]

            # There are some .txt files immediately in bin/, but they don't seem
            # to contain anything useful. (Everything is overridden by files in
            # Bin/$LANG/.)
            if not srcdir[dirname].is_dir():
                continue

            for basename in srcdir[dirname].list():
                langfilename = ["bin", lang.decode(), basename]
                with srcdir[langfilename].open('rb') as langfile:
                    # No utf-8 :(
                    stringres.fill_from(read_hd_language_file(langfile, lang, enc='iso-8859-1'))
                count += 1
    elif srcdir["language.dll"].is_file():
        from .pefile import PEFile
        for name in ["language.dll", "language_x1.dll", "language_x1_p1.dll"]:
            pefile = PEFile(srcdir[name].open('rb'))
            stringres.fill_from(pefile.resources().strings)
            count += 1

    if not count:
        raise FileNotFoundError("could not find any language files")

    # TODO transform and cleanup the read strings:
    #      convert formatting indicators from HTML to something sensible, etc

    return stringres