    def _login(self):
        (username, password) = self._get_login_info()
        if username is None:
            self.raise_login_required('safaribooksonline.com account is required')

        headers = std_headers.copy()
        if 'Referer' not in headers:
            headers['Referer'] = self._LOGIN_URL
        login_page_request = sanitized_Request(self._LOGIN_URL, headers=headers)

        login_page = self._download_webpage(
            login_page_request, None,
            'Downloading login form')

        csrf = self._html_search_regex(
            r"name='csrfmiddlewaretoken'\s+value='([^']+)'",
            login_page, 'csrf token')

        login_form = {
            'csrfmiddlewaretoken': csrf,
            'email': username,
            'password1': password,
            'login': 'Sign In',
            'next': '',
        }

        request = sanitized_Request(
            self._LOGIN_URL, urlencode_postdata(login_form), headers=headers)
        login_page = self._download_webpage(
            request, None, 'Logging in as %s' % username)

        if re.search(self._SUCCESSFUL_LOGIN_REGEX, login_page) is None:
            raise ExtractorError(
                'Login failed; make sure your credentials are correct and try again.',
                expected=True)

        self.to_screen('Login successful')