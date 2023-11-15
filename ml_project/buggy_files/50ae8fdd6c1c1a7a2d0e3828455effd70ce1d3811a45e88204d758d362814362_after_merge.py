    def stop(self):
        if self.resume_saving_task and not self.resume_saving_task.done():
            self.resume_saving_task.cancel()
        if self.re_reflect_task and not self.re_reflect_task.done():
            self.re_reflect_task.cancel()
        while self.streams:
            _, stream = self.streams.popitem()
            stream.stop_tasks()
        while self.update_stream_finished_futs:
            self.update_stream_finished_futs.pop().cancel()
        while self.running_reflector_uploads:
            _, t = self.running_reflector_uploads.popitem()
            t.cancel()
        self.started.clear()
        log.info("finished stopping the stream manager")