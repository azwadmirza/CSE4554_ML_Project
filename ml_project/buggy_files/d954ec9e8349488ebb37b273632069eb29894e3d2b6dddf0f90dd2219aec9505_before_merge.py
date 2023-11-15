    def pageChanged(self, event):
        """Event called when the user swtiches between editor tabs."""
        old = event.GetOldSelection()
        # close any auto-complete or calltips when swtiching pages
        if old != wx.NOT_FOUND:
            oldPage = self.notebook.GetPage(old)
            if hasattr(oldPage, 'CallTipActive'):
                if oldPage.CallTipActive():
                    oldPage.CallTipCancel()
                    oldPage.openBrackets = 0
            if hasattr(oldPage, 'AutoCompActive'):
                if oldPage.AutoCompActive():
                    oldPage.AutoCompCancel()

        new = event.GetSelection()
        self.currentDoc = self.notebook.GetPage(new)
        self.app.updateWindowMenu()
        self.setFileModified(self.currentDoc.UNSAVED)
        self.SetLabel('%s - PsychoPy Coder' % self.currentDoc.filename)

        self.currentDoc.analyseScript()

        fileType = self.currentDoc.getFileType()
        # enable run buttons if current file is a Python script
        if hasattr(self, 'cdrBtnRunner'):
            isExp = fileType == 'Python'
            self.toolbar.EnableTool(self.cdrBtnRunner.Id, isExp)
            self.toolbar.EnableTool(self.cdrBtnRun.Id, isExp)

        self.statusBar.SetStatusText(fileType, 2)

        # todo: reduce redundancy w.r.t OnIdle()
        if not self.expectedModTime(self.currentDoc):
            filename = os.path.basename(self.currentDoc.filename)
            msg = _translate("'%s' was modified outside of PsychoPy:\n\n"
                             "Reload (without saving)?") % filename
            dlg = dialogs.MessageDialog(self, message=msg, type='Warning')
            if dlg.ShowModal() == wx.ID_YES:
                self.statusBar.SetStatusText(_translate('Reloading file'))
                self.fileReload(event,
                                filename=self.currentDoc.filename,
                                checkSave=False)
                self.setFileModified(False)
            self.statusBar.SetStatusText('')
            dlg.Destroy()