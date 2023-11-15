    def write(self, sequence, res, chunk_size=8192, retries=None):
        retries = retries or self.retries
        if retries == 0:
            self.logger.error("Failed to open segment {0}", sequence.num)
            return
        try:
            if sequence.segment.key and sequence.segment.key.method != "NONE":
                try:
                    decryptor = self.create_decryptor(sequence.segment.key,
                                                      sequence.num)
                except StreamError as err:
                    self.logger.error("Failed to create decryptor: {0}", err)
                    self.close()
                    return

                for chunk in res.iter_content(chunk_size):
                    # If the input data is not a multiple of 16, cut off any garbage
                    garbage_len = len(chunk) % 16
                    if garbage_len:
                        self.logger.debug("Cutting off {0} bytes of garbage "
                                          "before decrypting", garbage_len)
                        decrypted_chunk = decryptor.decrypt(chunk[:-garbage_len])
                    else:
                        decrypted_chunk = decryptor.decrypt(chunk)
                    self.reader.buffer.write(decrypted_chunk)
            else:
                for chunk in res.iter_content(chunk_size):
                    self.reader.buffer.write(chunk)
        except StreamError as err:
            self.logger.error("Failed to open segment {0}: {1}", sequence.num, err)
            return self.write(sequence,
                              self.fetch(sequence, retries=self.retries),
                              chunk_size=chunk_size,
                              retries=retries - 1)

        self.logger.debug("Download of segment {0} complete", sequence.num)