def workflow_resources(workflow_id):
    workflow_details = Workflow.query.filter_by(run_id=workflow_id).first()
    if workflow_details is None:
        return render_template('error.html', message="Workflow %s could not be found" % workflow_id)

    df_resources = pd.read_sql_query(
        "SELECT * FROM resource WHERE run_id='%s'" % (workflow_id), db.engine)
    df_task = pd.read_sql_query(
        "SELECT * FROM task WHERE run_id='%s'" % (workflow_id), db.engine)

    df_task_resources = pd.read_sql_query('''
                                          SELECT task_id, timestamp, resource_monitoring_interval,
                                          psutil_process_cpu_percent, psutil_process_time_user,
                                          psutil_process_memory_percent, psutil_process_memory_resident
                                          from resource
                                          where run_id = '%s'
                                          ''' % (workflow_id), db.engine)

    return render_template('resource_usage.html', workflow_details=workflow_details,
                           user_time_distribution_avg_plot=resource_distribution_plot(
                               df_resources, df_task, type='psutil_process_time_user', label='CPU Time Distribution', option='avg'),
                           user_time_distribution_max_plot=resource_distribution_plot(
                               df_resources, df_task, type='psutil_process_time_user', label='CPU Time Distribution', option='max'),
                           memory_usage_distribution_avg_plot=resource_distribution_plot(
                               df_resources, df_task, type='psutil_process_memory_resident', label='Memory Distribution', option='avg'),
                           memory_usage_distribution_max_plot=resource_distribution_plot(
                               df_resources, df_task, type='psutil_process_memory_resident', label='Memory Distribution', option='max'),
                           user_time_time_series=resource_time_series(
                               df_task_resources, type='psutil_process_time_user', label='CPU User Time'),
                           cpu_percent_time_series=resource_time_series(
                               df_task_resources, type='psutil_process_cpu_percent', label='CPU Utilization'),
                           memory_percent_time_series=resource_time_series(
                               df_task_resources, type='psutil_process_memory_percent', label='Memory Utilization'),
                           memory_resident_time_series=resource_time_series(
                               df_task_resources, type='psutil_process_memory_resident', label='Memory Usage'),
                           )