    def get_file_url(self):
        """ returns the absolute downloadable filepath
        """
        url = None

        found = re.search(self.DOWNLOAD_URL_PATTERN, self.html, re.S)
        #Method #1: JS eval
        if found and re.search(r'span id="omg" class="(\d*)"', self.html):
            js = "\n".join(found.groups())
            d = re.search(r'span id="omg" class="(\d*)"', self.html).group(1)
            regex = r"document.getElementById\('omg'\).getAttribute\('class'\)"
            js = re.sub(regex, d, js)
            regex = r"document.getElementById\(\\*'dlbutton\\*'\).href = "
            js = re.sub(regex, '', js)
            url = self.js.eval(js)
        elif found and re.search(r"document.getElementById\(\\*'dlbutton\\*'\).omg", self.html):
            js = "\n".join(found.groups())
            regex = r"document.getElementById\(\\*'dlbutton\\*'\).omg"
            omg = re.search(regex + r" = ([^;]+);", js).group(1)
            js = re.sub(regex + r" = ([^;]+);", '', js)
            js = re.sub(regex, omg, js)
            js = re.sub(r"document.getElementById\(\\*'dlbutton\\*'\).href = ", '', js)
            url = self.js.eval(js)
        else:
            #Method #2: SWF eval
            url = self.swf_eval()

            if not url:
                #Method #3: Captcha
                url = self.do_recaptcha()

        return self.file_info['HOST'] + url