def main(argv):
    args = argv[1:]
    for fname in args:
        fp = open(fname, 'rb')
        cmap = FileUnicodeMap()
        #cmap = FileCMap()
        CMapParser(cmap, fp).run()
        fp.close()
        cmap.dump()
    return