    def write_urlmap_csv(output_file, url_map):
        utils.makedirs(os.path.dirname(output_file))
        fmode = 'wb+' if sys.version_info[0] == 2 else 'w+'
        with io.open(output_file, fmode) as fd:
            csv_writer = csv.writer(fd)
            for item in url_map.items():
                csv_writer.writerow(item)