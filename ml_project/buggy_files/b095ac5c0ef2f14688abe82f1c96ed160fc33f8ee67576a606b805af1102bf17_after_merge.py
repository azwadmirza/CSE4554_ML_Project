    async def slack_interactions_handler(self, request):
        """Handle interactive events in Slack.

        For each entry in request, it will check if the entry is one of the four main
        interaction types in slack: block_actions, message_actions, view_submissions
        and view_closed. Then it will process all the incoming messages.

        Return:
            A 200 OK response. The Messenger Platform will resend the webhook
            event every 20 seconds, until a 200 OK response is received.
            Failing to return a 200 OK may cause your webhook to be
            unsubscribed by the Messenger Platform.

        """

        req_data = await request.post()
        payload = json.loads(req_data["payload"])

        if "type" in payload:
            if payload["type"] == "block_actions":
                for action in payload["actions"]:
                    block_action = BlockActions(
                        payload,
                        user=payload["user"]["id"],
                        target=payload["channel"]["id"],
                        connector=self,
                    )

                    action_value = None
                    if action["type"] == "button":
                        action_value = action["value"]
                    elif action["type"] in ["overflow", "static_select"]:
                        action_value = action["selected_option"]["value"]
                    elif action["type"] == "datepicker":
                        action_value = action["selected_date"]
                    elif action["type"] == "multi_static_select":
                        action_value = [v["value"] for v in action["selected_options"]]

                    if action_value:
                        await block_action.update_entity("value", action_value)
                    await self.opsdroid.parse(block_action)
            elif payload["type"] == "message_action":
                await self.opsdroid.parse(
                    MessageAction(
                        payload,
                        user=payload["user"]["id"],
                        target=payload["channel"]["id"],
                        connector=self,
                    )
                )
            elif payload["type"] == "view_submission":
                await self.opsdroid.parse(
                    ViewSubmission(
                        payload,
                        user=payload["user"]["id"],
                        target=payload["user"]["id"],
                        connector=self,
                    )
                )
            elif payload["type"] == "view_closed":
                await self.opsdroid.parse(
                    ViewClosed(
                        payload,
                        user=payload["user"]["id"],
                        target=payload["user"]["id"],
                        connector=self,
                    )
                )

        return aiohttp.web.Response(text=json.dumps("Received"), status=200)