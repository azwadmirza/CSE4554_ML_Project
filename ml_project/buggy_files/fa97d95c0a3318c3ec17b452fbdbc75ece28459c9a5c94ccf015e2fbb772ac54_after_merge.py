    def _render_validation_header(cls, validation_results):
        success = validation_results.success
        expectation_suite_name = validation_results.meta["expectation_suite_name"]
        expectation_suite_path_components = (
            [".." for _ in range(len(expectation_suite_name.split(".")) + 3)]
            + ["expectations"]
            + str(expectation_suite_name).split(".")
        )
        expectation_suite_path = (
            os.path.join(*expectation_suite_path_components) + ".html"
        )
        if success:
            success = "Succeeded"
            html_success_icon = (
                '<i class="fas fa-check-circle text-success" aria-hidden="true"></i>'
            )
        else:
            success = "Failed"
            html_success_icon = (
                '<i class="fas fa-times text-danger" aria-hidden="true"></i>'
            )
        return RenderedHeaderContent(
            **{
                "content_block_type": "header",
                "header": RenderedStringTemplateContent(
                    **{
                        "content_block_type": "string_template",
                        "string_template": {
                            "template": "Overview",
                            "tag": "h5",
                            "styling": {"classes": ["m-0"]},
                        },
                    }
                ),
                "subheader": RenderedStringTemplateContent(
                    **{
                        "content_block_type": "string_template",
                        "string_template": {
                            "template": "${suite_title} ${expectation_suite_name}\n${status_title} ${html_success_icon} ${success}",
                            "params": {
                                "suite_title": "Expectation Suite:",
                                "status_title": "Status:",
                                "expectation_suite_name": expectation_suite_name,
                                "success": success,
                                "html_success_icon": html_success_icon,
                            },
                            "styling": {
                                "params": {
                                    "suite_title": {"classes": ["h6"]},
                                    "status_title": {"classes": ["h6"]},
                                    "expectation_suite_name": {
                                        "tag": "a",
                                        "attributes": {"href": expectation_suite_path},
                                    },
                                },
                                "classes": ["mb-0", "mt-1"],
                            },
                        },
                    }
                ),
                "styling": {
                    "classes": ["col-12", "p-0"],
                    "header": {"classes": ["alert", "alert-secondary"]},
                },
            }
        )