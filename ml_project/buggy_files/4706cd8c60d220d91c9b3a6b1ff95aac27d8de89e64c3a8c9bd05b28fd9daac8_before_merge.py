    def open_external_file(self, fname):
        """
        Open external files that can be handled either by the Editor or the
        variable explorer inside Spyder.
        """
        fname = encoding.to_unicode_from_fs(fname)
        if osp.exists(osp.join(CWD, fname)):
            fpath = osp.join(CWD, fname)
        elif osp.exists(fname):
            fpath = fname
        else:
            return

        if osp.isfile(fpath):
            self.open_file(fpath, external=True)
        elif osp.isdir(fpath):
            QMessageBox.warning(
                self, _("Error"),
                _('To open <code>{fpath}</code> as a project with Spyder, '
                  'please use <code>spyder -p "{fname}"</code>.')
                .format(fpath=osp.normpath(fpath), fname=fname)
            )