# -*- coding: utf-8 -*-
'''
Wrapper classes for parsers produced by parser generators: Waxeye, Parsimonious, or any other generator.
For easy implementation of semantic analysis - this is the major task that still has to be done by the programmer
after parser is generated.

Usage for Waxeye parsers (TODO: update this doc):
- Write LANG.wx file with Waxeye grammar of your language, LANG. Compile it to LANG_parser.py - it will contain LANGParser class.
- Subclass Context, WaxeyeTree and WaxeyeParser from this module. You'll get language-specific classes: Context, Tree and Parser
  (in some cases, Parser can be omitted and WaxeyeParser instantiated directly, without subclassing).
- Set: Tree.Parser = LANGParser, Tree.Context = Context, Parser.Tree = Tree

- Implement Context class so that it can collect all necessary language-specific data 
  when passed across the syntax Tree in WaxeyeTree.node.analyse().

- Inside Tree, define inner classes (nodes) for each non-terminal of the grammar that can be yielded by LANGParser.
  Class names must have a form of 'xNAME', where NAME is the name of the non-terminal.
  Typically, they will inherit from WaxeyeTree's "node" or "static". 
  Often, you'd like to implement own base "node" class, inheriting from the standard one.

- In nodes, override compile() method - it will be called by Tree.compile() and Parser.compile().
  Some nodes may require custom semantic analysis - override analyse() in such case.
  Implement other methods, as necessary: init(), __str__, ...

- Override Tree.compile() if you need special post-processing of the overall output generated by nodes' compile().
  Inside, call self._compile() to get the raw output.

- Use:
  >>> parser = Parser()
  >>> parser.parse(text)    -- to parse 'text' to a syntax tree (class Tree)
  >>> parser.compile(text)  -- to parse 'text' and compile the resulting tree, in one step

---
This file is part of Nifty python package. Copyright (c) 2009-2014 by Marcin Wojnarski.

Nifty is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
Nifty is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Nifty. If not, see <http://www.gnu.org/licenses/>.
'''

import copy
from ..util import isstring, escape, flatten

try:
    import waxeye           # you can use this object in client code when you need to access internal Waxeye objects
except:
    pass

#try:
#    from parsimonious.nodes import Node as ParsimoniousNode
#except:
#    pass


########################################################################################################################################################
###
###  UTILITIES
###

class ParserError(Exception):
    
    MAXLEN = 20
    pos    = None       # (start,end) position where the error occured, or None
    line   = None       # derived from 'pos'
    column = None       # derived from 'pos'
    text   = None       # initial MAXLEN characters of the input fragment that caused the error
    node   = None

    def __init__(self, msg, node = None, cause = None):
        if node:
            self.node, self.pos, self.text = node, node.pos, node.text(self.MAXLEN)
        if self.pos:                                            # calculate the line number and column of self.pos, if possible
            prefix = node.fulltext[:self.pos[1]]
            self.line = prefix.count('\n') + 1
            self.column = len(prefix) - prefix.rfind('\n')
        msg = self.make_msg(msg) or msg
        if cause: msg += " because of %s: %s" % (type(cause).__name__, cause)
        super(ParserError, self).__init__(msg)
        
    def make_msg(self, msg):
        if self.pos:
            return msg + " at line %s, column %s (%s)" % (self.line, self.column, self.text)


########################################################################################################################################################
###
###  TREE
###

class Tree(object):
    """Semantic tree. Produced as a result of rewriting of the original raw AST generated by parser.
    In contrast to raw AST, which always comprises nodes of the same type, no matter what language is parsed,
    this Tree comprises custom domain-specific nodes which implement semantic analysis specific to a given language.
    That's why rewriting from AST to Tree is needed.
    Subclasses of Tree should contain inner node classes named after the names of non-terminals of the grammar, 
    precedeed by leading 'x' to differentiate node classes from Tree methods and attributes.
    Instead of inner classes, you can use methods.
    """
    parser  = None              # instance of AST parser class produced by parser generator; only one method is used: parse(text) -> AST
    #Context = None              # Context subclass that shall be used in semantic analysis

    _use_init = True            # only set to True in old code that uses init(...) with arguments; otherwise set False in subclasses and override setup() in nodes

    # the sets below can be given as a space-separated string of names instead of a set
    _ignore_  = set()           # set of non-terminals that should be ignored during rewriting (pruned from the tree)
    _reduce_  = set()           # set of non-terminals that should be replaced with a list of their children
    _compact_ = set()           # set of non-terminals that should be replaced with their child if there is exactly 1 child AFTER rewriting of all children

    text    = None              # full text of the input string fed to the parser
    ast     = None              # raw AST generated by the parser; for read access by the client
    root    = None              # root node of the final tree after rewriting
    
    def __init__(self, text = None, ast = None, stopAfter = None):
        """Build Tree, either from input 'text' (will be parsed to raw AST and then rewritten to Tree), 
        or from raw AST 'ast' (only rewriting will be done).
        """
        def _split(names):
            if isstring(names): names = names.split()
            if isinstance(names, list): names = set(names)
            return names

        self._ignore_  = _split(self._ignore_)
        self._reduce_  = _split(self._reduce_)
        self._compact_ = _split(self._compact_)
        
        self.text = text
        self.ast = self.parse(text) if text else ast                # parse input text to raw AST; keep AST for reference by the client
        if stopAfter == "parse": return
        
        self.root = self.rewrite(self.ast)                          # rewrite AST to a tree of <Tree.node> nodes
        if not self.root: return
        
        self.root._enrich()                                         # enrich nodes with basic semantic information
        
        # bottom-up initialization of nodes by calls to custom init(), no arguments
        if not self._use_init:
            self.root._setup_all()

    def __str__(self):
        "For printing of the tree. Walks the tree via node.children, collects info() lines and concatenates them with proper indentation."
        lines = self.info(self.root)
        return '\n'.join(flatten(lines))

    @staticmethod
    def info(node, depth = 0):
        prefix = '  ' * depth
        if isstring(node): return prefix + node
        return prefix + node.info(), [Tree.info(n, depth+1) for n in node.children]

    def parse(self, text):
        "Parses raw text (string) into a syntax tree built of custom node classes (self.Tree). Can be overridden in subclasses."
        return self.parser.parse(text)

    def rewrite(self, astroot):
        "Recursively convert a node of raw AST and all its subtree into appropriate subclasses of ``Tree.node``. Generator-specific."
        raise NotImplementedError()
    
    def _rewriteNode(self, astnode):
        "Rewrites contents of a single node to corresponding Tree.node attributes: pos, type, children. Generator-specific."
        raise NotImplementedError()
    
    def compile(self):                                                                                                          #@ReservedAssignment
        "Full compilation, with postprocessing. Can be overriden in subclasses, but usually overriding postprocess() or analyse() is enough."
        data = self.analyse()                                   # run top-down semantic analysis of the tree
        code = self.root.compile()                              # generate output code
        return self.postprocess(code, data)

    def analyse(self):
        ctx = self.root.analyse(self.Context())
        return ctx.data

    def postprocess(self, code, data):
        "Override in subclasses to perform custom postprocessing of the compiled code and possibly change the return type, e.g., avoid returning 'data'."
        return code, data
        
    ### Base node classes
    
    class node(object):
        """Generic recursive node: passes all str() and compile() requests down to children, then concatenates returned strings.
        Base class for all nodes in rewritten trees.
        """
        
        tree     = None
        astnode  = None                     # original AST node this node was created from
        fulltext = None                     # full text of the input string fed to the parser; see text()
        pos      = None                     # (start,end) positions of the substring represented by this node in 'fulltext'
        type     = None                     # name of non-terminal that produced this node, [str]   @ReservedAssignment
        display  = ""                       # string representation of this node for debugging purposes
        
        children = []                       # list of child nodes after rewriting
        
        # enriched information
        parent = None                       # parent node; None if root
        sibling_prev = None                 # older sibling (before this node) AFTER rewriting
        sibling_next = None                 # younger sibling (after this node) AFTER rewriting
        
        @property
        def line(self):
            """
            Line number in `fulltext` where this node's match begins.
            NOTE: this method scans all fulltext up to self.pos, which can be costly.
            """
            prefix = self.fulltext[:self.pos[0]]
            return prefix.count('\n') + 1

        @property
        def column(self):
            prefix = self.fulltext[:self.pos[0]]
            return len(prefix) - prefix.rfind('\n')

        def __init__(self, tree, astnode): 
            self.tree = tree
            self.astnode = astnode
            self.fulltext = tree.text
            self.pos, self.type, self.children = tree._rewriteNode(astnode)
            if tree._use_init:
                self.init(tree, astnode)
            
        def init(self, tree = None, astnode = None):
            """
            Subclasses should override this method (args can be dropped!) instead of __init__,
            so that standard initialization is still performed beforehand, without explicit super() call.
            DEPRECATED. In new code, override setup() instead.
            """
        def setup(self):
            """
            Like init(), but doesn't take arguments. Can be overriden in subclasses to perform
            custom initialization of a node after standard rewriting and enrichment.
            In new code, setup() should be overriden instead of init(...), with Tree._use_init = False.
            """
            
        def _setup_all(self):
            """Recursive bottom-up initialization of nodes with calls to custom setup() methods, no arguments (!)."""
            for child in self.children: child._setup_all()
            self.setup()

        def text(self, maxlen = None):
            """The substring of source text matched by this node, or its leading 'maxlen' characters if maxlen != None. 
            None if this node was derived from other nodes during tree post-processing."""
            if not self.pos: return None
            end = self.pos[1] if maxlen is None else min(self.pos[1], self.pos[0] + maxlen)
            ret = self.fulltext[ self.pos[0] : end ]
            if end < self.pos[1]: return ret + "..."
            return ret
    
        def info(self):
            #d = self.__dict__.copy(); del d['fulltext']
            ds = "" #" %s" % d
            return "%s%s at position %s matching: %s" % (self.infoName(), ds, self.pos, escape(str(self.text())))
        def infoName(self):
            # override in subclasses to customize info() printout
            return "<%s>" % (self.type or self.__class__.__name__)
        
        def __str__(self): 
            return self.display or ''.join(str(c) for c in self.children)
        
        def child(self, idx):
            "Returns child with a given index, or None if missing."
            return self.children[idx] if len(self.children) > idx else None
        
        def _enrich(self):
            """Recursively enrich nodes with basic semantic information. Called right after rewriting."""
            
            prev = None
            for child in self.children:
                child.parent = self
                child.sibling_prev = prev
                if prev: prev.sibling_next = child
                prev = child

            for child in self.children:
                child._enrich()

        def analyse(self, ctx):
            """Top-down semantic analysis of the tree. 'ctx' is the opening Context (pre-context) of the current node. 
            Returns closing context (post-context) of the node, which may be the same object 'ctx' (!), but doesn't have to.  
            Parent nodes shall NEVER assume that 'ctx' doesn't get modified when passed down to a child.
            If this object is going to be used again after passing to a child (even if it's only passing to another child!), 
            a copy should be passed instead of the original.
            """
            for c in self.children: c.analyse(ctx.copy())
            return ctx

        def compile(self): #@ReservedAssignment
            "Top-down compilation of the tree. By default, returns concatenation of strings compiled by children nodes."
            return ''.join(c.compile() for c in self.children)

    class virtual(node):
        """A node that's artificially created after the tree is parsed, 
        having no corresponding AST node nor a position in the source text."""
        def __init__(self, tree):
            "No 'astnode' argument, we only keep the tree reference."
            self.tree = tree
    
    class static(node):
        """Static string (or value of another type) that can be inferred already during parsing (node initialization) and then returned 
        in str() and compile(). By default, the value is made up in __init__ by merging strings from all children."""
        typecast = str              # type or method that will be applied to the parsed string to convert it to a value of appropriate type
        
        def __init__(self, tree, astnode, string = None):
            "Additional argument 'string' is accepted, not present in base 'node'. It's used as a node value if children produce empty string."
            self.tree = tree
            self.fulltext = tree.text
            self.pos, self.type, children = tree._rewriteNode(astnode) if astnode else (None, None, [])
            string = ''.join(str(c) for c in children) or string or ''
            self.value = self.typecast(string)
            if tree._use_init:
                self.init(tree, astnode)
        
        def __str__(self): return str(self.value)
        def compile(self): return self.value                                                        #@ReservedAssignment
    
    class const(node):
        "A node that always generates the same output: cls.value. However, in general, it can be parsed from different substrings of input text (!)."
        value = ""
        def compile(self): return self.value                                                        #@ReservedAssignment
    
    class string(node):
        """Artificial node created at some intermediate stage of tree post-processing that may or may not correspond
        to a specific node of the initial AST. Typically produced from partial compilation of some other Tree nodes.
        """
        value = None
        type  = "(string)"                                                                          #@ReservedAssignment
        
        def __init__(self, tree, value, pos = None):
            self.tree = tree
            self.fulltext = tree.text
            self.value = value
            self.pos = pos
        def info(self):
            return "<%s> %s" % (self.type, escape(self.value))
        
    
    class empty(static): pass


########################################################################################################################################################
###
###  WAXEYE tree
###

class WaxeyeTree(Tree):

    def parse(self, text):
        waxtree = self.parser.parse(text)
        if isinstance(waxtree, waxeye.ParseError): raise waxtree
        return waxtree

    def rewrite(self, waxnode):
        if isstring(waxnode): return self.static(self, None, waxnode) 
        if not isinstance(waxnode, waxeye.AST): return self.empty(self, None)
        
        # node is a regular non-terminal; find corresponding inner class of the tree and instantiate (this will recursively rewrite nodes down the tree)
        nodeclass = getattr(self, 'x' + waxnode.type)
        return nodeclass(self, waxnode)

    def _rewriteNode(self, waxnode):
        children = [self.rewrite(c) for c in waxnode.children]
        return waxnode.pos, waxnode.type, children
    

########################################################################################################################################################
###
###  PARSIMONIOUS tree
###

class ParsimoniousTree(Tree):

    NODES = None                # the container (module/class/...) where node classes "x***" can be found; if None, self is used instead

    _reduce_anonym_ = True      # shall we reduce anonymous nodes? these are the nodes generated by unnamed expressions, typically groupings (...);
                                # leaf nodes (static strings) will be removed entirely from the tree, i.e., ignored rather than reduced
    _reduce_string_ = True      # if a node to be reduce has no children but matched a non-empty part of the text, shall it be replaced with a string node
                                # instead of raising an exception? 

    class reduced(Tree.string):
        "Like Tree.string, but adapted to reducing Parsimonious AST nodes."
        type = "(reduced)"
        
        def __init__(self, tree, astnode):
            Tree.string.__init__(self, tree, astnode.text, (astnode.start, astnode.end))
        

    def rewrite(self, astnode):
        def flat(): return self._rewriteNode(astnode)[-1]       # flattening: return children instead of the node
            
        if astnode is None: return None
        name = astnode.expr_name
        if not name and self._reduce_anonym_: return flat()     # flatten nodes without names; leaf nodes (static strings) removed entirely
        if name in self._ignore_: return []                     # remove nodes listed in _ignore_, together with their subtrees
        if name in self._reduce_:                               # flatten nodes listed in _reduce_
            if astnode.children: return flat()
            if astnode.start == astnode.end != None: return []
            if self._reduce_string_: return self.reduced(astnode)
            raise ParserError("Trying to reduce a node that has no children but consumed a non-empty part of the input at position (%s,%s): %s" % 
                              (astnode.start, astnode.end, astnode))
        
        # find corresponding inner class of the tree and instantiate (this will recursively rewrite nodes down the tree)
        nodeclass = getattr(self.NODES or self, 'x' + name)
        node = nodeclass(self, astnode)
    
        if name in self._compact_:                              # flatten nodes listed in _compact_
            if len(node.children) == 1: return node.children[0]

        return node
    
    def _rewriteNode(self, astnode):
        children = flatten(self.rewrite(c) for c in astnode.children)
        return (astnode.start, astnode.end), astnode.expr_name, children        # pos, type, children
    

########################################################################################################################################################
###
###  CONTEXT of semantic analysis
###

class Context(object):
    """Base class for classes representing current context of semantic analysis in Tree.analyse(), 
    for top-down transfer of contextual data from parent to child nodes and for bottom-up collection of global data from all nodes. 
    Can be modified along the way, when passed through the tree, and copied with .copy() method 
    when local modifications must be performed. 
    """
    
    Data = None                             # class (or function that returns instantiated object) of self.data
    
    def __init__(self):
        self.data = self.Data() if self.Data else None          # global semantic information about the syntax tree, shared by all copies of Context
        
    def copy(self):
        "A safe - shallow - copy of Context. Global data are shared by all copies."
        return copy.copy(self)
    
