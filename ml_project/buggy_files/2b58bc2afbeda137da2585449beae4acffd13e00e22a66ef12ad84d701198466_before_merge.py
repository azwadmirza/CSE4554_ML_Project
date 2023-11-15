    def get_repo_data(self, url, response):
        success = False
        try:
            data = response.json()
        except:
            data = json.loads(json.dumps(response.text))

        if 'errors' in data:
            logging.info("Error!: {}".format(data['errors']))
            if data['errors'][0]['message'] == 'API rate limit exceeded':
                self.update_gh_rate_limit(response)

        if 'id' in data:
            success = True
        else:
            logging.info("Request returned a non-data dict: {}\n".format(data))
            if data['message'] == 'Not Found':
                logging.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
            if data['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                self.update_gh_rate_limit(r, temporarily_disable=True)
            if data['message'] == 'Bad credentials':
                self.update_gh_rate_limit(r, bad_credentials=True)
        if not success:
            self.register_task_failure(self.task, repo_id, "Failed to hit endpoint: {}".format(url))

        return data