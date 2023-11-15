def create_app(
    agent: Optional["Agent"] = None,
    cors_origins: Union[Text, List[Text], None] = "*",
    auth_token: Optional[Text] = None,
    response_timeout: int = DEFAULT_RESPONSE_TIMEOUT,
    jwt_secret: Optional[Text] = None,
    jwt_method: Text = "HS256",
    endpoints: Optional[AvailableEndpoints] = None,
):
    """Class representing a Rasa HTTP server."""

    app = Sanic(__name__)
    app.config.RESPONSE_TIMEOUT = response_timeout
    configure_cors(app, cors_origins)

    # Setup the Sanic-JWT extension
    if jwt_secret and jwt_method:
        # since we only want to check signatures, we don't actually care
        # about the JWT method and set the passed secret as either symmetric
        # or asymmetric key. jwt lib will choose the right one based on method
        app.config["USE_JWT"] = True
        Initialize(
            app,
            secret=jwt_secret,
            authenticate=authenticate,
            algorithm=jwt_method,
            user_id="username",
        )

    app.agent = agent
    # Initialize shared object of type unsigned int for tracking
    # the number of active training processes
    app.active_training_processes = multiprocessing.Value("I", 0)

    @app.exception(ErrorResponse)
    async def handle_error_response(request: Request, exception: ErrorResponse):
        return response.json(exception.error_info, status=exception.status)

    add_root_route(app)

    @app.get("/version")
    async def version(request: Request):
        """Respond with the version number of the installed Rasa."""

        return response.json(
            {
                "version": rasa.__version__,
                "minimum_compatible_version": MINIMUM_COMPATIBLE_VERSION,
            }
        )

    @app.get("/status")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def status(request: Request):
        """Respond with the model name and the fingerprint of that model."""

        return response.json(
            {
                "model_file": app.agent.path_to_model_archive
                or app.agent.model_directory,
                "fingerprint": model.fingerprint_from_path(app.agent.model_directory),
                "num_active_training_jobs": app.active_training_processes.value,
            }
        )

    @app.get("/conversations/<conversation_id:path>/tracker")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def retrieve_tracker(request: Request, conversation_id: Text):
        """Get a dump of a conversation's tracker including its events."""

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)
        until_time = rasa.utils.endpoints.float_arg(request, "until")

        tracker = await app.agent.create_processor().fetch_tracker_with_initial_session(
            conversation_id
        )

        try:
            if until_time is not None:
                tracker = tracker.travel_back_in_time(until_time)

            state = tracker.current_state(verbosity)
            return response.json(state)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.post("/conversations/<conversation_id:path>/tracker/events")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def append_events(request: Request, conversation_id: Text):
        """Append a list of events to the state of a conversation"""
        validate_request_body(
            request,
            "You must provide events in the request body in order to append them"
            "to the state of a conversation.",
        )

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)

        try:
            async with app.agent.lock_store.lock(conversation_id):
                processor = app.agent.create_processor()
                events = _get_events_from_request_body(request)

                tracker = await update_conversation_with_events(
                    conversation_id, processor, app.agent.domain, events
                )

                output_channel = _get_output_channel(request, tracker)

                if rasa.utils.endpoints.bool_arg(
                    request, EXECUTE_SIDE_EFFECTS_QUERY_KEY, False
                ):
                    await processor.execute_side_effects(
                        events, tracker, output_channel
                    )

                app.agent.tracker_store.save(tracker)

            return response.json(tracker.current_state(verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    def _get_events_from_request_body(request: Request) -> List[Event]:
        events = request.json

        if not isinstance(events, list):
            events = [events]

        events = [Event.from_parameters(event) for event in events]
        events = [event for event in events if event]

        if not events:
            rasa.shared.utils.io.raise_warning(
                f"Append event called, but could not extract a valid event. "
                f"Request JSON: {request.json}"
            )
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "BadRequest",
                "Couldn't extract a proper event from the request body.",
                {"parameter": "", "in": "body"},
            )

        return events

    @app.put("/conversations/<conversation_id:path>/tracker/events")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def replace_events(request: Request, conversation_id: Text):
        """Use a list of events to set a conversations tracker to a state."""
        validate_request_body(
            request,
            "You must provide events in the request body to set the sate of the "
            "conversation tracker.",
        )

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)

        try:
            async with app.agent.lock_store.lock(conversation_id):
                tracker = DialogueStateTracker.from_dict(
                    conversation_id, request.json, app.agent.domain.slots
                )

                # will override an existing tracker with the same id!
                app.agent.tracker_store.save(tracker)

            return response.json(tracker.current_state(verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.get("/conversations/<conversation_id:path>/story")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    @ensure_conversation_exists()
    async def retrieve_story(request: Request, conversation_id: Text):
        """Get an end-to-end story corresponding to this conversation."""
        until_time = rasa.utils.endpoints.float_arg(request, "until")
        fetch_all_sessions = rasa.utils.endpoints.bool_arg(
            request, "all_sessions", default=False
        )

        try:
            stories = get_test_stories(
                app.agent.create_processor(),
                conversation_id,
                until_time,
                fetch_all_sessions=fetch_all_sessions,
            )
            return response.text(stories)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.post("/conversations/<conversation_id:path>/execute")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    @ensure_conversation_exists()
    async def execute_action(request: Request, conversation_id: Text):
        request_params = request.json

        action_to_execute = request_params.get("name", None)

        if not action_to_execute:
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "BadRequest",
                "Name of the action not provided in request body.",
                {"parameter": "name", "in": "body"},
            )

        policy = request_params.get("policy", None)
        confidence = request_params.get("confidence", None)
        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)

        try:
            async with app.agent.lock_store.lock(conversation_id):
                tracker = await app.agent.create_processor().fetch_tracker_and_update_session(
                    conversation_id
                )

                output_channel = _get_output_channel(request, tracker)
                await app.agent.execute_action(
                    conversation_id,
                    action_to_execute,
                    output_channel,
                    policy,
                    confidence,
                )

        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

        state = tracker.current_state(verbosity)

        response_body = {"tracker": state}

        if isinstance(output_channel, CollectingOutputChannel):
            response_body["messages"] = output_channel.messages

        return response.json(response_body)

    @app.post("/conversations/<conversation_id:path>/trigger_intent")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def trigger_intent(request: Request, conversation_id: Text) -> HTTPResponse:
        request_params = request.json

        intent_to_trigger = request_params.get("name")
        entities = request_params.get("entities", [])

        if not intent_to_trigger:
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "BadRequest",
                "Name of the intent not provided in request body.",
                {"parameter": "name", "in": "body"},
            )

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)

        try:
            async with app.agent.lock_store.lock(conversation_id):
                tracker = await app.agent.create_processor().fetch_tracker_and_update_session(
                    conversation_id
                )
                output_channel = _get_output_channel(request, tracker)
                if intent_to_trigger not in app.agent.domain.intents:
                    raise ErrorResponse(
                        HTTPStatus.NOT_FOUND,
                        "NotFound",
                        f"The intent {trigger_intent} does not exist in the domain.",
                    )
                await app.agent.trigger_intent(
                    intent_name=intent_to_trigger,
                    entities=entities,
                    output_channel=output_channel,
                    tracker=tracker,
                )
        except ErrorResponse:
            raise
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

        state = tracker.current_state(verbosity)

        response_body = {"tracker": state}

        if isinstance(output_channel, CollectingOutputChannel):
            response_body["messages"] = output_channel.messages

        return response.json(response_body)

    @app.post("/conversations/<conversation_id:path>/predict")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    @ensure_conversation_exists()
    async def predict(request: Request, conversation_id: Text) -> HTTPResponse:
        try:
            # Fetches the appropriate bot response in a json format
            responses = await app.agent.predict_next(conversation_id)
            responses["scores"] = sorted(
                responses["scores"], key=lambda k: (-k["score"], k["action"])
            )
            return response.json(responses)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.post("/conversations/<conversation_id:path>/messages")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def add_message(request: Request, conversation_id: Text):
        validate_request_body(
            request,
            "No message defined in request body. Add a message to the request body in "
            "order to add it to the tracker.",
        )

        request_params = request.json

        message = request_params.get("text")
        sender = request_params.get("sender")
        parse_data = request_params.get("parse_data")

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)

        # TODO: implement for agent / bot
        if sender != "user":
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "BadRequest",
                "Currently, only user messages can be passed to this endpoint. "
                "Messages of sender '{}' cannot be handled.".format(sender),
                {"parameter": "sender", "in": "body"},
            )

        user_message = UserMessage(message, None, conversation_id, parse_data)

        try:
            async with app.agent.lock_store.lock(conversation_id):
                tracker = await app.agent.log_message(user_message)

            return response.json(tracker.current_state(verbosity))
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ConversationError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.post("/model/train")
    @requires_auth(app, auth_token)
    @async_if_callback_url
    @run_in_thread
    @inject_temp_dir
    async def train(request: Request, temporary_directory: Path) -> HTTPResponse:
        validate_request_body(
            request,
            "You must provide training data in the request body in order to "
            "train your model.",
        )

        if request.headers.get("Content-type") == YAML_CONTENT_TYPE:
            training_payload = _training_payload_from_yaml(request, temporary_directory)
        else:
            training_payload = _training_payload_from_json(request, temporary_directory)

        try:
            with app.active_training_processes.get_lock():
                app.active_training_processes.value += 1

            from rasa.train import train_async

            # pass `None` to run in default executor
            training_result = await train_async(**training_payload)

            if training_result.model:
                filename = os.path.basename(training_result.model)

                return await response.file(
                    training_result.model,
                    filename=filename,
                    headers={"filename": filename},
                )
            else:
                raise ErrorResponse(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    "TrainingError",
                    "Ran training, but it finished without a trained model.",
                )
        except ErrorResponse as e:
            raise e
        except InvalidDomain as e:
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "InvalidDomainError",
                f"Provided domain file is invalid. Error: {e}",
            )
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "TrainingError",
                f"An unexpected error occurred during training. Error: {e}",
            )
        finally:
            with app.active_training_processes.get_lock():
                app.active_training_processes.value -= 1

    @app.post("/model/test/stories")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app, require_core_is_ready=True)
    @inject_temp_dir
    async def evaluate_stories(
        request: Request, temporary_directory: Path
    ) -> HTTPResponse:
        """Evaluate stories against the currently loaded model."""
        validate_request_body(
            request,
            "You must provide some stories in the request body in order to "
            "evaluate your model.",
        )

        test_data = _test_data_file_from_payload(request, temporary_directory)

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

    @app.post("/model/test/intents")
    @requires_auth(app, auth_token)
    @async_if_callback_url
    @run_in_thread
    @inject_temp_dir
    async def evaluate_intents(
        request: Request, temporary_directory: Path
    ) -> HTTPResponse:
        """Evaluate intents against a Rasa model."""
        validate_request_body(
            request,
            "You must provide some nlu data in the request body in order to "
            "evaluate your model.",
        )

        cross_validation_folds = request.args.get("cross_validation_folds")
        is_yaml_payload = request.headers.get("Content-type") == YAML_CONTENT_TYPE
        test_coroutine = None

        if is_yaml_payload:
            payload = _training_payload_from_yaml(request, temporary_directory)
            config_file = payload.get("config")
            test_data = payload.get("training_files")

            if cross_validation_folds:
                test_coroutine = _cross_validate(
                    test_data, config_file, int(cross_validation_folds)
                )
        else:
            test_data = _test_data_file_from_payload(request, temporary_directory)
            if cross_validation_folds:
                raise ErrorResponse(
                    HTTPStatus.BAD_REQUEST,
                    "TestingError",
                    "Cross-validation is only supported for YAML data.",
                )

        if not cross_validation_folds:
            test_coroutine = _evaluate_model_using_test_set(
                request.args.get("model"), test_data
            )

        try:
            evaluation = await test_coroutine
            return response.json(evaluation)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "TestingError",
                f"An unexpected error occurred during evaluation. Error: {e}",
            )

    async def _evaluate_model_using_test_set(
        model_path: Text, test_data_file: Text
    ) -> Dict:
        logger.info("Starting model evaluation using test set.")

        eval_agent = app.agent

        if model_path:
            model_server = app.agent.model_server
            if model_server is not None:
                model_server = model_server.copy()
                model_server.url = model_path
                # Set wait time between pulls to `0` so that the agent does not schedule
                # a job to pull the model from the server
                model_server.kwargs["wait_time_between_pulls"] = 0
            eval_agent = await _load_agent(
                model_path, model_server, app.agent.remote_storage
            )

        data_path = os.path.abspath(test_data_file)

        if not eval_agent.model_directory or not os.path.exists(
            eval_agent.model_directory
        ):
            raise ErrorResponse(
                HTTPStatus.CONFLICT, "Conflict", "Loaded model file not found."
            )

        model_directory = eval_agent.model_directory
        _, nlu_model = model.get_model_subdirectories(model_directory)

        return await run_evaluation(
            data_path, nlu_model, disable_plotting=True, report_as_dict=True
        )

    async def _cross_validate(data_file: Text, config_file: Text, folds: int) -> Dict:
        logger.info(f"Starting cross-validation with {folds} folds.")
        importer = TrainingDataImporter.load_from_dict(
            config=None, config_path=config_file, training_data_paths=[data_file]
        )
        config = await importer.get_config()
        nlu_data = await importer.get_nlu_data()

        evaluations = rasa.nlu.cross_validate(
            data=nlu_data,
            n_folds=folds,
            nlu_config=config,
            disable_plotting=True,
            errors=True,
            report_as_dict=True,
        )
        evaluation_results = _get_evaluation_results(*evaluations)

        return evaluation_results

    def _get_evaluation_results(
        intent_report: CVEvaluationResult,
        entity_report: CVEvaluationResult,
        response_selector_report: CVEvaluationResult,
    ) -> Dict[Text, Any]:
        eval_name_mapping = {
            "intent_evaluation": intent_report,
            "entity_evaluation": entity_report,
            "response_selection_evaluation": response_selector_report,
        }

        result = defaultdict(dict)
        for evaluation_name, evaluation in eval_name_mapping.items():
            report = evaluation.evaluation.get("report", {})
            averages = report.get("weighted avg", {})
            result[evaluation_name]["report"] = report
            result[evaluation_name]["precision"] = averages.get("precision")
            result[evaluation_name]["f1_score"] = averages.get("1-score")
            result[evaluation_name]["errors"] = evaluation.evaluation.get("errors", [])

        return result

    @app.post("/model/predict")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app, require_core_is_ready=True)
    async def tracker_predict(request: Request) -> HTTPResponse:
        """Given a list of events, predicts the next action."""
        validate_request_body(
            request,
            "No events defined in request_body. Add events to request body in order to "
            "predict the next action.",
        )

        verbosity = event_verbosity_parameter(request, EventVerbosity.AFTER_RESTART)
        request_params = request.json
        try:
            tracker = DialogueStateTracker.from_dict(
                DEFAULT_SENDER_ID, request_params, app.agent.domain.slots
            )
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.BAD_REQUEST,
                "BadRequest",
                f"Supplied events are not valid. {e}",
                {"parameter": "", "in": "body"},
            )

        try:
            result = app.agent.create_processor().predict_next_with_tracker(
                tracker, verbosity
            )

            return response.json(result)
        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "PredictionError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.post("/model/parse")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def parse(request: Request) -> HTTPResponse:
        validate_request_body(
            request,
            "No text message defined in request_body. Add text message to request body "
            "in order to obtain the intent and extracted entities.",
        )
        emulation_mode = request.args.get("emulation_mode")
        emulator = _create_emulator(emulation_mode)

        try:
            data = emulator.normalise_request_json(request.json)
            try:
                parsed_data = await app.agent.parse_message_using_nlu_interpreter(
                    data.get("text")
                )
            except Exception as e:
                logger.debug(traceback.format_exc())
                raise ErrorResponse(
                    HTTPStatus.BAD_REQUEST,
                    "ParsingError",
                    f"An unexpected error occurred. Error: {e}",
                )
            response_data = emulator.normalise_response_json(parsed_data)

            return response.json(response_data)

        except Exception as e:
            logger.debug(traceback.format_exc())
            raise ErrorResponse(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "ParsingError",
                f"An unexpected error occurred. Error: {e}",
            )

    @app.put("/model")
    @requires_auth(app, auth_token)
    async def load_model(request: Request) -> HTTPResponse:
        validate_request_body(request, "No path to model file defined in request_body.")

        model_path = request.json.get("model_file", None)
        model_server = request.json.get("model_server", None)
        remote_storage = request.json.get("remote_storage", None)

        if model_server:
            try:
                model_server = EndpointConfig.from_dict(model_server)
            except TypeError as e:
                logger.debug(traceback.format_exc())
                raise ErrorResponse(
                    HTTPStatus.BAD_REQUEST,
                    "BadRequest",
                    f"Supplied 'model_server' is not valid. Error: {e}",
                    {"parameter": "model_server", "in": "body"},
                )

        app.agent = await _load_agent(
            model_path, model_server, remote_storage, endpoints, app.agent.lock_store
        )

        logger.debug(f"Successfully loaded model '{model_path}'.")
        return response.json(None, status=HTTPStatus.NO_CONTENT)

    @app.delete("/model")
    @requires_auth(app, auth_token)
    async def unload_model(request: Request) -> HTTPResponse:
        model_file = app.agent.model_directory

        app.agent = Agent(lock_store=app.agent.lock_store)

        logger.debug(f"Successfully unloaded model '{model_file}'.")
        return response.json(None, status=HTTPStatus.NO_CONTENT)

    @app.get("/domain")
    @requires_auth(app, auth_token)
    @ensure_loaded_agent(app)
    async def get_domain(request: Request) -> HTTPResponse:
        """Get current domain in yaml or json format."""
        accepts = request.headers.get("Accept", default=JSON_CONTENT_TYPE)
        if accepts.endswith("json"):
            domain = app.agent.domain.as_dict()
            return response.json(domain)
        elif accepts.endswith("yml") or accepts.endswith("yaml"):
            domain_yaml = app.agent.domain.as_yaml()
            return response.text(
                domain_yaml, status=HTTPStatus.OK, content_type=YAML_CONTENT_TYPE
            )
        else:
            raise ErrorResponse(
                HTTPStatus.NOT_ACCEPTABLE,
                "NotAcceptable",
                f"Invalid Accept header. Domain can be "
                f"provided as "
                f'json ("Accept: {JSON_CONTENT_TYPE}") or'
                f'yml ("Accept: {YAML_CONTENT_TYPE}"). '
                f"Make sure you've set the appropriate Accept "
                f"header.",
            )

    return app