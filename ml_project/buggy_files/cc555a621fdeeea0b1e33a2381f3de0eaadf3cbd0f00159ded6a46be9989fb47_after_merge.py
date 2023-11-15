def parse_node_version(file_path):
    # from node experts the node value in package.json can be found here   "engines": { "node":  ">=10.6.0"}
    import json
    import re
    version_detected = []
    with open(file_path) as data_file:
        data = json.load(data_file)
        for key, value in data.items():
            if key == 'engines' and 'node' in value:
                value_detected = value['node']
                non_decimal = re.compile(r'[^\d.]+')
                # remove the string ~ or  > that sometimes exists in version value
                c = non_decimal.sub('', value_detected)
                # reduce the version to '6.0' from '6.0.0'
                if '.' in c:  # handle version set as 4 instead of 4.0
                    num_array = c.split('.')
                    num = num_array[0] + "." + num_array[1]
                else:
                    num = c + ".0"
                version_detected.append(num)
    return version_detected or ['0.0']