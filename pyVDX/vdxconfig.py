from parsimonious.grammar import Grammar
from collections import OrderedDict

conf = """no support autoupload enable
interfae Vlan 1
!
diag read interface-id 1
 enable
!
cee-map default
 precedence 1
 priority-group-table 1 weight 40 pfc on
 priority-group-table 15.0 pfc off
 priority-table 2 2 2 1 2 2 2 15.0
 remap fabric-priority priority 0
 remap lossless-priority priority 0
!
fcoe
 fabric-map default
  vlan 1002
  fcmap 0E:FC:00
  keep-alive timeout
 !
 map default
  fabric-map default
  cee-map default
 !
!
"""


class VdxConfig(object):
    """
    Vdx Config parser
    """
    def __init__(self, revision_id):
        self.revision_id = revision_id
        self.config = OrderedDict()
        self.__grammer__ = (r"""
                items = (~r"\n"* item (newline item)* "\n"*)
                item = (block / line)

                block = (indent* text (newline item)* newline indent* block_close)
                line = (indent* text)

                text = (token (space token)*)
                block_close = "!"
                indent = ~r" +"
                newline = "\n"
                space = ~r" +"
                token = ~r"[a-zA-Z0-9/:-].+"
                number = ~r"[0-9]+"
        """)

    def parse(self, string):
        return Grammar(self.__grammer__).parse(string)

    def loads(self, node):
        if isinstance(node, str):
            node = self.parse(node)
        method = getattr(self, node.expr_name, self.default)
        return method(node, [self.loads(n) for n in node])

    def default(self, node, children):
        return children

    def items(self, node, children):
        return children

    def item(self, node, children):
        return children

    def block(self, node, children):
        return children

    def line(self, node, children):
        return node.text.split(' ')

    def text(self, node, children):
        return node.text

    def block_close(self, node, children):
        return node.text

    def indent(self, node, children):
        return node.text

    def newline(self, node, children):
        return node.text

    def space(self, node, children):
        return node.text

    def token(self, node, children):
        return node.text

    def number(self, node, children):
        return node.text


def main():
    vdx = VdxConfig("tmp")
    print(vdx.parse(conf))
    print(vdx.loads(conf))

if __name__ == "__main__":
    main()
