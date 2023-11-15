    async def start_subscription(self, data, operation_id: str, websocket: WebSocket):
        query = data["query"]
        variables = data.get("variables")
        operation_name = data.get("operation_name")

        if self.debug:
            pretty_print_graphql_operation(operation_name, query, variables)

        context = {"websocket": websocket}

        data = await subscribe(
            self.schema,
            query,
            variable_values=variables,
            operation_name=operation_name,
            context_value=context,
        )

        try:
            async for result in data:
                payload = {"data": result.data}

                if result.errors:
                    payload["errors"] = [
                        format_graphql_error(err) for err in result.errors
                    ]
                await self._send_message(websocket, GQL_DATA, payload, operation_id)
        except Exception as error:
            if not isinstance(error, GraphQLError):
                error = GraphQLError(str(error), original_error=error)

            await self._send_message(
                websocket,
                GQL_DATA,
                {"data": None, "errors": [format_graphql_error(error)]},
                operation_id,
            )

        await self._send_message(websocket, GQL_COMPLETE, None, operation_id)

        if self._keep_alive_task:
            self._keep_alive_task.cancel()

        await websocket.close()