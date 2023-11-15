    def on_add_mdblob_browse_file(self):
        filenames = QFileDialog.getOpenFileNames(self,
                                                 "Please select the .mdblob file",
                                                 QDir.homePath(),
                                                 "Tribler metadata files (*.mdblob.lz4)")
        if len(filenames[0]) > 0:
            for filename in filenames[0]:
                self.pending_uri_requests.append(u"file:%s" % filename)
            self.process_uri_request()