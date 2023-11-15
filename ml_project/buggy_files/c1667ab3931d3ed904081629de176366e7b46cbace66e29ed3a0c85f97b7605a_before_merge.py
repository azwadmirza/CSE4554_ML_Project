    def parse_file_as_json(self, myfile):
        try:
            content = json.loads(myfile["f"])
        except ValueError:
            log.warn('Could not parse file as json: {}'.format(myfile["fn"]))
            return
        runId = content["RunId"]
        if runId not in self.bcl2fastq_data:
            self.bcl2fastq_data[runId] = dict()
        run_data = self.bcl2fastq_data[runId]
        for conversionResult in content.get("ConversionResults", []):
            l = conversionResult["LaneNumber"]
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
            # simplify the population of dictionaries
            rlane = run_data[lane]

            # Add undetermined barcodes
            try:
                unknown_barcode = content['UnknownBarcodes'][l - 1]['Barcodes']
            except IndexError:
                unknown_barcode = next(
                    (item['Barcodes'] for item in content['UnknownBarcodes'] if item['Lane'] == 8),
                    None
                )
            run_data[lane]['unknown_barcodes'] = unknown_barcode

            for demuxResult in conversionResult.get("DemuxResults", []):
                if demuxResult["SampleName"] == demuxResult["SampleName"]:
                    sample = demuxResult["SampleName"]
                else:
                    sample = "{}-{}".format(demuxResult["SampleId"], demuxResult["SampleName"])
                if sample in run_data[lane]["samples"]:
                    log.debug("Duplicate runId/lane/sample combination found! Overwriting: {}, {}".format(self.prepend_runid(runId, lane), sample))
                run_data[lane]["samples"][sample] = {
                    "total": 0,
                    "total_yield": 0,
                    "perfectIndex": 0,
                    "filename": os.path.join(myfile['root'], myfile["fn"]),
                    "yieldQ30": 0,
                    "qscore_sum": 0,
                    "R1_yield": 0,
                    "R2_yield": 0,
                    "R1_Q30": 0,
                    "R2_Q30": 0,
                    "R1_trimmed_bases": 0,
                    "R2_trimmed_bases": 0
                }
                # simplify the population of dictionnaries
                lsample = run_data[lane]["samples"][sample]
                rlane["total"] += demuxResult["NumberReads"]
                rlane["total_yield"] += demuxResult["Yield"]
                lsample["total"] += demuxResult["NumberReads"]
                lsample["total_yield"] += demuxResult["Yield"]
                for indexMetric in demuxResult.get("IndexMetrics", []):
                    rlane["perfectIndex"] += indexMetric["MismatchCounts"]["0"]
                    lsample["perfectIndex"] += indexMetric["MismatchCounts"]["0"]
                for readMetric in demuxResult.get("ReadMetrics", []):
                    r = readMetric["ReadNumber"]
                    rlane["yieldQ30"] += readMetric["YieldQ30"]
                    rlane["qscore_sum"] += readMetric["QualityScoreSum"]
                    lsample["yieldQ30"] += readMetric["YieldQ30"]
                    lsample["qscore_sum"] += readMetric["QualityScoreSum"]
                    lsample["R{}_yield".format(r)] += readMetric["Yield"]
                    lsample["R{}_Q30".format(r)] += readMetric["YieldQ30"]
                    lsample["R{}_trimmed_bases".format(r)] += readMetric["TrimmedBases"]
            undeterminedYieldQ30 = 0
            undeterminedQscoreSum = 0
            undeterminedTrimmedBases = 0
            if "Undetermined" in conversionResult:
                for readMetric in conversionResult["Undetermined"]["ReadMetrics"]:
                    undeterminedYieldQ30 += readMetric["YieldQ30"]
                    undeterminedQscoreSum += readMetric["QualityScoreSum"]
                    undeterminedTrimmedBases += readMetric["TrimmedBases"]
                run_data[lane]["samples"]["undetermined"] = {
                    "total": conversionResult["Undetermined"]["NumberReads"],
                    "total_yield": conversionResult["Undetermined"]["Yield"],
                    "perfectIndex": 0,
                    "yieldQ30": undeterminedYieldQ30,
                    "qscore_sum": undeterminedQscoreSum,
                    "trimmed_bases": undeterminedTrimmedBases
                }

        # Calculate Percents and averages
        for lane_id, lane in run_data.items():
            try:
                lane["percent_Q30"] = (float(lane["yieldQ30"])
                    / float(lane["total_yield"])) * 100.0
            except ZeroDivisionError:
                lane["percent_Q30"] = "NA"
            try:
                lane["percent_perfectIndex"] = (float(lane["perfectIndex"])
                    / float(lane["total"])) * 100.0
            except ZeroDivisionError:
                lane["percent_perfectIndex"] = "NA"
            try:
                lane["mean_qscore"] = float(lane["qscore_sum"]) / float(lane["total_yield"])
            except ZeroDivisionError:
                lane["mean_qscore"] = "NA"
            for sample_id, sample in lane["samples"].items():
                try:
                    sample["percent_Q30"] = (float(sample["yieldQ30"])
                        / float(sample["total_yield"])) * 100.0
                except ZeroDivisionError:
                    sample["percent_Q30"] = "NA"
                try:
                    sample["percent_perfectIndex"] = (float(sample["perfectIndex"])
                        / float(sample["total"])) * 100.0
                except ZeroDivisionError:
                    sample["percent_perfectIndex"] = "NA"
                try:
                    sample["mean_qscore"] = float(sample["qscore_sum"]) / float(sample["total_yield"])
                except ZeroDivisionError:
                    sample["mean_qscore"] = "NA"