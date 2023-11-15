    def recent_events(self, events):
        frame = events.get('frame')
        if not frame:
            return
        if self.run:
            for i in range(len(self.workers)):
                if self.workers[i] and self.workers[i].is_alive():
                    pass
                else:
                    logger.info("starting new job")
                    if self.active_exports:
                        self.workers[i] = self.active_exports.pop(0)
                        if not self.workers[i].is_alive():
                            self.workers[i].start()
                    else:
                        self.run = False