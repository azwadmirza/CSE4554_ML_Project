    def to_dict(self):
        data = {'message_id': self.message_id,
                'from': self.from_user.to_dict(),
                'chat': self.chat.to_dict()}
        try:
            # Python 3.3+ supports .timestamp()
            data['date'] = int(self.date.timestamp())

            if self.forward_date:
                data['forward_date'] = int(self.forward_date.timestamp())
        except AttributeError:
            # _totimestamp() for Python 3 (< 3.3) and Python 2
            data['date'] = self._totimestamp(self.date)

            if self.forward_date:
                data['forward_date'] = self._totimestamp(self.forward_date)

        if self.forward_from:
            data['forward_from'] = self.forward_from.to_dict()
        if self.reply_to_message:
            data['reply_to_message'] = self.reply_to_message
        if self.text:
            data['text'] = self.text
        if self.audio:
            data['audio'] = self.audio.to_dict()
        if self.document:
            data['document'] = self.document.to_dict()
        if self.photo:
            data['photo'] = [p.to_dict() for p in self.photo]
        if self.sticker:
            data['sticker'] = self.sticker.to_dict()
        if self.video:
            data['video'] = self.video.to_dict()
        if self.caption:
            data['caption'] = self.caption
        if self.contact:
            data['contact'] = self.contact.to_dict()
        if self.location:
            data['location'] = self.location.to_dict()
        if self.new_chat_participant:
            data['new_chat_participant'] = self.new_chat_participant
        if self.left_chat_participant:
            data['left_chat_participant'] = self.left_chat_participant
        if self.new_chat_title:
            data['new_chat_title'] = self.new_chat_title
        if self.new_chat_photo:
            data['new_chat_photo'] = self.new_chat_photo
        if self.delete_chat_photo:
            data['delete_chat_photo'] = self.delete_chat_photo
        if self.group_chat_created:
            data['group_chat_created'] = self.group_chat_created
        return data