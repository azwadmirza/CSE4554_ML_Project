    def remove(self, rule_type, rule_control, rule_path):
        current_line = self._head
        changed = 0

        while current_line is not None:
            if current_line.matches(rule_type, rule_control, rule_path):
                if current_line.prev is not None:
                    current_line.prev.next = current_line.next
                    current_line.next.prev = current_line.prev
                else:
                    self._head = current_line.next
                    current_line.next.prev = None
                changed += 1

            current_line = current_line.next
        return changed