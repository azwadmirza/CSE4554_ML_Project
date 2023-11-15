    def _get_microscope_name(self, ImageTags):
        try:
            if ImageTags.Session_Info.Microscope != "[]":
                return ImageTags.Session_Info.Microscope
        except AttributeError:
            return ImageTags.Microscope_Info.Name