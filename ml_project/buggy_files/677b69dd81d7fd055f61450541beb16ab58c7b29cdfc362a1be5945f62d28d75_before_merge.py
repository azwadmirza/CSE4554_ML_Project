    def write_urlmap_csv(output_file, url_map):
        utils.makedirs(os.path.dirname(output_file))
        with io.open(output_file, 'w+', encoding='utf8') as fd:
            csv_writer = csv.writer(fd)
            for item in url_map.items():
                csv_writer.writerow(item)