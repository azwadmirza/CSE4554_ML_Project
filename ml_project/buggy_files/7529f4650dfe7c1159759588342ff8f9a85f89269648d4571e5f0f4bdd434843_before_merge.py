    def validate_module(self, pipeline):
        '''Produce error if 'All:First' is selected and input image is not provided by the file image provider.'''
        if not pipeline.is_image_from_file(self.image_name.value) and self.each_or_all == EA_ALL_FIRST:
            raise cps.ValidationError(
                    "All: First cycle requires that the input image be provided by LoadImages or LoadData.",
                    self.each_or_all)
        
        '''Modify the image provider attributes based on other setttings'''
        d = self.illumination_image_name.provided_attributes
        if self.each_or_all == EA_ALL_ACROSS:
            d[cps.AVAILABLE_ON_LAST_ATTRIBUTE] = True
        elif d.has_key(cps.AVAILABLE_ON_LAST_ATTRIBUTE):
            del d[cps.AVAILABLE_ON_LAST_ATTRIBUTE]