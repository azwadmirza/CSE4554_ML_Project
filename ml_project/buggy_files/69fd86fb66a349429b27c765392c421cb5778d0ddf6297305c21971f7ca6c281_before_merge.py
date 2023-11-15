    def validate_module(self,pipeline):
        """Make sure that the module's settings are consistent
        
        We need at least one image name to be filled in
        """
        if self.scheme_choice != SCHEME_STACK:
            if all([color_scheme_setting.image_name.is_blank
                    for color_scheme_setting in self.color_scheme_settings]):
                raise cps.ValidationError("At least one of the images must not be blank",\
                                              self.color_scheme_settings[0].image_name.value)