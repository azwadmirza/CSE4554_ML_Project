    def fetch(self, start=None, stop=None, **kwargs):
        emails = []
        for qm in self.messages[start - 1:stop]:
            m = {"from": qm["mail__from_addr"],
                 "to": qm["mail__msgrcpt__rid__email"],
                 "subject": qm["mail__subject"],
                 "mailid": qm["mail__mail_id"],
                 "date": qm["mail__time_num"],
                 "type": qm["mail__msgrcpt__content"],
                 "score": qm["mail__msgrcpt__bspam_level"]}
            rs = qm["mail__msgrcpt__rs"]
            if rs == 'D':
                continue
            elif rs == '':
                m["class"] = "unseen"
            elif rs == 'R':
                m["img_rstatus"] = static_url("pics/release.png")
            elif rs == 'p':
                m["class"] = "pending"
            emails.append(m)
        return emails