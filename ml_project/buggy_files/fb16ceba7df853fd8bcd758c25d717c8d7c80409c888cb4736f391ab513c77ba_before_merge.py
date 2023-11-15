    def get_finished_label_text(self, started):
        """
        When an item finishes, returns a string displaying the start/end datetime range.
        started is a datetime object.
        """
        ended = datetime.now()
        if started.year == ended.year and started.month == ended.month and started.day == ended.day:
            if started.hour == ended.hour and started.minute == ended.minute:
                text = strings._('gui_all_modes_transfer_finished').format(
                    started.strftime("%b %d, %I:%M%p")
                )
            else:
                text = strings._('gui_all_modes_transfer_finished_range').format(
                    started.strftime("%b %d, %I:%M%p"),
                    ended.strftime("%I:%M%p")
                )
        else:
            text = strings._('gui_all_modes_transfer_finished_range').format(
                started.strftime("%b %d, %I:%M%p"),
                ended.strftime("%b %d, %I:%M%p")
            )
        return text