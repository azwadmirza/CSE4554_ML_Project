    def upload_file(self, file_path):
        """
        :param file_path: file path to upload
        :return: json response / None
        """
        try:
            url = self.base_url + "scan"
            files = {
                'file': open(file_path, 'rb')
            }
            headers = {
                "apikey": settings.VT_API_KEY
            }
            try:
                proxies, verify = upstream_proxy('https')
            except:
                PrintException("Setting upstream proxy")
            try:
                response = requests.post(
                    url, files=files, data=headers, proxies=proxies, verify=verify)
                if response.status_code == 403:
                    logger.error("VirusTotal Permission denied, wrong api key?")
                    return None
            except:
                logger.error("VirusTotal Connection Error, check internet connectivity")
                return None
            json_response = response.json()
            return json_response

        except:
            PrintException("VirusTotal upload_file")
            return None