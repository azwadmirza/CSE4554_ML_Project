    def need_update(self):
        if self.updater:
            return self.updater.need_update()