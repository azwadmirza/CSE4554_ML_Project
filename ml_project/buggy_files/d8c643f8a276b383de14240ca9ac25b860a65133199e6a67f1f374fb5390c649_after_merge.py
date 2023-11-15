    def get_text(self, client, node, replaceEnt):
        #get style for current node
        sty=client.styles.styleForNode(node)
        node_fontsize=sty.fontSize
        node_color='#'+sty.textColor.hexval()[2:]
        mf = math_flowable.Math(node.math_data,label=node.label,fontsize=node_fontsize,color=node_color)
        w, h = mf.wrap(0, 0)
        descent = mf.descent()
        img = mf.genImage()
        client.to_unlink.append(img)
        return '<img src="%s" width="%f" height="%f" valign="%f"/>' % (
            img, w, h, -descent)