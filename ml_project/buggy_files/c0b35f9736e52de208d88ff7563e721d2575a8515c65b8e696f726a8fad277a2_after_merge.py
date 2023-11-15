    def on_finish(self) -> None:
        total_any = sum(num_any for num_any, _ in self.counts.values())
        total_expr = sum(total for _, total in self.counts.values())
        total_coverage = 100.0
        if total_expr > 0:
            total_coverage = (float(total_expr - total_any) / float(total_expr)) * 100

        any_column_name = "Anys"
        total_column_name = "Exprs"
        file_column_name = "Name"
        coverage_column_name = "Coverage"
        # find the longest filename all files
        name_width = max([len(file) for file in self.counts] + [len(file_column_name)])
        # totals are the largest numbers in their column - no need to look at others
        min_column_distance = 3  # minimum distance between numbers in two columns
        any_width = max(len(str(total_any)) + min_column_distance, len(any_column_name))
        exprs_width = max(len(str(total_expr)) + min_column_distance, len(total_column_name))
        coverage_width = len(coverage_column_name) + min_column_distance
        header = '{:{name_width}} {:>{any_width}} {:>{total_width}} {:>{coverage_width}}'.format(
            file_column_name, any_column_name, total_column_name, coverage_column_name,
            name_width=name_width, any_width=any_width, total_width=exprs_width,
            coverage_width=coverage_width)

        with open(os.path.join(self.output_dir, 'any-exprs.txt'), 'w') as f:
            f.write(header + '\n')
            separator = '-' * len(header) + '\n'
            f.write(separator)
            coverage_width -= 1  # subtract one for '%'
            for file in sorted(self.counts):
                (num_any, num_total) = self.counts[file]
                coverage = (float(num_total - num_any) / float(num_total)) * 100
                f.write('{:{name_width}} {:{any_width}} {:{total_width}} '
                        '{:>{coverage_width}.2f}%\n'.
                        format(file, num_any, num_total, coverage, name_width=name_width,
                               any_width=any_width, total_width=exprs_width,
                               coverage_width=coverage_width))
            f.write(separator)
            f.write('{:{name_width}} {:{any_width}} {:{total_width}} {:>{coverage_width}.2f}%\n'
                    .format('Total', total_any, total_expr, total_coverage, name_width=name_width,
                            any_width=any_width, total_width=exprs_width,
                            coverage_width=coverage_width))