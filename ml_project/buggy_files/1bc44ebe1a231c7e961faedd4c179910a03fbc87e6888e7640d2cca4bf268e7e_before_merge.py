    def get_report(self, file_hash):
        """
        :param file_hash: md5/sha1/sha256
        :return: json response / None
        """
        try:
            url = self.base_url + 'report'
            params = {
                'apikey': settings.VT_API_KEY,
                'resource': file_hash
            }
            headers = {"Accept-Encoding": "gzip, deflate"}
            try:
                proxies, verify = upstream_proxy('https')
            except:
                PrintException("[ERROR] Setting upstream proxy")
            try:
                response = requests.get(
                    url, params=params, headers=headers, proxies=proxies, verify=verify)
                if response.status_code == 403:
                    logger.error("VirusTotal Permission denied, wrong api key?")
                    return None
            except:
                logger.error("VirusTotal ConnectionError, check internet connectivity")
                return None
            try:
                json_response = response.json()
                return json_response
            except ValueError:
                return None
        except:
            PrintException("[ERROR] in VirusTotal get_report")
            return None