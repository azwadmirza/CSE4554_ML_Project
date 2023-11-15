    def fetch_cluster_credentials(cls, db_user, db_name, cluster_id,
                                  iam_profile, duration_s, autocreate,
                                  db_groups):
        """Fetches temporary login credentials from AWS. The specified user
        must already exist in the database, or else an error will occur"""

        if iam_profile is None:
            boto_client = boto3.client('redshift')
        else:
            logger.debug("Connecting to Redshift using 'IAM'" +
                         f"with profile {iam_profile}")
            boto_session = boto3.Session(
                profile_name=iam_profile
            )
            boto_client = boto_session.client('redshift')

        try:
            return boto_client.get_cluster_credentials(
                DbUser=db_user,
                DbName=db_name,
                ClusterIdentifier=cluster_id,
                DurationSeconds=duration_s,
                AutoCreate=autocreate,
                DbGroups=db_groups,)

        except boto_client.exceptions.ClientError as e:
            raise dbt.exceptions.FailedToConnectException(
                "Unable to get temporary Redshift cluster credentials: {}"
                .format(e))