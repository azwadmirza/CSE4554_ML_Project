    def update(self, chunk):
        """Update detection state from a chunk of audio data.

        Arguments:
            chunk (bytes): Audio data to parse
        """
        pcm = struct.unpack_from("h" * (len(chunk)//2), chunk)
        self.audio_buffer += pcm
        while True:
            if len(self.audio_buffer) >= self.porcupine.frame_length:
                result = self.porcupine.process(
                    self.audio_buffer[0:self.porcupine.frame_length])
                # result will be the index of the found keyword or -1 if
                # nothing has been found.
                self.has_found |= result >= 0
                self.audio_buffer = self.audio_buffer[
                    self.porcupine.frame_length:]
            else:
                return