    def operator_method_signatures_overlap(
            self, reverse_class: str, reverse_method: str, forward_class: str,
            forward_method: str, context: Context) -> None:
        self.fail('Signatures of "{}" of "{}" and "{}" of "{}" '
                  'are unsafely overlapping'.format(
                      reverse_method, reverse_class,
                      forward_method, forward_class),
                  context)