    def __init__(self, html_path, refresh_time=1):
        html_filename = 'glances.html'
        html_template = 'default.html'
        self.__refresh_time = refresh_time

        # Set the HTML output file
        self.html_file = os.path.realpath(os.path.join(html_path, html_filename))

        # Get data path
        data_path = os.path.realpath(os.path.join(work_path, 'data'))

        # Set the template path
        template_path = os.path.join(data_path, 'html')
        environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            extensions=['jinja2.ext.loopcontrols'])

        # Open the template
        self.template = environment.get_template(html_template)

        # Define the colors list (hash table) for logged stats
        self.__colors_list = {
            'DEFAULT': "bgcdefault fgdefault",
            'OK': "bgcok fgok",
            'CAREFUL': "bgccareful fgcareful",
            'WARNING': "bgcwarning fgcwarning",
            'CRITICAL': "bgcritical fgcritical"
        }