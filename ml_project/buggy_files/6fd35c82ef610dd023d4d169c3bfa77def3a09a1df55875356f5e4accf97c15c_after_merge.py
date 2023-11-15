    def serialize(self, name, f):
        """

        :param name:
        :param f:
        :type f: file
        :return:
        """
        param = self.get(name)
        size = reduce(lambda a, b: a * b, param.shape)
        f.write(struct.pack("IIQ", 0, 4, size))
        param = param.astype(np.float32)
        f.write(param.tostring())