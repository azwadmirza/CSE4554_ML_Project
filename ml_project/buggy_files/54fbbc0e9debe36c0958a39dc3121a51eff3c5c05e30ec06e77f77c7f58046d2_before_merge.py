def compute_sha256(idirs):
    # better checksum so gpg signed README.txt containing the sums can be used
    # to verify the binaries instead of signing all binaries
    released = paver.path.path(idirs).listdir()
    checksums = []
    for fn in sorted(released):
        with open(fn, 'rb') as f:
            m = sha256(f.read())
        checksums.append('%s  %s' % (m.hexdigest(), os.path.basename(f)))

    return checksums