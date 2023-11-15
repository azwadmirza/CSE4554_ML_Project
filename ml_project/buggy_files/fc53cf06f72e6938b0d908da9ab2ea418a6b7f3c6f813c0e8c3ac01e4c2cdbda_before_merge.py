    def symlink(value, filename):    #analysis:ignore
        newlinkname = filename+"."+unique()+'.newlink'
        newvalname = os.path.join(newlinkname, "symlink")
        os.mkdir(newlinkname)
        f = _open(newvalname, 'wb')
        f.write(to_binary_string(value))
        f.flush()
        f.close()
        try:
            rename(newlinkname, filename)
        except:
            try:
                os.remove(newvalname)
                os.rmdir(newlinkname)
            except (IOError, OSError):
                pass
            raise