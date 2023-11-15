    def trigger(self, session=None):
        dag_id = request.values.get('dag_id')
        origin = request.values.get('origin') or "/admin/"

        if request.method == 'GET':
            return self.render(
                'airflow/trigger.html',
                dag_id=dag_id,
                origin=origin,
                conf=''
            )

        dag = session.query(models.DagModel).filter(models.DagModel.dag_id == dag_id).first()
        if not dag:
            flash("Cannot find dag {}".format(dag_id))
            return redirect(origin)

        execution_date = timezone.utcnow()
        run_id = "manual__{0}".format(execution_date.isoformat())

        dr = DagRun.find(dag_id=dag_id, run_id=run_id)
        if dr:
            flash("This run_id {} already exists".format(run_id))
            return redirect(origin)

        run_conf = {}
        conf = request.values.get('conf')
        if conf:
            try:
                run_conf = json.loads(conf)
            except ValueError:
                flash("Invalid JSON configuration", "error")
                return self.render(
                    'airflow/trigger.html',
                    dag_id=dag_id,
                    origin=origin,
                    conf=conf,
                )

        dag = dagbag.get_dag(dag_id)
        dag.create_dagrun(
            run_id=run_id,
            execution_date=execution_date,
            state=State.RUNNING,
            conf=run_conf,
            external_trigger=True
        )

        flash(
            "Triggered {}, "
            "it should start any moment now.".format(dag_id))
        return redirect(origin)