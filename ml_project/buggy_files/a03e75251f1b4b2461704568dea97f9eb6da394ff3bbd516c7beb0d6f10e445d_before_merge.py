    def close(self):
        log.debug("Closing ffmpeg thread")
        if self.process:
            # kill ffmpeg
            self.process.kill()
            self.process.stdout.close()

            # close the streams
            for stream in self.streams:
                if hasattr(stream, "close"):
                    stream.close()

            log.debug("Closed all the substreams")
        if self.close_errorlog:
            self.errorlog.close()
            self.errorlog = None