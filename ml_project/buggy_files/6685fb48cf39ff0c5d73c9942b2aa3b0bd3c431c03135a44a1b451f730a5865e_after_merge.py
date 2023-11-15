    def computeWorkbookFileName(self):
        """
        Return full path to the workbook.
        
        Return None if testing, or in batch mode, or if the containing
        directory does not exist.
        """
        # lm = self
        # Never create a workbook during unit tests or in batch mode.
        if g.unitTesting or g.app.batchMode:
            return None
        fn = g.app.config.getString(setting='default_leo_file') or '~/.leo/workbook.leo'
        fn = g.os_path_finalize(fn)
        directory = g.os_path_finalize(os.path.dirname(fn))
        # #1415.
        return fn if os.path.exists(directory) else None