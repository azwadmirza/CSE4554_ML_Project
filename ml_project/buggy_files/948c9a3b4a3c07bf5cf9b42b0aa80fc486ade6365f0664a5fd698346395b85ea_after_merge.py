def compute_md5(idirs):
    released = paver.path.path(idirs).listdir()
    checksums = []
    for fn in sorted(released):
        with open(fn, 'rb') as f:
            m = md5(f.read())
        checksums.append('%s  %s' % (m.hexdigest(), os.path.basename(fn)))

    return checksums