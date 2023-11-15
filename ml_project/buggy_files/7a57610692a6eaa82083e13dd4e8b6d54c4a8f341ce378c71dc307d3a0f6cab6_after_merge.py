    def list_repositories(self):

        res = self._query('ListRepositories', api_pb2.ListRepositoriesRequest)

        return deserialize_json_to_dagster_namedtuple(
            res.serialized_list_repositories_response_or_error
        )