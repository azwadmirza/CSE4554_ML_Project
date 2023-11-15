    def update(self, chunk):
        pcm = struct.unpack_from("h" * (len(chunk)//2), chunk)
        self.audio_buffer += pcm
        while True:
            if len(self.audio_buffer) >= self.porcupine.frame_length:
                result = self.porcupine.process(
                    self.audio_buffer[0:self.porcupine.frame_length])
                # result could be boolean (if there is one keword)
                # or int (if more than one keyword)
                self.has_found |= (
                    (self.num_keywords == 1 and result) |
                    (self.num_keywords > 1 and result >= 0))
                self.audio_buffer = self.audio_buffer[
                    self.porcupine.frame_length:]
            else:
                return