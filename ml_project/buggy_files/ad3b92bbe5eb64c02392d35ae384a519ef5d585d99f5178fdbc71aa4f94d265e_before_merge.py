    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            single = False
        else:
            single = True
            start = item
            stop = start + 1
            step = None

        if start is None:
            start = 0
        if stop is None:
            stop = self.size
        if step is None:
            step = 1

        stride = step * self.stride

        if start >= 0:
            start = self.start + start * self.stride
        else:
            start = self.stop + start * self.stride

        if stop >= 0:
            stop = self.start + stop * self.stride
        else:
            stop = self.stop + stop * self.stride

        size = (stop - start + (stride - 1)) // stride

        if self.start >= start >= self.stop:
            raise IndexError("start index out-of-bound")

        if self.start >= stop >= self.stop:
            raise IndexError("stop index out-of-bound")

        if stop < start:
            start = stop
            size = 0

        return Dim(start, stop, size, stride, single)