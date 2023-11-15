    def validate_module(self, pipeline):
        if self.mode == MODE_UNTANGLE:
            if self.training_set_directory.dir_choice != cpprefs.URL_FOLDER_NAME:
                path = os.path.join(
                    self.training_set_directory.get_absolute_path(),
                    self.training_set_file_name.value)
                if not os.path.exists(path):
                    raise cps.ValidationError(
                        "Can't find file %s" % 
                        self.training_set_file_name.value,
                        self.training_set_file_name)