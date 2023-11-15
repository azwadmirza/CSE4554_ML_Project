    def get_stats_pie(self, result, stats):
        pie_invalid, pie_off, pie_on, pie_partial = self.extract_pie_data_from_analysis(result)
        total_amount_of_files = self.calculate_total_files_for_pie([pie_off, pie_on, pie_partial, pie_invalid])
        self.append_pie_stats_to_result_dict(pie_invalid, pie_off, pie_on, pie_partial, stats, total_amount_of_files)