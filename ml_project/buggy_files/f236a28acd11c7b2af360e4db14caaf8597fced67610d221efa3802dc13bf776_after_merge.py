    def __init__(self, config={}):

        worker_type = "repo_info_worker"
        
        # Define what this worker can be given and know how to interpret
        given = [['github_url']]
        models = ['repo_info']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_info', 'repo']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Repo Info Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'