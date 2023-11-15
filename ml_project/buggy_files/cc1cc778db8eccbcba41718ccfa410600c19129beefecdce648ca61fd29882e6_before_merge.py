    def sha512_encode(path, inode=None):
        if inode is None:
            inode = stat(path).st_ino
        inode_path = "{0}{1}".format(str(inode), path)
        if PY3:
            inode_path = inode_path.encode('utf-8', 'backslashescape')
        return '{0}.jpg'.format(sha512(inode_path).hexdigest())