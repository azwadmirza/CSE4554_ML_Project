    def calculate_total_files_for_pie(pie_stats):
        total_amount_of_files = 0
        for item in pie_stats:
            with suppress(IndexError):
                total_amount_of_files += item[0][1]
        return total_amount_of_files