    def __call__(self, *args, **kwargs):
        """Call the compositor."""
        from satpy import Scene
        # Check if filename exists, if not then try from SATPY_ANCPATH
        if (not os.path.isfile(self.filename)):
            tmp_filename = os.path.join(get_environ_ancpath(), self.filename)
            if (os.path.isfile(tmp_filename)):
                self.filename = tmp_filename
        scn = Scene(reader='generic_image', filenames=[self.filename])
        scn.load(['image'])
        img = scn['image']
        # use compositor parameters as extra metadata
        # most important: set 'name' of the image
        img.attrs.update(self.attrs)
        # Check for proper area definition.  Non-georeferenced images
        # do not have `area` in the attributes
        if 'area' not in img.attrs:
            if self.area is None:
                raise AttributeError("Area definition needs to be configured")
            img.attrs['area'] = self.area
        img.attrs['sensor'] = None
        img.attrs['mode'] = ''.join(img.bands.data)
        img.attrs.pop('modifiers', None)
        img.attrs.pop('calibration', None)
        # Add start time if not present in the filename
        if 'start_time' not in img.attrs or not img.attrs['start_time']:
            import datetime as dt
            img.attrs['start_time'] = dt.datetime.utcnow()
        if 'end_time' not in img.attrs or not img.attrs['end_time']:
            import datetime as dt
            img.attrs['end_time'] = dt.datetime.utcnow()

        return img