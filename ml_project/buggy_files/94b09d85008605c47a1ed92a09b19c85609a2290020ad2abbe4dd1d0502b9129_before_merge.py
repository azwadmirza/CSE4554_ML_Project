    def _process_msg(self, msg):
        data = {}
        if 'x0' in msg and 'x1' in msg:
            x0, x1 = msg['x0'], msg['x1']
            if isinstance(self.plot.handles.get('xaxis'), DatetimeAxis):
                x0 = convert_timestamp(x0)
                x1 = convert_timestamp(x1)
            if self.plot.invert_xaxis:
                x0, x1 = x1, x0
            data['x_range'] = (x0, x1)
        if 'y0' in msg and 'y1' in msg:
            y0, y1 = msg['y0'], msg['y1']
            if isinstance(self.plot.handles.get('yaxis'), DatetimeAxis):
                y0 = convert_timestamp(y0)
                y1 = convert_timestamp(y1)
            if self.plot.invert_yaxis:
                y0, y1 = y1, y0
            data['y_range'] = (y0, y1)
        return self._transform(data)