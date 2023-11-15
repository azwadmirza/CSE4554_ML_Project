    def computeWorkbookFileName(self):
        """
        Return the name of the workbook.
        
        Return None *only* if:
        1. The workbook does not exist.
        2. We are unit testing or in batch mode.
        """
        # lm = self
        fn = g.app.config.getString(setting='default_leo_file')
            # The default is ~/.leo/workbook.leo
        if not fn:
            fn = g.os_path_finalize('~/.leo/workbook.leo')
        fn = g.os_path_finalize(fn)
        if not fn:
            return None
        if g.os_path_exists(fn):
            return fn
        if g.unitTesting or g.app.batchMode:
            # 2017/02/18: unit tests must not create a workbook.
            # Neither should batch mode operation.
            return None
        if g.os_path_isabs(fn):
            # Create the file.
            g.error('Using default leo file name:\n%s' % (fn))
            return fn
        # It's too risky to open a default file if it is relative.
        return None