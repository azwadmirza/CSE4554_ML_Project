    def __new__(cls):
        if cls.__singleton is None:
            # We define the masked singleton as a float for higher precedence.
            # Note that it can be tricky sometimes w/ type comparison
            data = np.array(0.)
            mask = np.array(True)

            # prevent any modifications
            data.flags.writeable = False
            mask.flags.writeable = False

            # don't fall back on MaskedArray.__new__(MaskedConstant), since
            # that might confuse it - this way, the construction is entirely
            # within our control
            cls.__singleton = MaskedArray(data, mask=mask).view(cls)

        return cls.__singleton