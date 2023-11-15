    def check_pid(self, pid):
        if os.name == 'nt':
            try:
                import ctypes
                # returns 0 if no such process (of ours) exists
                # positive int otherwise
                p = ctypes.windll.kernel32.OpenProcess(1,0,pid)
            except Exception:
                self.log.warn(
                    "Could not determine whether pid %i is running via `OpenProcess`. "
                    " Making the likely assumption that it is."%pid
                )
                return True
            return bool(p)
        else:
            try:
                p = Popen(['ps','x'], stdout=PIPE, stderr=PIPE)
                output,_ = p.communicate()
            except OSError:
                self.log.warn(
                    "Could not determine whether pid %i is running via `ps x`. "
                    " Making the likely assumption that it is."%pid
                )
                return True
            pids = list(map(int, re.findall(br'^\W*\d+', output, re.MULTILINE)))
            return pid in pids