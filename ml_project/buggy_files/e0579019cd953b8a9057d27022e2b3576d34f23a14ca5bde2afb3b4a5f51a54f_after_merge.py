    def render(self, validation_results):
        run_id = validation_results.meta["run_id"]
        if isinstance(run_id, str):
            try:
                run_time = parse(run_id).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            except (ValueError, TypeError):
                run_time = "__none__"
            run_name = run_id
        elif isinstance(run_id, dict):
            run_name = run_id.get("run_name") or "__none__"
            run_time = run_id.get("run_time") or "__none__"
        elif isinstance(run_id, RunIdentifier):
            run_name = run_id.run_name or "__none__"
            run_time = run_id.run_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        expectation_suite_name = validation_results.meta["expectation_suite_name"]
        batch_kwargs = validation_results.meta.get("batch_kwargs")

        # add datasource key to batch_kwargs if missing
        if "datasource" not in validation_results.meta.get("batch_kwargs", {}):
            # check if expectation_suite_name follows datasource.batch_kwargs_generator.data_asset_name.suite_name pattern
            if len(expectation_suite_name.split(".")) == 4:
                batch_kwargs["datasource"] = expectation_suite_name.split(".")[0]

        # Group EVRs by column
        # TODO: When we implement a ValidationResultSuite class, this method will move there.
        columns = self._group_evrs_by_column(validation_results)

        ordered_columns = Renderer._get_column_list_from_evrs(validation_results)
        column_types = self._overview_section_renderer._get_column_types(
            validation_results
        )

        data_asset_name = batch_kwargs.get("data_asset_name")
        # Determine whether we have a custom run_name
        try:
            run_name_as_time = parse(run_name)
        except ValueError:
            run_name_as_time = None
        try:
            run_time_datetime = parse(run_time)
        except ValueError:
            run_time_datetime = None

        include_run_name: bool = False
        if run_name_as_time != run_time_datetime and run_name_as_time != "__none__":
            include_run_name = True

        page_title = "Profiling Results / " + str(expectation_suite_name)
        if data_asset_name:
            page_title += " / " + str(data_asset_name)
        if include_run_name:
            page_title += " / " + str(run_name)
        page_title += " / " + str(run_time)

        return RenderedDocumentContent(
            **{
                "renderer_type": "ProfilingResultsPageRenderer",
                "page_title": page_title,
                "expectation_suite_name": expectation_suite_name,
                "utm_medium": "profiling-results-page",
                "batch_kwargs": batch_kwargs,
                "sections": [
                    self._overview_section_renderer.render(
                        validation_results, section_name="Overview"
                    )
                ]
                + [
                    self._column_section_renderer.render(
                        columns[column],
                        section_name=column,
                        column_type=column_types.get(column),
                    )
                    for column in ordered_columns
                ],
            }
        )