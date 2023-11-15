    def to_clipboard(self, excel=None, sep=None, **kwargs):
        """
        Attempt to write text representation of object to the system clipboard
        This can be pasted into Excel, for example.

        Parameters
        ----------
        excel : boolean, defaults to True
                if True, use the provided separator, writing in a csv
                format for allowing easy pasting into excel.
                if False, write a string representation of the object
                to the clipboard
        sep : optional, defaults to tab
        other keywords are passed to to_csv

        Notes
        -----
        Requirements for your platform
          - Linux: xclip, or xsel (with gtk or PyQt4 modules)
          - Windows: none
          - OS X: none
        """
        from pandas.io import clipboards
        clipboards.to_clipboard(self, excel=excel, sep=sep, **kwargs)