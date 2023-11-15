    def getGlobalData(self):
        '''Return a dict containing all global data.'''
        c = self.c
        data = c.db.get('window_position')
        if data:
            # pylint: disable=unpacking-non-sequence
            top, left, height, width = data
            d = {
                'top': int(top),
                'left': int(left),
                'height': int(height),
                'width': int(width),
            }
        else:
            # Use reasonable defaults.
            d = {'top': 50, 'left': 50, 'height': 500, 'width': 800}
        d ['r1'] = float(c.db.get('body_outline_ratio', '0.5'))
        d ['r2'] = float(c.db.get('body_secondary_ratio', '0.5'))
        return d