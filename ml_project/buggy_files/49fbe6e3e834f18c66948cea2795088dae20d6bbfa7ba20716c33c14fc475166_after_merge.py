def dag_link(attr):
    """Generates a URL to the Graph View for a Dag."""
    dag_id = attr.get('dag_id')
    execution_date = attr.get('execution_date')
    url = url_for('Airflow.graph', dag_id=dag_id, execution_date=execution_date)
    return Markup('<a href="{}">{}</a>').format(url, dag_id) if dag_id else Markup('None')  # noqa