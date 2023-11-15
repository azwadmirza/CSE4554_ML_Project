def main(argv=sys.argv[1:]):  # type: ignore
    # type: (List[unicode]) -> int
    locale.setlocale(locale.LC_ALL, '')
    sphinx.locale.init_console(os.path.join(package_dir, 'locale'), 'sphinx')

    if argv[:1] == ['-M']:
        return make_main(argv)
    else:
        return build_main(argv)