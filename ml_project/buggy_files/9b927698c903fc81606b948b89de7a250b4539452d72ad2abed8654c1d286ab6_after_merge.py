    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.indices(self.size)
            stride = step * self.stride
            start = self.start + start * abs(self.stride)
            stop = self.start + stop * abs(self.stride)
            if stride == 0:
                size = 1
            else:
                size = (stop - start + (stride - 1)) // stride
            if size < 0:
                size = 0
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
            return Dim(
                start=sliced.start,
                stop=sliced.stop,
                size=sliced.size,
                stride=sliced.stride,
                single=True,
            )