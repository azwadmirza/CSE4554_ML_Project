    def get(self):
        template = env.get_template('embed.html')
        script = autoload_server(model=None, url='http://localhost:5006/bkapp')
        self.write(template.render(script=script))