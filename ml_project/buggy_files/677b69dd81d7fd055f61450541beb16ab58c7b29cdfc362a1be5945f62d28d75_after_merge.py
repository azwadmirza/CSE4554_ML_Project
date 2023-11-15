    def write_urlmap_csv(output_file, url_map):
        utils.makedirs(os.path.dirname(output_file))
        if sys.version_info[0] == 2:
            with io.open(output_file, 'wb+') as fd:
                csv_writer = csv.writer(fd)
                for item in url_map.items():
                    csv_writer.writerow(item)
        else:
            with open(output_file, 'w+') as fd:
                csv_writer = csv.writer(fd)
                for item in url_map.items():
                    csv_writer.writerow(item)