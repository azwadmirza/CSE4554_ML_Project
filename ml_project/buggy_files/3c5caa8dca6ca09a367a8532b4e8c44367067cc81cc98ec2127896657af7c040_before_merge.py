    def privatize_temps(self, code, exclude_temps=()):
        """
        Make any used temporaries private. Before the relevant code block
        code.start_collecting_temps() should have been called.
        """
        if self.is_parallel:
            c = self.privatization_insertion_point

            self.temps = temps = code.funcstate.stop_collecting_temps()
            privates, firstprivates = [], []
            for temp, type in sorted(temps):
                if type.is_pyobject or type.is_memoryviewslice:
                    firstprivates.append(temp)
                else:
                    privates.append(temp)

            if privates:
                c.put(" private(%s)" % ", ".join(privates))
            if firstprivates:
                c.put(" firstprivate(%s)" % ", ".join(firstprivates))

            if self.breaking_label_used:
                shared_vars = [Naming.parallel_why]
                if self.error_label_used:
                    shared_vars.extend(self.parallel_exc)
                    c.put(" private(%s, %s, %s)" % self.pos_info)

                c.put(" shared(%s)" % ', '.join(shared_vars))