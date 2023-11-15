def main(argv):
    args = argv[1:]
    for fname in args:
        fp = open(fname, 'rb')
        cmap = FileUnicodeMap()
        CMapParser(cmap, fp).run()
        fp.close()
        cmap.dump()
    return