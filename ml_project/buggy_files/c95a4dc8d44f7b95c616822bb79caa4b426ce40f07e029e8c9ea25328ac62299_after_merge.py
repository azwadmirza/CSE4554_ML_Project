    def __m3u_export(self, file_path, files):
        try:
            fhandler = open(file_path, "wb")
        except IOError:
            self.__file_error(file_path)
        else:
            text = "#EXTM3U\n"

            for f in files:
                text += "#EXTINF:%d,%s\n" % (f['length'], f['title'])
                text += f['path'] + "\n"

            fhandler.write(text.encode("utf-8"))
            fhandler.close()