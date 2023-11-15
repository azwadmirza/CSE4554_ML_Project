    def execute(self, data, parent_data):
        executor = parent_data.get_one_of_inputs('executor')
        biz_cc_id = parent_data.get_one_of_inputs('biz_cc_id')
        supplier_account = parent_data.get_one_of_inputs('biz_supplier_account')
        client = get_client_by_user(executor)
        if parent_data.get_one_of_inputs('language'):
            translation.activate(parent_data.get_one_of_inputs('language'))

        notify_type = data.get_one_of_inputs('bk_notify_type')
        receiver_info = data.get_one_of_inputs('bk_receiver_info')
        # 兼容原有数据格式
        if receiver_info:
            receiver_group = receiver_info.get('bk_receiver_group')
            more_receiver = receiver_info.get('bk_more_receiver')
        else:
            receiver_group = data.get_one_of_inputs('bk_receiver_group')
            more_receiver = data.get_one_of_inputs('bk_more_receiver')
        title = data.get_one_of_inputs('bk_notify_title')
        content = data.get_one_of_inputs('bk_notify_content')

        code = ''
        message = ''
        result, msg, receivers = get_notify_receivers(client,
                                                      biz_cc_id,
                                                      supplier_account,
                                                      receiver_group,
                                                      more_receiver)

        if not result:
            data.set_outputs('ex_data', msg)
            return False

        for t in notify_type:
            kwargs = self._args_gen[t](self, receivers, title, content)
            result = getattr(client.cmsi, self._send_func[t])(kwargs)

            if not result['result']:
                data.set_outputs('ex_data', result['message'])
                return False

            code = result['code']
            message = result['message']

        data.set_outputs('code', code)
        data.set_outputs('message', message)
        return True