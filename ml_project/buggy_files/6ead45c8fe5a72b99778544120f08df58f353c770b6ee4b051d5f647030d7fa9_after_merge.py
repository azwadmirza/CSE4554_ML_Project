    def __read_data_stream(self, name, schema):
        sav = helpers.import_from_plugin("savReaderWriter", plugin="spss")
        path = self.__write_convert_name(name)
        yield schema.field_names
        with sav.SavReader(path, ioUtf8=True, rawMode=False) as reader:
            for item in reader:
                cells = []
                for index, field in enumerate(schema.fields):
                    value = item[index]
                    # Fix decimals that should be integers
                    if field.type == "integer" and value is not None:
                        value = int(float(value))
                    # We need to decode bytes to strings
                    if isinstance(value, bytes):
                        value = value.decode(reader.fileEncoding)
                    # Time values need a decimal, add one if missing.
                    if field.type == "time" and not re.search(r"\.\d*", value):
                        value = "{}.0".format(value)
                    cells.append(value)
                yield cells