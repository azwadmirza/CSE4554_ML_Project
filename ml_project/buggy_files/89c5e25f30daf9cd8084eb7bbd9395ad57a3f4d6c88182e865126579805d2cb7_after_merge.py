    def parse_file_as_json(self, myfile):
        try:
            content = json.loads(myfile["f"])
        except ValueError:
            log.warn('Could not parse file as json: {}'.format(myfile["fn"]))
            return
        runId = content["RunId"]
        if not runId in self.bcl2fastq_data:
            self.bcl2fastq_data[runId] = dict()
        run_data = self.bcl2fastq_data[runId]
        for conversionResult in content.get("ConversionResults", []):
            lane = 'L{}'.format(conversionResult["LaneNumber"])
            if lane in run_data:
                log.debug("Duplicate runId/lane combination found! Overwriting: {}".format(self.prepend_runid(runId, lane)))
            run_data[lane] = {
                "total": 0,
                "total_yield": 0,
                "perfectIndex": 0,
                "samples": dict(),
                "yieldQ30": 0,
                "qscore_sum": 0
            }
            for demuxResult in conversionResult.get("DemuxResults", []):
                sample = demuxResult["SampleName"]
                if sample in run_data[lane]["samples"]:
                    log.debug("Duplicate runId/lane/sample combination found! Overwriting: {}, {}".format(self.prepend_runid(runId, lane),sample))
                run_data[lane]["samples"][sample] = {
                    "total": 0,
                    "total_yield": 0,
                    "perfectIndex": 0,
                    "filename": os.path.join(myfile['root'],myfile["fn"]),
                    "yieldQ30": 0,
                    "qscore_sum": 0
                }
                run_data[lane]["total"] += demuxResult["NumberReads"]
                run_data[lane]["total_yield"] += demuxResult["Yield"]
                run_data[lane]["samples"][sample]["total"] += demuxResult["NumberReads"]
                run_data[lane]["samples"][sample]["total_yield"] += demuxResult["Yield"]
                if "IndexMetrics" in demuxResult:
                    for indexMetric in demuxResult["IndexMetrics"]:
                        run_data[lane]["perfectIndex"] += indexMetric["MismatchCounts"]["0"]
                        run_data[lane]["samples"][sample]["perfectIndex"] += indexMetric["MismatchCounts"]["0"]
                for readMetric in demuxResult.get("ReadMetrics", []):
                    run_data[lane]["yieldQ30"] += readMetric["YieldQ30"]
                    run_data[lane]["qscore_sum"] += readMetric["QualityScoreSum"]
                    run_data[lane]["samples"][sample]["yieldQ30"] += readMetric["YieldQ30"]
                    run_data[lane]["samples"][sample]["qscore_sum"] += readMetric["QualityScoreSum"]
            undeterminedYieldQ30 = 0
            undeterminedQscoreSum = 0
            if "Undetermined" in conversionResult:
                for readMetric in conversionResult["Undetermined"]["ReadMetrics"]:
                    undeterminedYieldQ30 += readMetric["YieldQ30"]
                    undeterminedQscoreSum += readMetric["QualityScoreSum"]
                run_data[lane]["samples"]["undetermined"] = {
                    "total": conversionResult["Undetermined"]["NumberReads"],
                    "total_yield": conversionResult["Undetermined"]["Yield"],
                    "perfectIndex": 0,
                    "yieldQ30": undeterminedYieldQ30,
                    "qscore_sum": undeterminedQscoreSum
                }

        # Calculate Percents and averages
        for lane in run_data:
            run_data[lane]["percent_Q30"] = (float(run_data[lane]["yieldQ30"]) / float(run_data[lane]["total_yield"])) * 100.0
            run_data[lane]["percent_perfectIndex"] = (float(run_data[lane]["perfectIndex"]) / float(run_data[lane]["total"])) * 100.0
            run_data[lane]["mean_qscore"] = float(run_data[lane]["qscore_sum"]) / float(run_data[lane]["total_yield"])
            for sample, d in run_data[lane]["samples"].items():
                run_data[lane]["samples"][sample]["percent_Q30"] = (float(d["yieldQ30"]) / float(d["total_yield"])) * 100.0
                run_data[lane]["samples"][sample]["percent_perfectIndex"] = (float(d["perfectIndex"]) / float(d["total"])) * 100.0
                run_data[lane]["samples"][sample]["mean_qscore"] = float(d["qscore_sum"]) / float(d["total_yield"])