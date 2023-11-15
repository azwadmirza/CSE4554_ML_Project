    def __or__(self, other):
        # These could be implemented in each individual class,
        # I'm sure, but for now we have this.
        if isinstance(self, group):
            if isinstance(other, group):
                # group() | group() -> single group
                return group(
                    itertools.chain(self.tasks, other.tasks), app=self.app)
            # group() | task -> chord
            return chord(self, body=other, app=self._app)
        elif isinstance(other, group):
            # unroll group with one member
            other = maybe_unroll_group(other)
            if isinstance(self, _chain):
                # chain | group() -> chain
                return _chain(seq_concat_item(
                    self.unchain_tasks(), other), app=self._app)
            # task | group() -> chain
            return _chain(self, other, app=self.app)

        if not isinstance(self, _chain) and isinstance(other, _chain):
            # task | chain -> chain
            return _chain(seq_concat_seq(
                (self,), other.unchain_tasks()), app=self._app)
        elif isinstance(other, _chain):
            # chain | chain -> chain
            return _chain(seq_concat_seq(
                self.unchain_tasks(), other.unchain_tasks()), app=self._app)
        elif isinstance(self, chord):
            # chord | task ->  attach to body
            sig = self.clone()
            sig.body = sig.body | other
            return sig
        elif isinstance(other, Signature):
            if isinstance(self, _chain):
                if self.tasks and isinstance(self.tasks[-1], group):
                    # CHAIN [last item is group] | TASK -> chord
                    sig = self.clone()
                    sig.tasks[-1] = chord(
                        sig.tasks[-1], other, app=self._app)
                    return sig
                elif self.tasks and isinstance(self.tasks[-1], chord):
                    # CHAIN [last item is chord] -> chain with chord body.
                    sig = self.clone()
                    sig.tasks[-1].body = sig.tasks[-1].body | other
                    return sig
                else:
                    # chain | task -> chain
                    return _chain(seq_concat_item(
                        self.unchain_tasks(), other), app=self._app)
            # task | task -> chain
            return _chain(self, other, app=self._app)
        return NotImplemented