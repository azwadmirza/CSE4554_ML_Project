    def OnSave(self, widget):
        sharesdir = os.path.join(self.data_dir, "usershares")

        try:
            if not os.path.exists(sharesdir):
                os.mkdir(sharesdir)
        except Exception as msg:
            error = _("Can't create directory '%(folder)s', reported error: %(error)s" % {'folder': sharesdir, 'error': msg})
            self.frame.logMessage(error)

        try:
            import pickle as mypickle
            import bz2
            sharesfile = bz2.BZ2File(os.path.join(sharesdir, CleanFile(self.user)), 'w')
            mypickle.dump(self.shares, sharesfile, mypickle.HIGHEST_PROTOCOL)
            sharesfile.close()
        except Exception as msg:
            error = _("Can't save shares, '%(user)s', reported error: %(error)s" % {'user': self.user, 'error': msg})
            self.frame.logMessage(error)