    def end_parallel_control_flow_block(
            self, code, break_=False, continue_=False, return_=False):
        """
        This ends the parallel control flow block and based on how the parallel
        section was exited, takes the corresponding action. The break_ and
        continue_ parameters indicate whether these should be propagated
        outwards:

            for i in prange(...):
                with cython.parallel.parallel():
                    continue

        Here break should be trapped in the parallel block, and propagated to
        the for loop.
        """
        c = self.begin_of_parallel_control_block_point

        # Firstly, always prefer errors over returning, continue or break
        if self.error_label_used:
            c.putln("const char *%s = NULL; int %s = 0, %s = 0;" % self.parallel_pos_info)
            c.putln("PyObject *%s = NULL, *%s = NULL, *%s = NULL;" % self.parallel_exc)

            code.putln(
                "if (%s) {" % Naming.parallel_exc_type)
            code.putln("/* This may have been overridden by a continue, "
                       "break or return in another thread. Prefer the error. */")
            code.putln("%s = 4;" % Naming.parallel_why)
            code.putln(
                "}")

        if continue_:
            any_label_used = self.any_label_used
        else:
            any_label_used = self.breaking_label_used

        if any_label_used:
            # __pyx_parallel_why is used, declare and initialize
            c.putln("int %s;" % Naming.parallel_why)
            c.putln("%s = 0;" % Naming.parallel_why)

            code.putln(
                "if (%s) {" % Naming.parallel_why)

            for temp_cname, private_cname in self.parallel_private_temps:
                code.putln("%s = %s;" % (private_cname, temp_cname))

            code.putln("switch (%s) {" % Naming.parallel_why)
            if continue_:
                code.put("    case 1: ")
                code.put_goto(code.continue_label)

            if break_:
                code.put("    case 2: ")
                code.put_goto(code.break_label)

            if return_:
                code.put("    case 3: ")
                code.put_goto(code.return_label)

            if self.error_label_used:
                code.globalstate.use_utility_code(restore_exception_utility_code)
                code.putln("    case 4:")
                self.restore_parallel_exception(code)
                code.put_goto(code.error_label)

            code.putln("}") # end switch
            code.putln(
                "}") # end if

        code.end_block() # end parallel control flow block
        self.redef_builtin_expect_apple_gcc_bug(code)