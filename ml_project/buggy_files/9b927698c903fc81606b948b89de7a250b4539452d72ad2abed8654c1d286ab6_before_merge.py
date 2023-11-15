    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            single = False
        else:
            single = True
            start = item
            stop = start + 1
            step = None

        # Default values
        #   Start value is default to zero
        if start is None:
            start = 0
        #   Stop value is default to self.size
        if stop is None:
            stop = self.size
        #   Step is default to 1
        if step is None:
            step = 1

        stride = step * self.stride

        # Compute start in bytes
        if start >= 0:
            start = self.start + start * self.stride
        else:
            start = self.stop + start * self.stride
        start = max(start, self.start)

        # Compute stop in bytes
        if stop >= 0:
            stop = self.start + stop * self.stride
        else:
            stop = self.stop + stop * self.stride
        stop = min(stop, self.stop)

        # Clip stop
        if (stop - start) > self.size * self.stride:
            stop = start + self.size * stride

        if stop < start:
            start = stop
            size = 0
        elif stride == 0:
            size = 1 if single else ((stop - start) // step)
        else:
            size = (stop - start + (stride - 1)) // stride

        return Dim(start, stop, size, stride, single)