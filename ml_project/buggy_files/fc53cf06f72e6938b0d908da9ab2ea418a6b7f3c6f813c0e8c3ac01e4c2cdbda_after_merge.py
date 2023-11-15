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
            # This is needed to avoid an error when we don't
            # have permissions to write in ~/.spyder
            # See issues 6319 and 9093
            try:
                os.remove(newvalname)
                os.rmdir(newlinkname)
            except (IOError, OSError):
                return
            raise