    def serialize_value(value: Any):
        """Serialize Xcom value to str or pickled object"""
        if conf.getboolean('core', 'enable_xcom_pickling'):
            return pickle.dumps(value)
        try:
            return json.dumps(value).encode('UTF-8')
        except (ValueError, TypeError):
            log.error(
                "Could not serialize the XCom value into JSON. "
                "If you are using pickles instead of JSON "
                "for XCom, then you need to enable pickle "
                "support for XCom in your airflow config."
            )
            raise