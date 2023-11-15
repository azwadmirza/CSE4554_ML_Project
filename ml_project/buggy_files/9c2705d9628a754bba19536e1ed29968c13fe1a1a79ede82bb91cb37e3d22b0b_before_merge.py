    def default(self, line):
        """Implements code execution."""
        line = line if line.endswith('\n') else line + '\n'
        src, code = self.push(line)
        if code is None:
            return
        hist = builtins.__xonsh_history__  # pylint: disable=no-member
        ts1 = None
        store_stdout = builtins.__xonsh_env__.get('XONSH_STORE_STDOUT')  # pylint: disable=no-member
        tee = Tee() if store_stdout else io.StringIO()
        try:
            ts0 = time.time()
            run_compiled_code(code, self.ctx, None, 'single')
            ts1 = time.time()
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 0  # returncode for success
        except XonshError as e:
            print(e.args[0], file=sys.stderr)
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 1  # return code for failure
        except Exception:  # pylint: disable=broad-except
            print_exception()
            if hist.last_cmd_rtn is None:
                hist.last_cmd_rtn = 1  # return code for failure
        finally:
            ts1 = ts1 or time.time()
            self._append_history(inp=src, ts=[ts0, ts1], tee_out=tee.getvalue())
            tee.close()
            builtins.__xonsh_env__['PWD'] = os.getcwd()        # track any change in working directory
        if builtins.__xonsh_exit__:  # pylint: disable=no-member
            return True