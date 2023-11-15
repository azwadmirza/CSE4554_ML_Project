    def reorder_filenames(self, filenames):
        """Take the last session filenames and put the last open on first.

        It takes a list of filenames and using the current filename from the 
        layout settings, sets the one that had focused last in the position 0. 
        It also reorders the current lines for each file (supposing that they 
        are in the same order as the filenames) and sets them back in the 
        layout settings.
        """
        layout = self.get_option('layout_settings', None)
        splitsettings = layout.get('splitsettings')
        index_first_file = 0
        reordered_splitsettings = []
        for index, (is_vertical, cfname, clines) in enumerate(splitsettings):
            #the first element of filenames is now the one that last had focus
            if index == 0:
                index_first_file = filenames.index(cfname)
                filenames.pop(index_first_file)
                filenames.insert(0, cfname)
            clines_0 = clines[0]
            clines.pop(index_first_file)
            clines.insert(0, clines_0)
            reordered_splitsettings.append((is_vertical, cfname, clines))
        layout['splitsettings'] = reordered_splitsettings
        self.set_option('layout_settings', layout)
        return filenames