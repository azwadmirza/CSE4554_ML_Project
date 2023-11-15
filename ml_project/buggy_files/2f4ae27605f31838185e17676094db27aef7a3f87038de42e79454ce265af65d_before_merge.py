    def ticker(self, *userdata):
        changed = self.tick(self.masterq, timeout=0)
        if changed:
            self.loop.draw_screen()
            signals.update_settings.send()
        self.loop.set_alarm_in(0.01, self.ticker)