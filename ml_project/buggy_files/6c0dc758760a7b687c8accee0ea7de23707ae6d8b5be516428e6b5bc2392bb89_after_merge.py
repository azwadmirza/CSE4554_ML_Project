    def process(self):
        event = self.receive_message()
        procedure = Procedure.CONTINUE
        if self.sieve:  # empty rules file results in empty string
            for rule in self.sieve.rules:
                procedure = self.process_rule(rule, event)
                if procedure == Procedure.KEEP:
                    self.logger.debug('Stop processing based on rule at %s: %s.', self.get_linecol(rule), event)
                    break
                elif procedure == Procedure.DROP:
                    self.logger.debug('Dropped event based on rule at %s: %s.', self.get_linecol(rule), event)
                    break

        # forwarding decision
        if procedure != Procedure.DROP:
            path = getattr(event, "path", "_default")
            self.send_message(event, path=path)

        self.acknowledge_message()