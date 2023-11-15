    def get_frame(self, tt):

        buffersize = self.buffersize
        if isinstance(tt,np.ndarray):
            # lazy implementation, but should not cause problems in
            # 99.99 %  of the cases


            # elements of t that are actually in the range of the
            # audio file.
            in_time = (tt>=0) & (tt < self.duration)
		
	    # Check that the requested time is in the valid range
            if not in_time.any():
                raise IOError("Error in file %s, "%(self.filename)+
                       "Accessing time t=%.02f-%.02f seconds, "%(tt[0], tt[-1])+
                       "with clip duration=%d seconds, "%self.duration)

            # The np.round in the next line is super-important.
            # Removing it results in artifacts in the noise.
            frames = np.round((self.fps*tt)).astype(int)[in_time]
            fr_min, fr_max = frames.min(), frames.max()

            if not (0 <=
                     (fr_min - self.buffer_startframe)
                          < len(self.buffer)):
                self.buffer_around(fr_min)
            elif not (0 <=
                        (fr_max - self.buffer_startframe)
                             < len(self.buffer)):
                self.buffer_around(fr_max)

            try:
                result = np.zeros((len(tt),self.nchannels))
                indices = frames - self.buffer_startframe
                result[in_time] = self.buffer[indices]
                return result

            except IndexError as error:
                warnings.warn("Error in file %s, "%(self.filename)+
                       "At time t=%.02f-%.02f seconds, "%(tt[0], tt[-1])+
                       "indices wanted: %d-%d, "%(indices.min(), indices.max())+
                       "but len(buffer)=%d\n"%(len(self.buffer))+ str(error),
                   UserWarning)

                # repeat the last frame instead
                indices[indices>=len(self.buffer)] = len(self.buffer) -1
                result[in_time] = self.buffer[indices]
                return result

        else:

            ind = int(self.fps*tt)
            if ind<0 or ind> self.nframes: # out of time: return 0
                return np.zeros(self.nchannels)

            if not (0 <= (ind - self.buffer_startframe) <len(self.buffer)):
                # out of the buffer: recenter the buffer
                self.buffer_around(ind)

            # read the frame in the buffer
            return self.buffer[ind - self.buffer_startframe]