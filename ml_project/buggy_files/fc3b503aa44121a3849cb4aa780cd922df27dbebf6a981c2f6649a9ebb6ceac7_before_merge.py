    def __init__(self, start, stop, size, stride, single):
        if stop < start:
            raise ValueError("end offset is before start offset")
        self.start = start
        self.stop = stop
        self.size = size
        self.stride = stride
        self.single = single
        assert not single or size == 1