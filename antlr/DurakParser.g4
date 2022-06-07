parser grammar DurakParser;

options { tokenVocab=DurakLexer; }

document: entity+ EOF;
entity: VERBATIM | element | directive | injection | COMMENT | TEXT;


element
	: TAG_OPEN TAG_NAME tag_attribute* (tag_attribute_last EXPR_TAG_CLOSE | TAG_CLOSE)
	| TAG_OPEN TAG_NAME tag_attribute* (tag_attribute_last EXPR_TAG_END | TAG_END) entity* CLOSING_TAG
;

tag_attribute: TAG_ATTRIBUTE_NAME (TAG_EQ expr EXPR_COLON)?;
tag_attribute_last: TAG_ATTRIBUTE_NAME TAG_EQ expr;


directive: if_directive | foreach_directive | let_directive | include_directive | insert_directive;

if_directive:
	DIRECTIVE_OPEN DIRECTIVE_IF expr EXPR_TAG_END
	main_body+=entity*
	if_directive_elif*
	(DIRECTIVE_OPEN DIRECTIVE_ELSE DIRECTIVE_END else_body+=entity*)?
	CLOSING_TAG
;

if_directive_elif: DIRECTIVE_OPEN DIRECTIVE_ELIF expr EXPR_TAG_END entity*;

foreach_directive:
	DIRECTIVE_OPEN DIRECTIVE_FOREACH DIRECTIVE_FOREACH_IDENTIFIER DIRECTIVE_IN expr EXPR_TAG_END
	main_body+=entity*
	(DIRECTIVE_OPEN DIRECTIVE_ELSE DIRECTIVE_END else_body+=entity*)?
	CLOSING_TAG
;

let_directive:
	DIRECTIVE_OPEN DIRECTIVE_LET
	(idents+=DIRECTIVE_IDENTIFIER DIRECTIVE_EQ vals+=expr EXPR_COLON)*
	idents+=DIRECTIVE_IDENTIFIER DIRECTIVE_EQ vals+=expr EXPR_TAG_END
	body+=entity*
	CLOSING_TAG
;

include_directive
	: DIRECTIVE_OPEN DIRECTIVE_INCLUDE expr EXPR_TAG_CLOSE
	| DIRECTIVE_OPEN DIRECTIVE_INCLUDE expr EXPR_TAG_END (element | COMMENT | TEXT)* CLOSING_TAG
;

insert_directive: DIRECTIVE_OPEN DIRECTIVE_INSERT DIRECTIVE_INSERT_IDENTIFIER DIRECTIVE_CLOSE;


injection: INJECTION_OPEN expr EXPR_TAG_CLOSE;


expr: expr_or;

expr_or
	: left=expr_or EXPR_OR right=expr_and
	| expr_and
;

expr_and
	: left=expr_and EXPR_AND right=expr_not
	| expr_not
;

expr_not
	: EXPR_NOT expr_comp
	| expr_comp
;

expr_comp
	: left=expr_comp op=(EXPR_EQEQ | EXPR_NEQ | EXPR_LT | EXPR_GT | EXPR_LE | EXPR_GE) right=expr_addsub
	| expr_addsub
;

expr_addsub
	: left=expr_addsub op=(EXPR_PLUS | EXPR_MINUS) right=expr_multdiv
	| expr_multdiv
;

expr_multdiv
	: left=expr_multdiv op=(EXPR_STAR | EXPR_SLASH | EXPR_MOD) right=expr_dot
	| expr_dot
;

expr_dot
	: head=expr_dot (EXPR_DOT tail+=EXPR_IDENT)+
	| expr_atom
;

expr_atom: EXPR_LPAREN expr EXPR_RPAREN | EXPR_IDENT | expr_literal;

expr_literal: EXPR_INT_LITERAL | EXPR_FLOAT_LITERAL | EXPR_STRING_LITERAL;
