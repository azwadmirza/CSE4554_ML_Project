    def get_ending_note(self):
        # command_name = self.context.invoked_with
        return (
            "Type {0}help <command> for more info on a command.\n"
            "You can also type {0}help <category> for more info on a category.".format(
                self.context.clean_prefix
            )
        )