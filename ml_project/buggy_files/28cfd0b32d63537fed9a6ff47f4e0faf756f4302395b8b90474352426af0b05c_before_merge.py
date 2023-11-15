    def start_task(self, task, rampart_group, dependent_tasks=None, instance=None):
        from awx.main.tasks import handle_work_error, handle_work_success

        dependent_tasks = dependent_tasks or []

        task_actual = {
            'type': get_type_for_model(type(task)),
            'id': task.id,
        }
        dependencies = [{'type': get_type_for_model(type(t)), 'id': t.id} for t in dependent_tasks]

        controller_node = None
        if task.supports_isolation() and rampart_group.controller_id:
            try:
                controller_node = rampart_group.choose_online_controller_node()
            except IndexError:
                logger.debug("No controllers available in group {} to run {}".format(
                             rampart_group.name, task.log_format))
                return

        task.status = 'waiting'

        (start_status, opts) = task.pre_start()
        if not start_status:
            task.status = 'failed'
            if task.job_explanation:
                task.job_explanation += ' '
            task.job_explanation += 'Task failed pre-start check.'
            task.save()
            # TODO: run error handler to fail sub-tasks and send notifications
        else:
            if type(task) is WorkflowJob:
                task.status = 'running'
                task.send_notification_templates('running')
                logger.debug('Transitioning %s to running status.', task.log_format)
                schedule_task_manager()
            elif not task.supports_isolation() and rampart_group.controller_id:
                # non-Ansible jobs on isolated instances run on controller
                task.instance_group = rampart_group.controller
                task.execution_node = random.choice(list(rampart_group.controller.instances.all().values_list('hostname', flat=True)))
                logger.debug('Submitting isolated {} to queue {}.'.format(
                             task.log_format, task.instance_group.name, task.execution_node))
            elif controller_node:
                task.instance_group = rampart_group
                task.execution_node = instance.hostname
                task.controller_node = controller_node
                logger.debug('Submitting isolated {} to queue {} controlled by {}.'.format(
                             task.log_format, task.execution_node, controller_node))
            elif rampart_group.is_containerized:
                # find one real, non-containerized instance with capacity to
                # act as the controller for k8s API interaction
                match = None
                for group in InstanceGroup.objects.all():
                    if group.is_containerized or group.controller_id:
                        continue
                    match = group.find_largest_idle_instance()
                    if match:
                        break
                task.instance_group = rampart_group
                if task.supports_isolation():
                    task.controller_node = match.hostname
                else:
                    # project updates and inventory updates don't *actually* run in pods,
                    # so just pick *any* non-isolated, non-containerized host and use it
                    # as the execution node
                    task.execution_node = match.hostname
                    logger.debug('Submitting containerized {} to queue {}.'.format(
                                 task.log_format, task.execution_node))
            else:
                task.instance_group = rampart_group
                if instance is not None:
                    task.execution_node = instance.hostname
                logger.debug('Submitting {} to <instance group, instance> <{},{}>.'.format(
                             task.log_format, task.instance_group_id, task.execution_node))
            with disable_activity_stream():
                task.celery_task_id = str(uuid.uuid4())
                task.save()

            if rampart_group is not None:
                self.consume_capacity(task, rampart_group.name)

        def post_commit():
            if task.status != 'failed' and type(task) is not WorkflowJob:
                task_cls = task._get_task_class()
                task_cls.apply_async(
                    [task.pk],
                    opts,
                    queue=task.get_queue_name(),
                    uuid=task.celery_task_id,
                    callbacks=[{
                        'task': handle_work_success.name,
                        'kwargs': {'task_actual': task_actual}
                    }],
                    errbacks=[{
                        'task': handle_work_error.name,
                        'args': [task.celery_task_id],
                        'kwargs': {'subtasks': [task_actual] + dependencies}
                    }],
                )

        task.websocket_emit_status(task.status)  # adds to on_commit
        connection.on_commit(post_commit)