    def _check_missing_providers(providers):

        current_airflow_version = Version(__import__("airflow").__version__)
        if current_airflow_version.major >= 2:
            prefix = "apache-airflow-providers-"
        else:
            prefix = "apache-airflow-backport-providers-"

        for provider in providers:
            dist_name = prefix + provider
            try:
                distribution(dist_name)
            except PackageNotFoundError:
                yield "Please install `{}`".format(dist_name)