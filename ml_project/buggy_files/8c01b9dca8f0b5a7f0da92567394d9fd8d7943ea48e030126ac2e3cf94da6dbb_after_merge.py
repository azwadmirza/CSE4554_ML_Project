    def _get_many_from_db_backend(self, async_tasks) -> Mapping[str, EventBufferValueType]:
        task_ids = _tasks_list_to_task_ids(async_tasks)
        session = app.backend.ResultSession()
        task_cls = getattr(app.backend, "task_cls", TaskDb)
        with session_cleanup(session):
            tasks = session.query(task_cls).filter(task_cls.task_id.in_(task_ids)).all()

        task_results = [app.backend.meta_from_decoded(task.to_dict()) for task in tasks]
        task_results_by_task_id = {task_result["task_id"]: task_result for task_result in task_results}
        return self._prepare_state_and_info_by_task_dict(task_ids, task_results_by_task_id)