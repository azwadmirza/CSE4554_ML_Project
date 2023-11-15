    def sha512_encode(path, inode=None):
        if inode is None:
            inode = stat(path).st_ino
        sha = sha512(
            "{0}{1}".format(path, str(inode)).encode('utf-8', 'backslashescape')
        )
        return '{0}.jpg'.format(sha.hexdigest())