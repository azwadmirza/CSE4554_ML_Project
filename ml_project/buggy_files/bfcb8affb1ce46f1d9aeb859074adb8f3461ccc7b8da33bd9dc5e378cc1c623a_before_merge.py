async def send_message_receive_stream(
    server_url: Text, auth_token: Text, sender_id: Text, message: Text
):
    payload = {"sender": sender_id, "message": message}

    url = f"{server_url}/webhooks/rest/webhook?stream=true&token={auth_token}"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = ClientTimeout(DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, raise_for_status=True) as resp:

            async for line in resp.content:
                if line:
                    yield json.loads(line.decode(DEFAULT_ENCODING))