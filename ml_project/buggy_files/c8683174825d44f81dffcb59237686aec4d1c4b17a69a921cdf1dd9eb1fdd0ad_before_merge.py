    def sendChatAction(self,
                       chat_id,
                       action):
        """Use this method when you need to tell the user that something is
        happening on the bot's side. The status is set for 5 seconds or less
        (when a message arrives from your bot, Telegram clients clear its
        typing status).

        Args:
          chat_id:
            Unique identifier for the message recipient - User or GroupChat id.
          action:
            Type of action to broadcast. Choose one, depending on what the user
            is about to receive:
            - ChatAction.TYPING for text messages,
            - ChatAction.UPLOAD_PHOTO for photos,
            - ChatAction.UPLOAD_VIDEO or upload_video for videos,
            - ChatAction.UPLOAD_AUDIO or upload_audio for audio files,
            - ChatAction.UPLOAD_DOCUMENT for Lesser files,
            - ChatAction.FIND_LOCATION for location data.
        """

        url = '%s/sendChatAction' % self.base_url

        data = {'chat_id': chat_id,
                'action': action}

        return url, data