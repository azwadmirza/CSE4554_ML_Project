def write_head(fo):
    fo.write("==> %s <==\n" % time.strftime(TIME_FORMAT))
    fo.write("# cmd: %s\n" % (' '.join(sys.argv)))