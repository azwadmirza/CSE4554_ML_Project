    def split_data_by_lane_and_sample(self):
        for runId in self.bcl2fastq_data.keys():
            for lane in self.bcl2fastq_data[runId].keys():
                uniqLaneName = self.prepend_runid(runId, lane)
                self.bcl2fastq_bylane[uniqLaneName] = {
                    "total": self.bcl2fastq_data[runId][lane]["total"],
                    "total_yield": self.bcl2fastq_data[runId][lane]["total_yield"],
                    "perfectIndex": self.bcl2fastq_data[runId][lane]["perfectIndex"],
                    "undetermined": self.bcl2fastq_data[runId][lane]["samples"]["undetermined"]["total"],
                    "yieldQ30": self.bcl2fastq_data[runId][lane]["yieldQ30"],
                    "qscore_sum": self.bcl2fastq_data[runId][lane]["qscore_sum"],
                    "percent_Q30": self.bcl2fastq_data[runId][lane]["percent_Q30"],
                    "percent_perfectIndex": self.bcl2fastq_data[runId][lane]["percent_perfectIndex"],
                    "mean_qscore": self.bcl2fastq_data[runId][lane]["mean_qscore"]
                }
                for sample in self.bcl2fastq_data[runId][lane]["samples"].keys():
                    if not sample in self.bcl2fastq_bysample:
                        self.bcl2fastq_bysample[sample] = {
                            "total": 0,
                            "total_yield": 0,
                            "perfectIndex": 0,
                            "yieldQ30": 0,
                            "qscore_sum": 0
                        }
                    self.bcl2fastq_bysample[sample]["total"] += self.bcl2fastq_data[runId][lane]["samples"][sample]["total"]
                    self.bcl2fastq_bysample[sample]["total_yield"] += self.bcl2fastq_data[runId][lane]["samples"][sample]["total_yield"]
                    self.bcl2fastq_bysample[sample]["perfectIndex"] += self.bcl2fastq_data[runId][lane]["samples"][sample]["perfectIndex"]
                    self.bcl2fastq_bysample[sample]["yieldQ30"] += self.bcl2fastq_data[runId][lane]["samples"][sample]["yieldQ30"]
                    self.bcl2fastq_bysample[sample]["qscore_sum"] += self.bcl2fastq_data[runId][lane]["samples"][sample]["qscore_sum"]
                    self.bcl2fastq_bysample[sample]["percent_Q30"] = (float(self.bcl2fastq_bysample[sample]["yieldQ30"]) / float(self.bcl2fastq_bysample[sample]["total_yield"])) * 100.0
                    self.bcl2fastq_bysample[sample]["percent_perfectIndex"] = (float(self.bcl2fastq_bysample[sample]["perfectIndex"]) / float(self.bcl2fastq_bysample[sample]["total"])) * 100.0
                    self.bcl2fastq_bysample[sample]["mean_qscore"] = float(self.bcl2fastq_bysample[sample]["qscore_sum"]) / float(self.bcl2fastq_bysample[sample]["total_yield"])
                    if sample != "undetermined":
                        if not sample in self.source_files:
                            self.source_files[sample] = []
                        self.source_files[sample].append(self.bcl2fastq_data[runId][lane]["samples"][sample]["filename"])