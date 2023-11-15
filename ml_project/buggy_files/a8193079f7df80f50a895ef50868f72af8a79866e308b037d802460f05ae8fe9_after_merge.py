    def run(self, workspace):
        '''Run on an image set'''
        image_name = self.image_name.value
        m = workspace.measurements
        #
        # Get the path and file names from the measurements
        #
        path = m.get_current_image_measurement('PathName_%s' % image_name)
        file_name = m.get_current_image_measurement('FileName_%s' % image_name)
        #
        # Pull out the prefix, middle and suffix from the file name
        #
        prefix = file_name[:self.number_characters_prefix.value]
        if self.number_characters_suffix.value == 0:
            suffix = ""
            middle = file_name[self.number_characters_prefix.value:]
        else:
            suffix = file_name[-self.number_characters_suffix.value:]
            middle = file_name[self.number_characters_prefix.value:
                               -self.number_characters_suffix.value]
        #
        # Possibly apply the renumbering rule
        #
        if self.action == A_RENUMBER:
            if not middle.isdigit():
                raise ValueError(
                    ('The middle of the filename, "%s", is "%s".\n'
                     "It has non-numeric characters and can't be "
                     "converted to a number") %
                    ( file_name, middle ))
            format = '%0'+str(self.number_digits.value)+'d'
            middle = format % int(middle)
        elif self.action == A_DELETE:
            middle = ""
        else:
            raise NotImplementedError("Unknown action: %s" % self.action.value)
        #
        # Possibly apply the added text
        #
        if self.wants_text:
            middle += self.text_to_add.value
        new_file_name = prefix + middle + suffix
        if self.wants_to_replace_spaces:
            new_file_name = new_file_name.replace(
                " ", self.space_replacement.value)
        if self.show_window:
            workspace.display_data.old_file_name = file_name
            workspace.display_data.new_file_name = new_file_name
        
        if workspace.pipeline.test_mode:
            return
        #
        # Perform the actual renaming
        #
        
        # Most likely, we have a handle on the file open in BioFormats
        from bioformats.formatreader import clear_image_reader_cache
        clear_image_reader_cache()
        os.rename(os.path.join(path, file_name),
                  os.path.join(path, new_file_name))