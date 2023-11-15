    def deserialize_value(result: "XCom") -> Any:
        """Deserialize XCom value from str or pickle object"""
        enable_pickling = conf.getboolean('core', 'enable_xcom_pickling')
        if enable_pickling:
            return pickle.loads(result.value)
        try:
            return json.loads(result.value.decode('UTF-8'))
        except JSONDecodeError:
            log.error(
                "Could not deserialize the XCom value from JSON. "
                "If you are using pickles instead of JSON "
                "for XCom, then you need to enable pickle "
                "support for XCom in your airflow config."
            )
            raise