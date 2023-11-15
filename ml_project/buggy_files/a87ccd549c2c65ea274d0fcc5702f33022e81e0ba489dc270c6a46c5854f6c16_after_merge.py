    def _compile_string(self, nb_json):
        """Export notebooks as HTML strings."""
        self._req_missing_ipynb()
        c = Config(self.site.config['IPYNB_CONFIG'])
        c.update(get_default_jupyter_config())
        exportHtml = HTMLExporter(config=c)
        body, _ = exportHtml.from_notebook_node(nb_json)
        return body