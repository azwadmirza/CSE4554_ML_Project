    def save_as(self, index=None):
        """Save file as...

        Args:
            index: self.data index for the file to save.

        Returns:
            False if no file name was selected or if save() was unsuccessful.
            True is save() was successful.

        Gets the new file name from select_savename().  If no name is chosen,
        then the save_as() aborts.  Otherwise, the current stack is checked
        to see if the selected name already exists and, if so, then the tab
        with that name is closed.

        The current stack (self.data) and current tabs are updated with the
        new name and other file info.  The text is written with the new
        name using save() and the name change is propagated to the other stacks
        via the file_renamed_in_data signal.
        """
        if index is None:
            # Save the currently edited file
            index = self.get_stack_index()
        finfo = self.data[index]
        # The next line is necessary to avoid checking if the file exists
        # While running __check_file_status
        # See spyder-ide/spyder#3678 and spyder-ide/spyder#3026.
        finfo.newly_created = True
        original_filename = finfo.filename
        filename = self.select_savename(original_filename)
        if filename:
            ao_index = self.has_filename(filename)
            # Note: ao_index == index --> saving an untitled file
            if ao_index is not None and ao_index != index:
                if not self.close_file(ao_index):
                    return
                if ao_index < index:
                    index -= 1

            new_index = self.rename_in_data(original_filename,
                                            new_filename=filename)

            # We pass self object ID as a QString, because otherwise it would
            # depend on the platform: long for 64bit, int for 32bit. Replacing
            # by long all the time is not working on some 32bit platforms
            # See spyder-ide/spyder#1094 and spyder-ide/spyder#1098.
            self.file_renamed_in_data.emit(str(id(self)),
                                           original_filename, filename)

            ok = self.save(index=new_index, force=True)
            self.refresh(new_index)
            self.set_stack_index(new_index)
            return ok
        else:
            finfo.newly_created = False
            return False