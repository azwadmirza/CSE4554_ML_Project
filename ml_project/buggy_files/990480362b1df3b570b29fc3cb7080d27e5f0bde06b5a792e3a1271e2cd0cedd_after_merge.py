    def handle_cannot_determine_type(self, name: str, context: Context) -> None:
        node = self.scope.top_non_lambda_function()
        if self.pass_num < self.last_pass and isinstance(node, FuncDef):
            # Don't report an error yet. Just defer. Note that we don't defer
            # lambdas because they are coupled to the surrounding function
            # through the binder and the inferred type of the lambda, so it
            # would get messy.
            enclosing_class = self.scope.enclosing_class()
            self.defer_node(node, enclosing_class)
            # Set a marker so that we won't infer additional types in this
            # function. Any inferred types could be bogus, because there's at
            # least one type that we don't know.
            self.current_node_deferred = True
        else:
            self.msg.cannot_determine_type(name, context)