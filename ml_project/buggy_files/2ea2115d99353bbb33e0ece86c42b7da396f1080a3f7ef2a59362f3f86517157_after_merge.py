    def update(self, stats):
        if stats.getCpu():
            # Update CSV with the CPU stats
            cpu = stats.getCpu()
            # Standard CPU stats
            cpu_line = ["cpu", cpu['user'], cpu['system'], cpu['nice']]
            # Extra CPU stats
            for key in ('idle', 'iowait', 'irq'):
                cpu_line.append(cpu[key] if key in cpu.keys() else None)
            self.__csvfile.writerow(cpu_line)
        if stats.getLoad():
            # Update CSV with the LOAD stats
            load = stats.getLoad()
            self.__csvfile.writerow(
                ["load", load['min1'], load['min5'], load['min15']])
        if stats.getMem() and stats.getMemSwap():
            # Update CSV with the MEM stats
            mem = stats.getMem()
            self.__csvfile.writerow(
                ["mem", mem['total'], mem['used'], mem['free']])
            memswap = stats.getMemSwap()
            self.__csvfile.writerow(
                ["swap", memswap['total'], memswap['used'], memswap['free']])
        self.__csvfile_fd.flush()