    def __update(self):
        """
        Load the IRQ file and update the internal dict
        """

        self.reset()

        if not os.path.exists(self.IRQ_FILE):
            # Correct issue #947: IRQ file do not exist on OpenVZ container
            return self.stats

        with open(self.IRQ_FILE) as irq_proc:
            time_since_update = getTimeSinceLastUpdate('irq')
            # Read the header
            self.__header(irq_proc.readline())
            # Read the rest of the lines (one line per IRQ)
            for line in irq_proc.readlines():
                irq_line = self.__humanname(line)
                current_irqs = self.__sum(line)
                irq_rate = int(
                    current_irqs -
                    self.lasts.get(irq_line) if self.lasts.get(irq_line) else 0 //
                    time_since_update)
                irq_current = {
                    'irq_line': irq_line,
                    'irq_rate': irq_rate,
                    'key': self.get_key(),
                    'time_since_update': time_since_update
                }
                self.stats.append(irq_current)
                self.lasts[irq_line] = current_irqs

        return self.stats