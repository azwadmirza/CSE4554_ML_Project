def main(argv):
    for fname in argv[1:]:
        fp = open(fname, 'rb')
        font = CFFFont(fname, fp)
        print (font)
        fp.close()
    return