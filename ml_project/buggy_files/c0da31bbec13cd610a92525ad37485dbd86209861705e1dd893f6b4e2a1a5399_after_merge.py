    def __pls_export(self, file_path, files):
        try:
            fhandler = open(file_path, "wb")
        except IOError:
            self.__file_error(file_path)
        else:
            text = "[playlist]\n"

            for num, f in enumerate(files):
                num += 1
                text += "File%d=%s\n" % (num, f['path'])
                text += "Title%d=%s\n" % (num, f['title'])
                text += "Length%d=%s\n" % (num, f['length'])

            text += "NumberOfEntries=%d\n" % len(files)
            text += "Version=2\n"

            fhandler.write(text.encode("utf-8"))
            fhandler.close()