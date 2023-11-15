    def calculate_total_files_for_pie(pie_off, pie_on, pie_partial, pie_invalid):
        if len(pie_on) > 0 or len(pie_off) > 0 or len(pie_partial) > 0 or len(pie_invalid) > 0:
            total_amount_of_files = pie_on[0][1] + pie_off[0][1] + pie_partial[0][1] + pie_invalid[0][1]
        else:
            total_amount_of_files = 0
        return total_amount_of_files