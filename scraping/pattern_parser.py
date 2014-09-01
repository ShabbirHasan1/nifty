# Generated by the Waxeye Parser Generator - version 0.8.0
# www.waxeye.org

from waxeye import Edge, State, FA, WaxeyeParser

class PatternParser (WaxeyeParser):
    start = 0
    eof_check = True
    automata = [FA("document", [State([Edge(12, 1, False)], False),
            State([Edge(16, 2, False)], False),
            State([], True)], FA.PRUNE),
        FA("alphanum", [State([Edge([(48, 57), (65, 90), "_", (97, 122)], 1, False)], False),
            State([], True)], FA.PRUNE),
        FA("space", [State([Edge([(9, 10), "\r", " "], 1, True)], False),
            State([Edge([(9, 10), "\r", " "], 1, True)], True)], FA.VOID),
        FA("tilde", [State([Edge("~", 1, False)], False),
            State([], True)], FA.LEFT),
        FA("dot1", [State([Edge(".", 1, False)], False),
            State([Edge(33, 2, False)], False),
            State([], True)], FA.LEFT),
        FA("dot2", [State([Edge(2, 1, True),
                Edge(".", 2, False)], False),
            State([Edge(".", 2, False)], False),
            State([Edge(".", 3, False)], False),
            State([Edge(34, 4, False)], False),
            State([Edge(2, 5, True)], True),
            State([], True)], FA.LEFT),
        FA("dot3", [State([Edge(2, 1, True),
                Edge(".", 2, False)], False),
            State([Edge(".", 2, False)], False),
            State([Edge(".", 3, False)], False),
            State([Edge(".", 4, False)], False),
            State([Edge(".", 4, False),
                Edge(2, 5, True)], True),
            State([], True)], FA.LEFT),
        FA("special", [State([Edge("{", 1, False),
                Edge("}", 1, False),
                Edge("[", 1, False),
                Edge("]", 1, False),
                Edge("<", 1, False),
                Edge(">", 1, False),
                Edge(".", 1, False),
                Edge("~", 1, False)], False),
            State([], True)], FA.LEFT),
        FA("escaped", [State([Edge("{", 1, True)], False),
            State([Edge(7, 2, False)], False),
            State([Edge("}", 3, True)], False),
            State([], True)], FA.PRUNE),
        FA("space0", [State([Edge(2, 1, False)], False),
            State([], True)], FA.LEFT),
        FA("space1", [State([Edge(2, 1, False)], False),
            State([], True)], FA.LEFT),
        FA("spaceX", [State([Edge(2, 1, False)], False),
            State([], True)], FA.LEFT),
        FA("dropspace", [State([Edge(2, 1, False)], True),
            State([], True)], FA.VOID),
        FA("word", [State([Edge(38, 1, False)], False),
            State([Edge(37, 2, False)], False),
            State([Edge(-1, 3, False)], False),
            State([Edge(36, 4, False)], True),
            State([Edge(35, 5, False)], False),
            State([Edge(-1, 3, False)], False)], FA.LEFT),
        FA("static", [State([Edge(13, 1, False)], False),
            State([Edge(10, 2, False)], True),
            State([Edge(13, 1, False)], False)], FA.LEFT),
        FA("wordB", [State([Edge(13, 1, False)], False),
            State([], True)], FA.LEFT),
        FA("exprA", [State([Edge(8, 0, False),
                Edge(22, 0, False),
                Edge(30, 0, False),
                Edge(28, 0, False),
                Edge(31, 0, False),
                Edge(14, 0, False),
                Edge(21, 0, False),
                Edge(3, 0, False),
                Edge(6, 0, False),
                Edge(5, 0, False),
                Edge(4, 0, False),
                Edge(9, 0, False)], True)], FA.LEFT),
        FA("exprB", [State([Edge(8, 0, False),
                Edge(22, 0, False),
                Edge(30, 0, False),
                Edge(29, 0, False),
                Edge(32, 0, False),
                Edge(15, 0, False),
                Edge(3, 0, False),
                Edge(5, 0, False),
                Edge(4, 0, False),
                Edge(11, 0, False)], True)], FA.LEFT),
        FA("tagspecial", [State([Edge("/", 1, False),
                Edge(":", 1, False)], True),
            State([], True)], FA.LEFT),
        FA("tagname", [State([Edge(13, 1, False)], False),
            State([], True)], FA.LEFT),
        FA("noname", [State([Edge(".", 1, False)], False),
            State([], True)], FA.LEFT),
        FA("tag", [State([Edge("<", 1, True)], False),
            State([Edge(18, 2, False)], False),
            State([Edge(19, 3, False),
                Edge(20, 3, False)], False),
            State([Edge(17, 4, False)], False),
            State([Edge("/", 5, False),
                Edge(">", 6, False)], False),
            State([Edge(">", 6, False)], False),
            State([], True)], FA.LEFT),
        FA("regex", [State([Edge("{", 1, True)], False),
            State([Edge("~", 2, True)], False),
            State([Edge(39, 3, False),
                Edge("~", 4, True)], False),
            State([Edge(-1, 2, False)], False),
            State([Edge("}", 5, True)], False),
            State([], True)], FA.LEFT),
        FA("varname", [State([Edge(1, 1, False)], False),
            State([Edge(1, 1, False)], True)], FA.LEFT),
        FA("repeat", [State([Edge("*", 1, False),
                Edge("+", 1, False),
                Edge("*", 2, False),
                Edge("+", 3, False)], False),
            State([], True),
            State([Edge("+", 1, False)], False),
            State([Edge("+", 1, False)], False)], FA.LEFT),
        FA("vregex", [State([Edge("~", 1, True)], False),
            State([Edge(41, 2, False)], False),
            State([Edge(-1, 3, False)], False),
            State([Edge(40, 4, False)], True),
            State([Edge(-1, 3, False)], False)], FA.LEFT),
        FA("vexprA", [State([Edge(42, 1, False)], False),
            State([Edge(2, 2, True),
                Edge(16, 3, False)], False),
            State([Edge(16, 3, False)], False),
            State([], True)], FA.PRUNE),
        FA("vexprB", [State([Edge(43, 1, False)], False),
            State([Edge(2, 2, True),
                Edge(17, 3, False)], False),
            State([Edge(17, 3, False)], False),
            State([], True)], FA.PRUNE),
        FA("varA", [State([Edge("{", 1, True)], False),
            State([Edge(24, 2, False),
                Edge(23, 3, False),
                Edge(26, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(23, 3, False),
                Edge(26, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(25, 4, False),
                Edge(26, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(26, 5, False),
                Edge("}", 6, True)], False),
            State([Edge("}", 6, True)], False),
            State([], True)], FA.LEFT),
        FA("varB", [State([Edge("{", 1, True)], False),
            State([Edge(24, 2, False),
                Edge(23, 3, False),
                Edge(27, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(23, 3, False),
                Edge(27, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(25, 4, False),
                Edge(27, 5, False),
                Edge("}", 6, True)], False),
            State([Edge(27, 5, False),
                Edge("}", 6, True)], False),
            State([Edge("}", 6, True)], False),
            State([], True)], FA.LEFT),
        FA("atomic", [State([Edge("{", 1, True)], False),
            State([Edge(">", 2, True)], False),
            State([Edge(2, 3, True),
                Edge(16, 4, False)], False),
            State([Edge(16, 4, False)], False),
            State([Edge("}", 5, True)], False),
            State([], True)], FA.LEFT),
        FA("optionalA", [State([Edge("[", 1, True)], False),
            State([Edge(16, 2, False)], False),
            State([Edge("]", 3, True)], False),
            State([], True)], FA.LEFT),
        FA("optionalB", [State([Edge("[", 1, True)], False),
            State([Edge(17, 2, False)], False),
            State([Edge("]", 3, True)], False),
            State([], True)], FA.LEFT),
        FA("", [State([Edge(".", 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge(".", 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge(2, 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge(7, 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge(2, 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge(7, 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge("~", 1, False)], False),
            State([Edge("}", 2, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge("}", 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge("}", 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge("~", 1, False)], False),
            State([], True)], FA.NEG),
        FA("", [State([Edge("~", 1, False)], False),
            State([], True)], FA.NEG)]

    def __init__(self):
        WaxeyeParser.__init__(self, PatternParser.start, PatternParser.eof_check, PatternParser.automata)

