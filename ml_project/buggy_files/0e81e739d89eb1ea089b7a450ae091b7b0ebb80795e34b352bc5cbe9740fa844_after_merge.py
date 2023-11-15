    def set_title(self, title, transaction_ids=[]):
        """Sets the task title"""
        title = html.escape(title)
        result = self.rtm.tasks.setName(timeline=self.timeline,
                                        list_id=self.rtm_list.id,
                                        taskseries_id=self.rtm_taskseries.id,
                                        task_id=self.rtm_task.id,
                                        name=title)
        transaction_ids.append(result.transaction.id)