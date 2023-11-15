    def check_subtype(self, subtype: Type, supertype: Type, context: Context,
                      msg: str = message_registry.INCOMPATIBLE_TYPES,
                      subtype_label: Optional[str] = None,
                      supertype_label: Optional[str] = None, *,
                      code: Optional[ErrorCode] = None) -> bool:
        """Generate an error if the subtype is not compatible with
        supertype."""
        if is_subtype(subtype, supertype):
            return True

        subtype = get_proper_type(subtype)
        supertype = get_proper_type(supertype)

        if self.should_suppress_optional_error([subtype]):
            return False
        extra_info = []  # type: List[str]
        note_msg = ''
        notes = []  # type: List[str]
        if subtype_label is not None or supertype_label is not None:
            subtype_str, supertype_str = format_type_distinctly(subtype, supertype)
            if subtype_label is not None:
                extra_info.append(subtype_label + ' ' + subtype_str)
            if supertype_label is not None:
                extra_info.append(supertype_label + ' ' + supertype_str)
            note_msg = make_inferred_type_note(context, subtype,
                                               supertype, supertype_str)
            if isinstance(subtype, Instance) and isinstance(supertype, Instance):
                notes = append_invariance_notes([], subtype, supertype)
        if extra_info:
            msg += ' (' + ', '.join(extra_info) + ')'
        self.fail(msg, context, code=code)
        for note in notes:
            self.msg.note(note, context, code=code)
        if note_msg:
            self.note(note_msg, context, code=code)
        if (isinstance(supertype, Instance) and supertype.type.is_protocol and
                isinstance(subtype, (Instance, TupleType, TypedDictType))):
            self.msg.report_protocol_problems(subtype, supertype, context, code=code)
        if isinstance(supertype, CallableType) and isinstance(subtype, Instance):
            call = find_member('__call__', subtype, subtype)
            if call:
                self.msg.note_call(subtype, call, context, code=code)
        if isinstance(subtype, (CallableType, Overloaded)) and isinstance(supertype, Instance):
            if supertype.type.is_protocol and supertype.type.protocol_members == ['__call__']:
                call = find_member('__call__', supertype, subtype)
                assert call is not None
                self.msg.note_call(supertype, call, context, code=code)
        return False