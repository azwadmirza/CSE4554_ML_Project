        def _discover_or_abort(_first_result):
            self.log.debug(f"{self} learning at {datetime.datetime.now()}")
            result = self.learn_from_teacher_node(eager=False, canceller=self._discovery_canceller)
            self.log.debug(f"{self} finished learning at {datetime.datetime.now()}")
            return result