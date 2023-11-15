    def get_file_url(self):
        """ returns the absolute downloadable filepath
        """
        url = multiply = modulo = None

        found = re.search(self.DOWNLOAD_URL_PATTERN, self.html, re.S)
        if found:
            #Method #1: JS eval
            js = "\n".join(found.groups())
            regex = r"document.getElementById\(\\*'dlbutton\\*'\).omg"
            omg = re.search(regex + r" = ([^;]+);", js).group(1)
            js = re.sub(regex + r" = ([^;]+);", '', js)
            js = re.sub(regex, omg, js)
            url = self.js.eval(js)
        else:
            #Method #2: SWF eval
            seed_search = re.search(self.SEED_PATTERN, self.html)
            if seed_search:
                swf_url, file_seed = seed_search.groups()

                swf_sts = self.getStorage("swf_sts")
                swf_stamp = int(self.getStorage("swf_stamp") or 0)
                swf_version = self.getStorage("version")
                self.logDebug("SWF", swf_sts, swf_stamp, swf_version)

                if not swf_sts:
                    self.logDebug('Using default values')
                    multiply, modulo = self.LAST_KNOWN_VALUES
                elif swf_sts == "1":
                    self.logDebug('Using stored values')
                    multiply = self.getStorage("multiply")
                    modulo = self.getStorage("modulo")
                elif swf_sts == "2":
                    if swf_version < self.__version__:
                        self.logDebug('Reverting to default values')
                        self.setStorage("swf_sts", "")
                        self.setStorage("version", self.__version__)
                        multiply, modulo = self.LAST_KNOWN_VALUES
                    elif (swf_stamp + 3600000) < timestamp():
                        swfdump = self.get_swfdump_path()
                        if swfdump:
                            multiply, modulo = self.get_swf_values(self.file_info['HOST'] + swf_url, swfdump)
                        else:
                            self.logWarning("Swfdump not found. Install swftools to bypass captcha.")

                if multiply and modulo:
                    self.logDebug("TIME = (%s * %s) %s" % (file_seed, multiply, modulo))
                    url = "/download?key=%s&time=%d" % (self.file_info['KEY'],
                                                        (int(file_seed) * int(multiply)) % int(modulo))

            if not url:
                #Method #3: Captcha
                url = self.do_recaptcha()

        return self.file_info['HOST'] + url