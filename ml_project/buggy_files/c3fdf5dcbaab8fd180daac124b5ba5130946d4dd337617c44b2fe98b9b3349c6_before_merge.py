    def render(self, validation_results: ExpectationSuiteValidationResult):
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
        columns = {}
        for evr in validation_results.results:
            if "column" in evr.expectation_config.kwargs:
                column = evr.expectation_config.kwargs["column"]
            else:
                column = "Table-Level Expectations"

            if column not in columns:
                columns[column] = []
            columns[column].append(evr)

        ordered_columns = Renderer._get_column_list_from_evrs(validation_results)

        overview_content_blocks = [
            self._render_validation_header(validation_results),
            self._render_validation_statistics(validation_results=validation_results),
        ]

        collapse_content_blocks = [
            self._render_validation_info(validation_results=validation_results)
        ]

        if validation_results["meta"].get("batch_markers"):
            collapse_content_blocks.append(
                self._render_nested_table_from_dict(
                    input_dict=validation_results["meta"].get("batch_markers"),
                    header="Batch Markers",
                )
            )

        if validation_results["meta"].get("batch_kwargs"):
            collapse_content_blocks.append(
                self._render_nested_table_from_dict(
                    input_dict=validation_results["meta"].get("batch_kwargs"),
                    header="Batch Kwargs",
                )
            )

        if validation_results["meta"].get("batch_parameters"):
            collapse_content_blocks.append(
                self._render_nested_table_from_dict(
                    input_dict=validation_results["meta"].get("batch_parameters"),
                    header="Batch Parameters",
                )
            )

        collapse_content_block = CollapseContent(
            **{
                "collapse_toggle_link": "Show more info...",
                "collapse": collapse_content_blocks,
                "styling": {
                    "body": {"classes": ["card", "card-body"]},
                    "classes": ["col-12", "p-1"],
                },
            }
        )

        if not self.run_info_at_end:
            overview_content_blocks.append(collapse_content_block)

        sections = [
            RenderedSectionContent(
                **{
                    "section_name": "Overview",
                    "content_blocks": overview_content_blocks,
                }
            )
        ]

        if "Table-Level Expectations" in columns:
            sections += [
                self._column_section_renderer.render(
                    validation_results=columns["Table-Level Expectations"]
                )
            ]

        sections += [
            self._column_section_renderer.render(validation_results=columns[column],)
            for column in ordered_columns
        ]

        if self.run_info_at_end:
            sections += [
                RenderedSectionContent(
                    **{
                        "section_name": "Run Info",
                        "content_blocks": collapse_content_blocks,
                    }
                )
            ]

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

        page_title = "Validations / " + expectation_suite_name
        if data_asset_name:
            page_title += " / " + data_asset_name
        if include_run_name:
            page_title += " / " + run_name
        page_title += " / " + run_time

        return RenderedDocumentContent(
            **{
                "renderer_type": "ValidationResultsPageRenderer",
                "page_title": page_title,
                "batch_kwargs": batch_kwargs,
                "expectation_suite_name": expectation_suite_name,
                "sections": sections,
                "utm_medium": "validation-results-page",
            }
        )