    def rpc(self, name):
        """RPC to be execute on remote device
           :name: Name of rpc in string format"""
        try:
            obj = to_ele(name)
            resp = self.m.rpc(obj)
            return resp.data_xml if hasattr(resp, 'data_xml') else resp.xml
        except RPCError as exc:
            msg = exc.data_xml if hasattr(exc, 'data_xml') else exc.xml
            raise Exception(to_xml(msg))