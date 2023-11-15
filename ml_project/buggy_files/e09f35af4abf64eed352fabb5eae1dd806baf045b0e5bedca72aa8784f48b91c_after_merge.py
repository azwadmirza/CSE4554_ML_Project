    def set(self, color=None, space=None):
        """Set the colour of this object - essentially the same as what happens on creation, but without
        having to initialise a new object"""
        if isinstance(color, numpy.ndarray):
            color = tuple(float(c) for c in color)
        if space in ['rgb255', 'rgba255']:
            color = tuple(int(c) for c in color[:3])+color[3:]
        if isinstance(color, (int, float)):
            color = (color, color, color)
        # If input is a Color object, duplicate all settings
        if isinstance(color, Color):
            self._requested = color._requested
            self._requestedSpace = color._requestedSpace
            self.rgba = color.rgba
            return
        # if supplied a named color, ignore color space
        if 'named' in self.getSpace(color, True):
            space = 'named'
        # Store requested colour and space (or defaults, if none given)
        self._requested = color if color is not None else None
        self._requestedSpace = space \
            if space and space in self.getSpace(self._requested, debug=True) \
            else self.getSpace(self._requested)
        if isinstance(self._requestedSpace, (list, type(None))):
            logging.error("Color space could not be determined by values supplied, please specify a color space.")
            return

        # Convert to lingua franca
        if self._requestedSpace:
            setattr(self, self._requestedSpace, self._requested)
        else:
            self.named = None