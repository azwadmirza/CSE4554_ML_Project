    async def check(self, obj: Union[Message, CallbackQuery, InlineQuery]):
        if isinstance(obj, Message):
            user_id = None
            if obj.from_user is not None:
                user_id = obj.from_user.id
            chat_id = obj.chat.id
        elif isinstance(obj, CallbackQuery):
            user_id = obj.from_user.id
            chat_id = None
            if obj.message is not None:
                # if the button was sent with message
                chat_id = obj.message.chat.id
        elif isinstance(obj, InlineQuery):
            user_id = obj.from_user.id
            chat_id = None
        else:
            return False

        if self.user_id and self.chat_id:
            return user_id in self.user_id and chat_id in self.chat_id
        if self.user_id:
            return user_id in self.user_id
        if self.chat_id:
            return chat_id in self.chat_id

        return False