    def build(self, resource_identifiers=None):
        source_store_keys = self.source_store.list_keys()
        if self.name == "validations" and self.validation_results_limit:
            source_store_keys = sorted(
                source_store_keys, key=lambda x: x.run_id.run_time, reverse=True
            )[: self.validation_results_limit]

        for resource_key in source_store_keys:
            # if no resource_identifiers are passed, the section
            # builder will build
            # a page for every keys in its source store.
            # if the caller did pass resource_identifiers, the section builder
            # will build pages only for the specified resources
            if resource_identifiers and resource_key not in resource_identifiers:
                continue

            if self.run_name_filter:
                if not resource_key_passes_run_name_filter(
                    resource_key, self.run_name_filter
                ):
                    continue
            try:
                resource = self.source_store.get(resource_key)
            except exceptions.InvalidKeyError:
                logger.warning(
                    f"Object with Key: {str(resource_key)} could not be retrieved. Skipping..."
                )
                continue

            if isinstance(resource_key, ExpectationSuiteIdentifier):
                expectation_suite_name = resource_key.expectation_suite_name
                logger.debug(
                    "        Rendering expectation suite {}".format(
                        expectation_suite_name
                    )
                )
            elif isinstance(resource_key, ValidationResultIdentifier):
                run_id = resource_key.run_id
                run_name = run_id.run_name
                run_time = run_id.run_time
                expectation_suite_name = (
                    resource_key.expectation_suite_identifier.expectation_suite_name
                )
                if self.name == "profiling":
                    logger.debug(
                        "        Rendering profiling for batch {}".format(
                            resource_key.batch_identifier
                        )
                    )
                else:

                    logger.debug(
                        "        Rendering validation: run name: {}, run time: {}, suite {} for batch {}".format(
                            run_name,
                            run_time,
                            expectation_suite_name,
                            resource_key.batch_identifier,
                        )
                    )

            try:
                rendered_content = self.renderer_class.render(resource)
                viewable_content = self.view_class.render(
                    rendered_content,
                    data_context_id=self.data_context_id,
                    show_how_to_buttons=self.show_how_to_buttons,
                )
            except Exception as e:
                exception_message = f"""\
An unexpected Exception occurred during data docs rendering.  Because of this error, certain parts of data docs will \
not be rendered properly and/or may not appear altogether.  Please use the trace, included in this message, to \
diagnose and repair the underlying issue.  Detailed information follows:
                """
                exception_traceback = traceback.format_exc()
                exception_message += (
                    f'{type(e).__name__}: "{str(e)}".  '
                    f'Traceback: "{exception_traceback}".'
                )
                logger.error(exception_message, e, exc_info=True)

            self.target_store.set(
                SiteSectionIdentifier(
                    site_section_name=self.name, resource_identifier=resource_key,
                ),
                viewable_content,
            )