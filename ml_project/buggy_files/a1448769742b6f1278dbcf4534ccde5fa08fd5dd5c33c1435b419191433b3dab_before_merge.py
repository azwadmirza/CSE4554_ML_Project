    def next(self):
        '''
        Return the next iteration by popping `chunk_size` from the left and
        appending `chunk_size` to the right if there's info on the file left
        to be read.
        '''
        if self.__buffered is None:
            # Use floor division to force multiplier to an integer
            multiplier = self.__max_in_mem // self.__chunk_size
            self.__buffered = ""
        else:
            multiplier = 1
            self.__buffered = self.__buffered[self.__chunk_size:]

        if six.PY3:
            # Data is a byte object in Python 3
            # Decode it in order to append to self.__buffered str later
            data = self.__file.read(self.__chunk_size * multiplier).decode(
                __salt_system_encoding__
            )
        else:
            data = self.__file.read(self.__chunk_size * multiplier)

        if not data:
            self.__file.close()
            raise StopIteration

        self.__buffered += data
        return self.__buffered