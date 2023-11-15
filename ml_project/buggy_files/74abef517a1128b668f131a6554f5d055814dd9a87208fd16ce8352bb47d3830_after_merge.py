    def augment(self, resources):
        results = []
        client = local_session(self.session_factory).client('ecs')
        for task_def_set in resources:
            response = self.retry(
                client.describe_task_definition,
                taskDefinition=task_def_set,
                include=['TAGS'])
            r = response['taskDefinition']
            r['tags'] = response.get('tags', [])
            results.append(r)
        ecs_tag_normalize(results)
        return results