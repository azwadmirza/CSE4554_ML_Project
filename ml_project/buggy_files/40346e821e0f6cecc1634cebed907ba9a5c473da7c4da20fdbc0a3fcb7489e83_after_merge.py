    def as_story_string(self, e2e=False):
        if self.intent:
            if self.entities:
                ent_string = json.dumps(
                    {ent["entity"]: ent["value"] for ent in self.entities},
                    ensure_ascii=False,
                )
            else:
                ent_string = ""

            parse_string = "{intent}{entities}".format(
                intent=self.intent.get("name", ""), entities=ent_string
            )
            if e2e:
                message = md_format_message(self.text, self.intent, self.entities)
                return "{}: {}".format(self.intent.get("name"), message)
            else:
                return parse_string
        else:
            return self.text