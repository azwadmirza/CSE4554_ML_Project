    def hook(self):
        """Returns S3Hook."""
        remote_conn_id = conf.get('logging', 'REMOTE_LOG_CONN_ID')
        try:
            from airflow.providers.amazon.aws.hooks.s3 import S3Hook

            return S3Hook(remote_conn_id, transfer_config_args={"use_threads": False})
        except Exception as e:  # pylint: disable=broad-except
            self.log.exception(
                'Could not create an S3Hook with connection id "%s". '
                'Please make sure that airflow[aws] is installed and '
                'the S3 connection exists. Exception : "%s"',
                remote_conn_id,
                e,
            )
            return None