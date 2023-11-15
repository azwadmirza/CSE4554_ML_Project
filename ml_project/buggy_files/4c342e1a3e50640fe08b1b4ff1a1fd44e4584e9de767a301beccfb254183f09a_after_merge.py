    def incompatible_argument_note(self,
                                   original_caller_type: ProperType,
                                   callee_type: ProperType,
                                   context: Context,
                                   code: Optional[ErrorCode]) -> None:
        if (isinstance(original_caller_type, (Instance, TupleType, TypedDictType)) and
                isinstance(callee_type, Instance) and callee_type.type.is_protocol):
            self.report_protocol_problems(original_caller_type, callee_type, context, code=code)
        if (isinstance(callee_type, CallableType) and
                isinstance(original_caller_type, Instance)):
            call = find_member('__call__', original_caller_type, original_caller_type,
                               is_operator=True)
            if call:
                self.note_call(original_caller_type, call, context, code=code)