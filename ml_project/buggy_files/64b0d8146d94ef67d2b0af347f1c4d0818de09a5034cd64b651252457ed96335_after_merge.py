    def serve_component_suites(self, package_name, path_in_package_dist):
        if package_name not in self.registered_paths:
            raise exceptions.InvalidResourceError(
                'Error loading dependency.\n'
                '"{}" is not a registered library.\n'
                'Registered libraries are: {}'
                .format(package_name, list(self.registered_paths.keys())))

        elif path_in_package_dist not in self.registered_paths[package_name]:
            raise exceptions.InvalidResourceError(
                '"{}" is registered but the path requested is not valid.\n'
                'The path requested: "{}"\n'
                'List of registered paths: {}'
                .format(
                    package_name,
                    path_in_package_dist,
                    self.registered_paths
                )
            )

        mimetype = ({
            'js': 'application/JavaScript',
            'css': 'text/css'
        })[path_in_package_dist.split('.')[-1]]

        headers = {
            'Cache-Control': 'public, max-age={}'.format(
                self.config.components_cache_max_age)
        }

        return Response(
            pkgutil.get_data(package_name, path_in_package_dist),
            mimetype=mimetype,
            headers=headers
        )