    async def find_linked_message_from_dm(self, message, either_direction=False):
        if either_direction and message.embeds:
            compare_url = message.embeds[0].author.url
            compare_id = compare_url.split("#")[-1]
        else:
            compare_url = None
            compare_id = None

        if self.channel is not None:
            async for linked_message in self.channel.history():
                if not linked_message.embeds:
                    continue
                url = linked_message.embeds[0].author.url
                if not url:
                    continue
                if url == compare_url:
                    return linked_message

                msg_id = url.split("#")[-1]
                if not msg_id.isdigit():
                    continue
                msg_id = int(msg_id)
                if int(msg_id) == message.id:
                    return linked_message

                if compare_id is not None and compare_id.isdigit():
                    if int(msg_id) == int(compare_id):
                        return linked_message

            raise ValueError("Thread channel message not found.")