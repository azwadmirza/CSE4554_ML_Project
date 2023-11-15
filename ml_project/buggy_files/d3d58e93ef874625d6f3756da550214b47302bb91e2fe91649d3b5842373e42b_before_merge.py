    def match(self, node: nodes.image) -> bool:
        if self.app.builder.supported_remote_images == []:
            return False
        elif self.app.builder.supported_data_uri_images is True:
            return False
        else:
            return 'data:' in node['uri']