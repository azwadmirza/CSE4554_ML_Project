    def _template_url_to_path(self, template_url):
        # TODO: this code assumes a specific url schema, should rather attempt to
        #  resolve values from params/defaults
        template_path = None
        if isinstance(template_url, dict):
            if "Fn::Sub" in template_url.keys():
                if isinstance(template_url["Fn::Sub"], str):
                    template_path = template_url["Fn::Sub"].split("}")[-1]
                else:
                    template_path = template_url["Fn::Sub"][0].split("}")[-1]
            elif "Fn::Join" in list(template_url.keys())[0]:
                template_path = template_url["Fn::Join"][1][-1]
        elif isinstance(template_url, str):
            template_path = "/".join(template_url.split("/")[-2:])
        if isinstance(template_path, str):
            template_path = self.project_root / template_path
            if template_path.is_file():
                return template_path
        LOG.warning(
            "Failed to discover path for %s, path %s does not exist",
            template_url,
            template_path,
        )
        return ""