    def operator_method_signatures_overlap(
            self, reverse_class: TypeInfo, reverse_method: str, forward_class: Type,
            forward_method: str, context: Context) -> None:
        self.fail('Signatures of "{}" of "{}" and "{}" of {} '
                  'are unsafely overlapping'.format(
                      reverse_method, reverse_class.name(),
                      forward_method, self.format(forward_class)),
                  context)