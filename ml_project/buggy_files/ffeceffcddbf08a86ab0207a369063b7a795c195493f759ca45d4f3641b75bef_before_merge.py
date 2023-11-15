    def get_result(self, file_path, file_hash):
        """
        Uoloading a file and getting the approval msg from VT or fetching existing report
        :param file_path: file's path
        :param file_hash: file's hash - md5/sha1/sha256
        :return: VirusTotal result json / None upon error
        """
        try:
            logger.info("[INFO] VirusTotal: Check for existing report")
            report = self.get_report(file_hash)
            # Check for existing report
            if report:
                if report['response_code'] == 1:
                    logger.info("[INFO] VirusTotal: " + report['verbose_msg'])
                    return report
            if settings.VT_UPLOAD:
                logger.info("[INFO] VirusTotal: file upload")
                upload_response = self.upload_file(file_path)
                if upload_response:
                    logger.info("[INFO] VirusTotal: {}".format(upload_response['verbose_msg']))
                return upload_response
            else:
                logger.info("MobSF: VirusTotal Scan not performed as file upload is disabled in settings.py. "
                            "To enable file upload, set VT_UPLOAD to True.")
                report = {
                    "verbose_msg": "Scan Not performed, VirusTotal file upload disabled in settings.py", "positives": 0, "total": 0}
                return report
        except:
            PrintException("[ERROR] in VirusTotal get_result")