    def __refresh_readonly(self, index):
        if self.data and len(self.data) > index:
            finfo = self.data[index]
            read_only = not QFileInfo(finfo.filename).isWritable()
            if not osp.isfile(finfo.filename):
                # This is an 'untitledX.py' file (newly created)
                read_only = False
            finfo.editor.setReadOnly(read_only)
            self.readonly_changed.emit(read_only)