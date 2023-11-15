    def run(self, **kwargs):
        """Analyze trajectory and produce timeseries"""
        h_list = []
        i = 0
        if (self.nproc > 1):
            while i < len(self.universe.trajectory):
                jobs = []
                k = i
                for j in range(self.nproc):
                    # start
                    print("ts=", i + 1)
                    if i >= len(self.universe.trajectory):
                        break
                    conn_parent, conn_child = multiprocessing.Pipe(False)
                    while True:
                        try:
                            # new thread
                            jobs.append(
                                (multiprocessing.Process(
                                    target=self._HBA,
                                    args=(self.universe.trajectory[i],
                                          conn_child, self.universe,
                                          self.selection1, self.selection2,)),
                                 conn_parent))
                            break
                        except:
                            print("error in jobs.append")
                    jobs[j][0].start()
                    i = i + 1

                for j in range(self.nproc):
                    if k >= len(self.universe.trajectory):
                        break
                    rec01 = jobs[j][1]
                    received = rec01.recv()
                    h_list.append(received)
                    jobs[j][0].join()
                    k += 1
            self.timeseries = self._getGraphics(
                h_list, 0, self.tf - 1, self.dtmax)
        else:
            h_list = MDAnalysis.analysis.hbonds.HydrogenBondAnalysis(self.universe,
                                                                     self.selection1,
                                                                     self.selection2,
                                                                     distance=3.5,
                                                                     angle=120.0)
            h_list.run(**kwargs)
            self.timeseries = self._getGraphics(
                h_list.timeseries, self.t0, self.tf, self.dtmax)