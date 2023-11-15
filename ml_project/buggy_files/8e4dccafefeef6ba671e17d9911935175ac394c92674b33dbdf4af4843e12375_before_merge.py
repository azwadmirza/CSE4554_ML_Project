    def messages_count(self, **kwargs):
        if self.count is None:
            filter = Q(chunk_ind=1)
            if self.mail_ids is not None:
                filter &= Q(mail__in=self.mail_ids)
            if self.filter:
                filter &= self.filter
            self.messages = Quarantine.objects.filter(filter).values(
                "mail__from_addr",
                "mail__msgrcpt__rid__email",
                "mail__subject",
                "mail__mail_id",
                "mail__time_num",
                "mail__msgrcpt__content",
                "mail__msgrcpt__bspam_level",
                "mail__msgrcpt__rs"
            )
            if "order" in kwargs:
                order = kwargs["order"]
                sign = ""
                if order[0] == "-":
                    sign = "-"
                    order = order[1:]
                order = self.order_translation_table[order]
                self.messages = self.messages.order_by(sign + order)

            self.count = len(self.messages)
        return self.count