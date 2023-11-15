    def validate_module(self, pipeline):
        '''Keep users from using LoadSingleImage to define image sets'''
        if not any([x.is_load_module() for x in pipeline.modules()]):
            raise cps.ValidationError(
                "LoadSingleImage cannot be used to run a pipeline on one "
                "image file. Please use LoadImages or LoadData instead.",
                self.directory)
        
        '''Make sure metadata tags exist'''
        for group in self.file_settings:
            text_str = group.file_name.value
            undefined_tags = pipeline.get_undefined_metadata_tags(text_str)
            if len(undefined_tags) > 0:
                raise cps.ValidationError("%s is not a defined metadata tag. Check the metadata specifications in your load modules" %
                                 undefined_tags[0], 
                                 group.file_name)