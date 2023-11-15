    def __init__(self, **kwargs):
        """The TikTokApi class. Used to interact with TikTok.

        :param logging_level: The logging level you want the program to run at
        :param request_delay: The amount of time to wait before making a request.
        :param executablePath: The location of the chromedriver.exe
        """
        # Forces Singleton
        if TikTokApi.__instance is None:
            TikTokApi.__instance = self
        else:
            raise Exception("Only one TikTokApi object is allowed")
        logging.basicConfig(level=kwargs.get("logging_level", logging.WARNING))
        logging.info("Class initalized")
        self.executablePath = kwargs.get("executablePath", None)

        self.userAgent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.111 Safari/537.36"
        )
        self.proxy = kwargs.get("proxy", None)

        self.signer_url = kwargs.get("external_signer", None)
        if self.signer_url == None:
            self.browser = browser(**kwargs)
            self.userAgent = self.browser.userAgent
        

        try:
            self.timezone_name = self.__format_new_params__(self.browser.timezone_name)
            self.browser_language = self.__format_new_params__(
                self.browser.browser_language
            )
            self.browser_platform = self.__format_new_params__(
                self.browser.browser_platform
            )
            self.browser_name = self.__format_new_params__(self.browser.browser_name)
            self.browser_version = self.__format_new_params__(
                self.browser.browser_version
            )
            self.width = self.browser.width
            self.height = self.browser.height
        except Exception as e:
            logging.warning("An error occured but it was ignored.")

            self.timezone_name = ""
            self.browser_language = ""
            self.browser_platform = ""
            self.browser_name = ""
            self.browser_version = ""
            self.width = "1920"
            self.height = "1080"

        self.request_delay = kwargs.get("request_delay", None)