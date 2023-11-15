    def pull(self, service_names=None, ignore_pull_failures=False, parallel_pull=False, silent=False,
             include_deps=False):
        services = self.get_services(service_names, include_deps)

        if parallel_pull:
            def pull_service(service):
                service.pull(ignore_pull_failures, True)

            _, errors = parallel.parallel_execute(
                services,
                pull_service,
                operator.attrgetter('name'),
                not silent and 'Pulling' or None,
                limit=5,
            )
            if len(errors):
                raise ProjectError(b"\n".join(errors.values()))
        else:
            for service in services:
                service.pull(ignore_pull_failures, silent=silent)