    def set_text(self, texte):
        self.can_be_deleted = False
        if texte != "<content/>":
            # defensive programmation to filter bad formatted tasks
            if not texte.startswith("<content>"):
                texte = html.escape(texte, quote=True)
                texte = f"<content>{texte}"
            if not texte.endswith("</content>"):
                texte = f"{texte}</content>"
            self.content = str(texte)
        else:
            self.content = ''