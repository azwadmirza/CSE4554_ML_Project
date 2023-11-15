    def handle(self, *args, **options):
        self.style = color_style()

        self.options = options
        if options["requirements"]:
            req_files = options["requirements"]
        elif os.path.exists("requirements.txt"):
            req_files = ["requirements.txt"]
        elif os.path.exists("requirements"):
            req_files = [
                "requirements/{0}".format(f) for f in os.listdir("requirements")
                if os.path.isfile(os.path.join("requirements", f)) and f.lower().endswith(".txt")
            ]
        elif os.path.exists("requirements-dev.txt"):
            req_files = ["requirements-dev.txt"]
        elif os.path.exists("requirements-prod.txt"):
            req_files = ["requirements-prod.txt"]
        else:
            raise CommandError("Requirements file(s) not found")

        self.reqs = {}
        with PipSession() as session:
            for filename in req_files:
                for req in parse_requirements(filename, session=session):
                    # url attribute changed to link in pip version 6.1.0 and above
                    if LooseVersion(pip.__version__) > LooseVersion('6.0.8'):
                        self.reqs[req.name] = {
                            "pip_req": req,
                            "url": req.link,
                        }
                    else:
                        self.reqs[req.name] = {
                            "pip_req": req,
                            "url": req.url,
                        }

        if options["github_api_token"]:
            self.github_api_token = options["github_api_token"]
        elif os.environ.get("GITHUB_API_TOKEN"):
            self.github_api_token = os.environ.get("GITHUB_API_TOKEN")
        else:
            self.github_api_token = None  # only 50 requests per hour

        self.check_pypi()
        if HAS_REQUESTS:
            self.check_github()
        else:
            print(self.style.ERROR("Cannot check github urls. The requests library is not installed. ( pip install requests )"))
        self.check_other()