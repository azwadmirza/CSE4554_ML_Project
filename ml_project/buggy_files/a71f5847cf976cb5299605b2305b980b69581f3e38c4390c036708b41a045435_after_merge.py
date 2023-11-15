    def clearShares(
        self, sharedfiles, bsharedfiles, sharedfilesstreams, bsharedfilesstreams,
        wordindex, bwordindex, fileindex, bfileindex, sharedmtimes, bsharedmtimes
    ):

        try:
            if sharedfiles:
                sharedfiles.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'files.db'))
            except Exception:
                pass
            sharedfiles = shelve.open(os.path.join(self.data_dir, "files.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if bsharedfiles:
                bsharedfiles.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'buddyfiles.db'))
            except Exception:
                pass
            bsharedfiles = shelve.open(os.path.join(self.data_dir, "buddyfiles.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if sharedfilesstreams:
                sharedfilesstreams.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'streams.db'))
            except Exception:
                pass
            sharedfilesstreams = shelve.open(os.path.join(self.data_dir, "streams.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if bsharedfilesstreams:
                bsharedfilesstreams.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'buddystreams.db'))
            except Exception:
                pass
            bsharedfilesstreams = shelve.open(os.path.join(self.data_dir, "buddystreams.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if wordindex:
                wordindex.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'wordindex.db'))
            except Exception:
                pass
            wordindex = shelve.open(os.path.join(self.data_dir, "wordindex.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if bwordindex:
                bwordindex.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'buddywordindex.db'))
            except Exception:
                pass
            bwordindex = shelve.open(os.path.join(self.data_dir, "buddywordindex.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if fileindex:
                fileindex.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'fileindex.db'))
            except Exception:
                pass
            fileindex = shelve.open(os.path.join(self.data_dir, "fileindex.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if bfileindex:
                bfileindex.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'buddyfileindex.db'))
            except Exception:
                pass
            bfileindex = shelve.open(os.path.join(self.data_dir, "buddyfileindex.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if sharedmtimes:
                sharedmtimes.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'mtimes.db'))
            except Exception:
                pass
            sharedmtimes = shelve.open(os.path.join(self.data_dir, "mtimes.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)

            if bsharedmtimes:
                bsharedmtimes.close()
            try:
                os.unlink(os.path.join(self.data_dir, 'buddymtimes.db'))
            except Exception:
                pass
            bsharedmtimes = shelve.open(os.path.join(self.data_dir, "buddymtimes.db"), flag='n', protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as error:
            log.addwarning(_("Error while writing database files: %s") % error)
            return None
        return sharedfiles, bsharedfiles, sharedfilesstreams, bsharedfilesstreams, wordindex, bwordindex, fileindex, bfileindex, sharedmtimes, bsharedmtimes