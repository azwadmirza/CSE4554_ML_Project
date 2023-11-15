    async def graphql_http_server(self, request: Request) -> Response:
        try:
            data = await self.extract_data_from_request(request)
        except HttpError as error:
            return PlainTextResponse(error.message or error.status, status_code=400)

        success, response = await self.execute_graphql_query(request, data)

        status_code = 200 if success else 400
        return JSONResponse(response, status_code=status_code)