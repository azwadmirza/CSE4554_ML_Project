    def declare(self, name, memory_type='BIT', memory_size=1, shared_region=None, offsets=None):
        """DECLARE a quil variable

        This adds the declaration to the current program and returns a MemoryReference to the
        base (offset = 0) of the declared memory.

        .. note::
            This function returns a MemoryReference and cannot be chained like some
            of the other Program methods. Consider using ``inst(DECLARE(...))`` if you
            would like to chain methods, but please be aware that you must create your
            own MemoryReferences later on.

        :param name: Name of the declared variable
        :param memory_type: Type of the declared variable
        :param memory_size: Number of array elements in the declared memory.
        :param shared_region: You can declare a variable that shares its underlying memory
            with another region. This allows aliasing. For example, you can interpret an array
            of measured bits as an integer.
        :param offsets: If you are using ``shared_region``, this allows you to share only
            a part of the parent region. The offset is given by an array type and the number
            of elements of that type. For example,
            ``DECLARE target-bit BIT SHARING real-region OFFSET 1 REAL 4 BIT`` will let you use
            target-bit to poke into the fourth bit of the second real from the leading edge of
            real-region.
        :return: a MemoryReference to the start of the declared memory region, ie a memory
            reference to ``name[0]``.
        """
        self.inst(Declare(name=name, memory_type=memory_type, memory_size=memory_size,
                          shared_region=shared_region, offsets=offsets))
        return MemoryReference(name=name, declared_size=memory_size)