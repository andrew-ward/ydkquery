import stream
import lextools
import querylib
import db


PREFIX = ['not', 'any', 'all']
INFIX = {
			'or'  : 20,
			'and' : 20,
			'contains' : 50,
			'>'   : 50,
			'>='  : 50,
			'<='  : 50,
			'='   : 50,
			'!='  : 50,
			'<'   : 50,
			'>'   : 50
}

lexer = lextools.AutoLexer(
	operators=(
		[ '(', ')'] +
		[x for x in INFIX.keys() if not x.isalpha()] +
		[x for x in PREFIX if not x.isalpha()]
	) ,
	keywords= (
		[x for x in INFIX.keys() if x.isalpha()] +
		[x for x in PREFIX if x.isalpha()])
)

class Visitor(object):
	def visit_base(self, ast, card):
		raise NotImplementedError()
	def visit_prefix(self, ast, card):
		raise NotImplementedError()
	def visit_infix(self, ast, card):
		raise NotImplementedError()

class BaseAST(object):
	def __init__(self, kind, data):
		self.kind = kind
		self.data = data
	def accept(self, visitor, arg):
		return visitor.visit_base(self, arg)
	def __str__(self):
		return str(self.data)

class PrefixAST(object):
	def __init__(self, head, arg):
		self.head = head
		self.arg = arg
	def accept(self, visitor, arg):
		return visitor.visit_prefix(self, arg)
	def __str__(self):
		return '({0} {1})'.format(self.head, self.arg)

class InfixAST(object):
	def __init__(self, left, op, right):
		self.left = left
		self.operator = op
		self.right = right
	def accept(self, visitor, arg):
		return visitor.visit_infix(self, arg)
	def __str__(self):
		return '({0} {1} {2})'.format(self.left, self.operator, self.right)

class Parser(object):
	def __init__(self, tokens):
		self.source = stream.IterStream(tokens)
		self.prefix = PREFIX
		self.infix = INFIX

	def peekPrec(self):
		if self.source.empty():
			return 0
		nxt = self.source.peek()
		if nxt.kind in ('keyword', 'operator') and nxt.data in self.infix:
			return self.infix[nxt.data]
		else:
			return 0

	def parse(self, precedence=0):
		if self.source.empty():
			raise RuntimeError('cannot parse empty stream')
		nxt = self.source.next()

		left = None

		if nxt.kind in ['integer', 'string', 'word']:
			left = BaseAST(nxt.kind, nxt.data)
		
		elif nxt.kind == 'operator' and nxt.data == '(':
			left = self.parse()
			if self.source.empty():
				raise RuntimeError('Reached eof while parsing parentheses')
			elif self.source.peek().kind != 'operator' or self.source.peek().data != ')':
				raise RuntimeError('Invalid token {0} found while parsing parentheses'.format(self.source.peek()))
			else:
				self.source.next()

		elif nxt.kind == 'keyword' and nxt.data in self.prefix:
			left = PrefixAST(nxt.data, self.parse(35))

		else:
			raise RuntimeError('Cannot parse stream because found unknown token {0}'.format(nxt))

		while self.source.ready():
			op = self.source.peek()
			if op.kind in ('operator', 'keyword') and op.data in self.infix:
				if precedence < self.infix[op.data]:
					op = self.source.next()
					left = InfixAST(left, op.data, self.parse(self.infix[op.data]))
				else:
					break
			else:
				break

		return left
				

class Evaluator(Visitor):
	@staticmethod
	def ofString(txt):
		tokens = list(lexer.tokenize(txt))
		print(tokens)
		parser = Parser(tokens)
		ast = parser.parse()
		return Evaluator(ast)

	@staticmethod
	def ofTokens(tokens):
		parser = Parser(tokens)
		return Evaluator(parser.parse())

	@staticmethod
	def ofAST(ast):
		return Evaluator(ast)
		
	def __init__(self, ast):
		self.library = querylib.Library
		assert(ast != None)
		self.ast = ast

	def __call__(self, arg):
		return self.ast.accept(self, arg)

	def visit_base(self, base, arg):
		if base.kind == 'integer':
			return int(base.data)
		elif base.kind == 'string':
			return base.data
		elif base.kind == 'word':
			if base.data == 'true':
				return True
			elif base.data == 'false':
				return False
			elif base.data in db.MAGIC_NUMBERS:
				return base.data
			elif isinstance(arg, db.Card) and base.data in arg:
				return arg[base.data]
			raise RuntimeError('Invalid variable name {0}'.format(base.data))
	
	def visit_prefix(self, prefix_ast, arg):
		if prefix_ast.head in self.library:
			return self.library[prefix_ast.head](self, arg, prefix_ast.arg)
		else:
			raise RuntimeError('Invalid prefix command {0}'.format(prefix_ast.head))

	def visit_infix(self, inast, arg):
		left = inast.left
		right = inast.right
		op = inast.operator
		if op in self.library:
			return self.library[op](self, arg, left, right)
		else:
			raise RuntimeError('Invalid infix operator {0}'.format(op))
