    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.indices(self.size)
            stride = step * self.stride
            start = self.start + start * abs(self.stride)
            stop = self.start + stop * abs(self.stride)
            if stride == 0:
                size = 1
            else:
                size = _compute_size(start, stop, stride)
            ret = Dim(
                start=start,
                stop=stop,
                size=size,
                stride=stride,
                single=False
            )
            return ret
        else:
            sliced = self[item:item + 1]
            if sliced.size != 1:
                raise IndexError
            return Dim(
                start=sliced.start,
                stop=sliced.stop,
                size=sliced.size,
                stride=sliced.stride,
                single=True,
            )