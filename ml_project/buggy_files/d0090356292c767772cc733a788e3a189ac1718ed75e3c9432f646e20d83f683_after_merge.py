    async def evaluate_stories(
        request: Request, temporary_directory: Path
    ) -> HTTPResponse:
        """Evaluate stories against the currently loaded model."""
        validate_request_body(
            request,
            "You must provide some stories in the request body in order to "
            "evaluate your model.",
        )

        test_data = _test_data_file_from_payload(request, temporary_directory, ".md")

        use_e2e = rasa.utils.endpoints.bool_arg(request, "e2e", default=False)

        try:
            evaluation = await test(
                test_data, app.agent, e2e=use_e2e, disable_plotting=True
            )
            return response.json(evaluation)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "TestingError",
                f"An unexpected error occurred during evaluation. Error: {e}",
            )