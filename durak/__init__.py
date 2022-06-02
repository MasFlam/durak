import argparse
from dataclasses import dataclass, asdict
from typing import Optional, Dict
import os
import json
import importlib.util
from .grammar import DurakParser
from .grammar import DurakLexer
from .grammar import DurakParserVisitor
from antlr4 import FileStream, CommonTokenStream

class DurakExpr:
	pass

@dataclass
class ExprOr(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprAnd(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprNot(DurakExpr):
	expr: DurakExpr

@dataclass
class ExprEq(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprNe(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprLt(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprGt(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprLe(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprGe(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprAdd(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprSub(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprMult(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprDiv(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprMod(DurakExpr):
	left: DurakExpr
	right: DurakExpr

@dataclass
class ExprDot(DurakExpr):
	head: DurakExpr
	tail: list

@dataclass
class ExprIdent(DurakExpr):
	identifier: str

class ExprLiteral(DurakExpr):
	pass

@dataclass
class ExprIntLiteral(ExprLiteral):
	value: int

@dataclass
class ExprFloatLiteral(ExprLiteral):
	value: float

@dataclass
class ExprStringLiteral(ExprLiteral):
	value: str

@dataclass
class Document:
	body: list

@dataclass
class Comment:
	text: str

@dataclass
class Element:
	name: str
	attributes: list
	body: Optional[list]

@dataclass
class TagAttribute:
	name: str
	value: Optional[DurakExpr]

@dataclass
class IfDirective:
	conditions: list
	bodies: list
	else_body: Optional[list]

@dataclass
class ForeachDirective:
	varname: str
	through: DurakExpr
	body: list
	else_body: Optional[list]

@dataclass
class IncludeDirective:
	expr: DurakExpr
	body: Optional[list]

@dataclass
class InsertDirective:
	identifier: str

@dataclass
class Injection:
	expr: DurakExpr

@dataclass
class HtmlElement:
	name: str
	attributes: list
	body: Optional[list]
	
	def __str__(self):
		attr_str = ''.join([' ' + a.name + '="' + a.value + '"' if a.value else ' ' + a.name for a in self.attributes])
		if self.body is not None:
			return '<' + self.name + attr_str + '>' + ''.join(str(x) for x in self.body) + '</' + self.name + '>'
		else:
			return '<' + self.name + attr_str + '/>'

@dataclass
class HtmlAttribute:
	name: str
	value: Optional[str]

@dataclass
class HtmlText:
	text: str
	
	def __str__(self):
		return self.text

class Resource:
	def __init__(self, is_component: bool, name: str, has_py: bool, has_meta: bool):
		self._is_component = is_component
		self._name = name
		self._has_py = has_py
		self._has_meta = has_meta
		self._doc = None
		self._meta = None
		self._pymod = None
		self._model = None
		self.status = None if is_component else 'unrendered'
	
	def is_component(self) -> bool:
		return self._is_component
	
	def name(self) -> str:
		return self._name
	
	def has_py(self) -> bool:
		return self._has_py
	
	def has_meta(self) -> bool:
		return self._has_meta
	
	def doc(self) -> Document:
		return self._doc
	
	def meta(self) -> dict:
		return self._meta
	
	def pymod(self):
		return self._pymod
	
	def model(self) -> dict:
		return self._model
	
	def path(self) -> str:
		return self._name[1:] + (".drc" if self._is_component else ".dr")
	
	def path_py(self) -> str:
		return self._name[1:] + ".py" if self._has_py else None
	
	def path_meta(self) -> str:
		return self._name[1:] + ".json" if self._has_meta else None
	
	def path_output(self) -> str:
		return self._name[1:] + ".html" if not self._is_component else None
	
	def __str__(self):
		return f'<Resource {self._name}>'

class DurakVisitor(DurakParserVisitor):
	def visitDocument(self, ctx):
		body = []
		for entity in ctx.entity():
			body.append(self.visit(entity))
		return Document(body=body)
	
	def visitEntity(self, ctx):
		if ctx.VERBATIM():
			return ctx.VERBATIM().getText().removeprefix("<!>").removesuffix("<!/>")
		elif ctx.COMMENT():
			return Comment(ctx.COMMENT().getText())
		elif ctx.TEXT():
			return ctx.TEXT().getText()
		else:
			return self.visitChildren(ctx)
	
	def visitElement(self, ctx):
		name = ctx.TAG_NAME().getText()
		attributes = []
		for attr in ctx.tag_attribute():
			attributes.append(self.visit(attr))
		if ctx.tag_attribute_last():
			attributes.append(self.visit(ctx.tag_attribute_last()))
		if ctx.entity() is not None:
			body = []
			for ent in ctx.entity():
				body.append(self.visit(ent))
		else:
			body = None
		return Element(name=name, attributes=attributes, body=body)
	
	def visitTag_attribute(self, ctx):
		name = ctx.TAG_ATTRIBUTE_NAME().getText()
		if ctx.expr_dot():
			value = self.visit(ctx.expr_dot())
		else:
			value = None
		return TagAttribute(name=name, value=value)
	
	def visitTag_attribute_last(self, ctx):
		return self.visitTag_attribute(ctx) # same logic
	
	def visitDirective(self, ctx):
		return self.visitChildren(ctx)
	
	def visitIf_directive(self, ctx):
		if_condition = self.visit(ctx.expr())
		if_body = []
		for ent in ctx.main_body:
			if_body.append(self.visit(ent))
		conditions = [if_condition]
		bodies = [if_body]
		for x in ctx.if_directive_elif():
			condition = self.visit(x.expr())
			body = []
			for ent in x.entity():
				body.append(self.visit(ent))
			conditions.append(condition)
			bodies.append(body)
		else_body = []
		for ent in ctx.else_body:
			else_body.append(self.visit(ent))
		return IfDirective(conditions=conditions, bodies=bodies, else_body=else_body)
	
	def visitForeach_directive(self, ctx):
		varname = ctx.DIRECTIVE_FOREACH_IDENTIFIER().getText()
		through = self.visit(ctx.expr())
		body = []
		for ent in ctx.main_body:
			body.append(self.visit(ent))
		if ctx.else_body is not None:
			else_body = []
			for ent in ctx.else_body:
				else_body.append(self.visit(ent))
		else:
			else_body = None
		return ForeachDirective(varname=varname, through=through, body=body, else_body=else_body)
	
	def visitInclude_directive(self, ctx):
		expr = self.visit(ctx.expr())
		if ctx.element() is not None:
			body = []
			for ent in ctx.element():
				body.append(self.visit(ent))
		else:
			body = None
		return IncludeDirective(expr=expr, body=body)
	
	def visitInsert_directive(self, ctx):
		identifier = ctx.DIRECTIVE_INSERT_IDENTIFIER().getText()
		return InsertDirective(identifier=identifier)
	
	def visitInjection(self, ctx):
		expr = self.visit(ctx.expr())
		return Injection(expr)
	
	def visitExpr(self, ctx):
		return self.visitChildren(ctx)
	
	def visitExpr_or(self, ctx):
		if not ctx.left:
			return self.visitChildren(ctx)
		return ExprOr(left=self.visit(ctx.left), right=self.visit(ctx.right))
	
	def visitExpr_and(self, ctx):
		if not ctx.left:
			return self.visitChildren(ctx)
		return ExprAnd(left=self.visit(ctx.left), right=self.visit(ctx.right))
	
	def visitExpr_comp(self, ctx):
		if not ctx.left:
			return self.visitChildren(ctx)
		op = ctx.op.getSymbol().type
		if   op == DurakParser.EXPR_EQEQ: T = ExprEq
		elif op == DurakParser.EXPR_NEQ:  T = ExprNe
		elif op == DurakParser.EXPR_LT:   T = ExprLt
		elif op == DurakParser.EXPR_GT:   T = ExprGt
		elif op == DurakParser.EXPR_LE:   T = ExprLe
		elif op == DurakParser.EXPR_GE:   T = ExprGe
		return T(left=self.visit(ctx.left), right=self.visit(ctx.right))
	
	def visitExpr_addsub(self, ctx):
		if not ctx.left:
			return self.visitChildren(ctx)
		op = ctx.op.getSymbol().type
		if   op == DurakParser.EXPR_PLUS:  T = ExprAdd
		elif op == DurakParser.EXPR_MINUS: T = ExprSub
		return T(left=self.visit(ctx.left), right=self.visit(ctx.right))
	
	def visitExpr_multdiv(self, ctx):
		if not ctx.left:
			return self.visitChildren(ctx)
		op = ctx.op.getSymbol().type
		if   op == DurakParser.EXPR_MULT: T = ExprMult
		elif op == DurakParser.EXPR_DIV:  T = ExprDiv
		elif op == DurakParser.EXPR_MOD:  T = ExprMod
		return T(left=self.visit(ctx.left), right=self.visit(ctx.right))
	
	def visitExpr_dot(self, ctx):
		if not ctx.head:
			return self.visitChildren(ctx)
		tail = []
		for ident in ctx.tail:
			tail.append(ident.text)
		return ExprDot(head=self.visit(ctx.head), tail=tail)
	
	def visitExpr_atom(self, ctx):
		if ctx.EXPR_IDENT():
			return ExprIdent(identifier=ctx.EXPR_IDENT().getText())
		else:
			return self.visitChildren(ctx)
	
	def visitExpr_literal(self, ctx):
		if ctx.EXPR_INT_LITERAL():
			return ExprIntLiteral(value=int(ctx.EXPR_INT_LITERAL().getText()))
		elif ctx.EXPR_FLOAT_LITERAL():
			return ExprFloatLiteral(value=float(ctx.EXPR_FLOAT_LITERAL().getText()))
		elif ctx.EXPR_STRING_LITERAL():
			# TODO: string literals
			return ExprStringLiteral(value=ctx.EXPR_STRING_LITERAL().getText()[1:-1])

class Durak:
	
	def __init__(self, source_dir: str):
		self.source_dir = source_dir
		self.resources = dict()
		
		# Scan the source directory for resources
		def process_dir(dirpath, resname):
			for file in os.listdir(dirpath):
				path = os.path.join(dirpath, file)
				if os.path.isdir(path):
					process_dir(path, resname + "/" + file)
				elif file.endswith(".dr") and os.path.isfile(path):
					has_py = os.path.isfile(path.removesuffix(".dr") + ".py")
					has_meta = os.path.isfile(path.removesuffix(".dr") + ".json")
					name = resname + "/" + file.removesuffix(".dr")
					self.resources[name] = Resource(False, name, has_py, has_meta)
				elif file.endswith(".drc") and os.path.isfile(path):
					name = resname + "/" + file.removesuffix(".drc")
					self.resources[name] = Resource(True, name, False, False)
		process_dir(self.source_dir, "")
		
		# Process the resources
		for res in self.resources.values():
			# 1. Load and parse the resource file
			fs = FileStream(os.path.join(self.source_dir, res.path()))
			lexer = DurakLexer(fs)
			cts = CommonTokenStream(lexer)
			parser = DurakParser(cts)
			visitor = DurakVisitor()
			doc = visitor.visit(parser.document())
			res._doc = doc
			
			# 2. Load the resource metadata file
			if res.has_meta():
				with open(os.path.join(self.source_dir, res.path_meta()), 'r') as fp:
					meta = json.load(fp)
					res._meta = meta
			
			# 3. Load resource model generation python modules
			# (black magic to me, but it works. ask importlib documentation)
			if res.has_py():
				spec = importlib.util.spec_from_file_location(res.name(), os.path.join(self.source_dir, res.path_py()))
				mod = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(mod)
				res._pymod = mod
	
	def _use_component(self, res: Resource, params: dict):
		def visit(x):
			if isinstance(x, Element):
				if x.body is None:
					new_body = None
				else:
					new_body = []
					for ent in x.body:
						new_body.extend(visit(ent))
				return [Element(x.name, x.attributes, new_body)]
			elif isinstance(x, InsertDirective):
				param_name = x.identifier
				replacement_entities = params[param_name]
				return replacement_entities
			elif isinstance(x, IfDirective):
				new_bodies = []
				for body in x.bodies:
					new_body = []
					for ent in body:
						new_body.extend(visit(ent))
					new_bodies.append(new_body)
				if x.else_body is None:
					new_else_body = None
				else:
					new_else_body = []
					for ent in x.else_body:
						new_else_body.extend(visit(ent))
				return [IfDirective(x.conditions, new_bodies, new_else_body)]
			elif isinstance(x, ForeachDirective):
				new_body = []
				for ent in x.body:
					new_body.extend(visit(ent))
				if x.else_body is None:
					new_else_body = None
				else:
					new_else_body = []
					for ent in x.else_body:
						new_else_body.extend(visit(ent))
				return [ForeachDirective(x.varname, x.through, new_body, new_else_body)]
			elif isinstance(x, IncludeDirective):
				if x.body is None:
					new_body = None
				else:
					new_body = []
					for ent in x.body:
						new_body.extend(visit(ent))
				return [IncludeDirective(x.expr, new_body)]
			else:
				return [x]
		
		out = []
		for entity in res.doc().body:
			out.extend(visit(entity))
		
		return out
	
	def _render_resource(self, res: Resource):
		res.status = 'rendering'
		doc = res.doc()
		
		def eval_expr(locals: dict, e: DurakExpr):
			if isinstance(e, ExprOr): return eval_expr(locals, e.left) or eval_expr(locals, e.right)
			if isinstance(e, ExprAnd): return eval_expr(locals, e.left) and eval_expr(locals, e.right)
			if isinstance(e, ExprNot): return not eval_expr(locals, e.expr)
			if isinstance(e, ExprEq): return eval_expr(locals, e.left) == eval_expr(locals, e.right)
			if isinstance(e, ExprNe): return eval_expr(locals, e.left) != eval_expr(locals, e.right)
			if isinstance(e, ExprLt): return eval_expr(locals, e.left) < eval_expr(locals, e.right)
			if isinstance(e, ExprGt): return eval_expr(locals, e.left) > eval_expr(locals, e.right)
			if isinstance(e, ExprLe): return eval_expr(locals, e.left) <= eval_expr(locals, e.right)
			if isinstance(e, ExprGe): return eval_expr(locals, e.left) >= eval_expr(locals, e.right)
			if isinstance(e, ExprAdd): return eval_expr(locals, e.left) + eval_expr(locals, e.right)
			if isinstance(e, ExprSub): return eval_expr(locals, e.left) - eval_expr(locals, e.right)
			if isinstance(e, ExprMult): return eval_expr(locals, e.left) * eval_expr(locals, e.right)
			if isinstance(e, ExprDiv): return eval_expr(locals, e.left) / eval_expr(locals, e.right)
			if isinstance(e, ExprMod): return eval_expr(locals, e.left) % eval_expr(locals, e.right)
			if isinstance(e, ExprDot):
				head = eval_expr(locals, e.head)
				value = head
				for ident in e.tail:
					if hasattr(value, ident):
						attr = getattr(value, ident)
					else:
						attr = value[ident]
					if callable(attr):
						value = attr()
					else:
						value = attr
				return value
			if isinstance(e, ExprIdent):
				ident = e.identifier
				if ident == '_':
					return res.meta()
				elif ident in locals:
					return locals[ident]
				else:
					return res.model()[ident]
			if isinstance(e, ExprLiteral): return e.value
		
		def render(locals: dict, x) -> list:
			if isinstance(x, Comment):
				return []
			if isinstance(x, Element):
				name = x.name
				attributes = []
				for attr in x.attributes:
					attr_name = attr.name
					attr_value = str(eval_expr(locals, attr.value))
					attributes.append(HtmlAttribute(attr_name, attr_value))
				body = []
				for y in x.body:
					body.extend(render(locals, y))
				return [HtmlElement(name, attributes, body)]
			if isinstance(x, IfDirective):
				for cond_expr, cond_body in zip(x.conditions, x.bodies):
					fulfilled = bool(eval_expr(locals, cond_expr))
					if fulfilled:
						body = []
						for ent in cond_body:
							body.extend(render(locals, ent))
						return body
				else:
					if x.else_body is None:
						return []
					body = []
					for ent in x.else_body:
						body.extend(render(locals, ent))
					return body
			if isinstance(x, ForeachDirective):
				varname = x.varname
				coll = eval_expr(locals, x.through)
				if len(coll) == 0 and x.else_body:
					else_body = []
					for ent in x.else_body:
						else_body.extend(render(locals, ent))
					return else_body
				out = []
				new_locals = locals.copy() # shallow copy, that's what we want
				for elem in coll:
					new_locals[varname] = elem
					for ent in x.body:
						out.extend(render(new_locals, ent))
				return out
			if isinstance(x, IncludeDirective):
				comp_resname = str(eval_expr(locals, x.expr))
				compres = self.resources[comp_resname]
				params = dict()
				if x.body is None:
					pass
				for el in x.body:
					if isinstance(el, str):
						continue
					param_name = el.name
					param_body = el.body
					params[param_name] = param_body
				component_replacement = self._use_component(compres, params)
				out = []
				for ent in component_replacement:
					out.extend(render(locals, ent))
				return out
			if isinstance(x, InsertDirective):
				raise Exception("The insert directive can only be used in component resources")
			if isinstance(x, Injection):
				text = str(eval_expr(locals, x.expr))
				return [HtmlText(text)]
			if isinstance(x, str):
				return [HtmlText(x)]
		
		if res.has_py():
			ctx = ResourceContext(self, res)
			cwd = os.getcwd()
			os.chdir(os.path.join(self.source_dir, os.path.dirname(res.path())))
			res._model = res.pymod().generate_model(ctx)
			os.chdir(cwd)
		else:
			res._model = dict()
		
		rendered = []
		for entity in doc.body:
			rendered.extend(render(res.model(), entity))
		
		res.status = 'rendered'
		rendered_str = ''.join(str(x) for x in rendered)
		return rendered_str
	
	def render(self, target_dir: str):
		for res in self.resources.values():
			if res.is_component() or res.status == 'rendered':
				continue
			#rendered = durak_render(self.resources, res)
			rendered = self._render_resource(res)
			outpath = os.path.join(target_dir, res.path_output())
			outpath_dirname = os.path.dirname(outpath)
			if not os.path.isdir(outpath_dirname):
				os.makedirs(outpath_dirname)
			with open(outpath, 'w') as fp:
				fp.write(rendered)

class ResourceContext:
	def __init__(self, durak: Durak, res: Resource):
		self.durak = durak
		self.resource = res
	
	def resolve(self, path: str) -> Resource:
		path = path.removesuffix(".dr")
		me = self.resource.name()
		name = os.path.join(os.path.dirname(me), path)
		return self.durak.resources[name]

def main():
	parser = argparse.ArgumentParser(prog="durak", description="HTML templating language and static site generator.")
	
	parser.add_argument("-v", "--version", action='version', version='Durak 0.1.0')
	parser.add_argument("src_dir", help="path to source directory")
	parser.add_argument("out_dir", help="path to output directory")
	
	args = parser.parse_args()
	
	durak = Durak(args.src_dir)
	durak.render(args.out_dir)
