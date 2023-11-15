    def main_loop(self):
        if self.args.profile == -1:
            profile_file = None
        else:
            profile_file = self.args.profile or ('mars_' + self.__class__.__name__ + '.prof')
        try:
            if profile_file:
                import yappi
                yappi.set_clock_type('wall')
                yappi.start(builtins=False, profile_threads=False)

            with self.pool:
                try:
                    self.start()
                    self._running = True
                    while True:
                        self.pool.join(1)
                        stopped = []
                        for idx, proc in enumerate(self.pool.processes):
                            if not proc.is_alive():
                                stopped.append(idx)
                        if stopped:
                            self.handle_process_down(stopped)
                except:
                    self._running = False
                    self.stop()
        finally:
            self._running = False
            if profile_file:
                import yappi
                yappi.logger = logging.getLogger(__name__)
                p = yappi.convert2pstats(yappi.get_func_stats())
                p.strip_dirs()
                p.sort_stats('time')
                p.print_stats(40)
                p.dump_stats(profile_file)