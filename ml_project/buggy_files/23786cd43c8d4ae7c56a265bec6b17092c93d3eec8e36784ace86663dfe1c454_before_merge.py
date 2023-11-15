    def stop(self):
        """Stops logging and closes the file."""
        if self.fp.closed:
            return
        self._flush()
        filesize = self.fp.tell()
        self.fp.close()

        # Write header in the beginning of the file
        header = [b"LOGG", FILE_HEADER_STRUCT.size,
                  APPLICATION_ID, 0, 0, 0, 2, 6, 8, 1]
        # The meaning of "count of objects read" is unknown
        header.extend([filesize, self.uncompressed_size,
                       self.count_of_objects, 0])
        header.extend(timestamp_to_systemtime(self.start_timestamp))
        header.extend(timestamp_to_systemtime(self.stop_timestamp))
        with open(self.fp.name, "r+b") as f:
            f.write(FILE_HEADER_STRUCT.pack(*header))