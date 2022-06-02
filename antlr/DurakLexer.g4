lexer grammar DurakLexer;

//TODO: whitespace -- maybe should be ()* or ()+ ?

COMMENT: '<!--' .*? '-->';
VERBATIM: '<!>' .*? '<!/>';
CLOSING_TAG: '</>';
DIRECTIVE_OPEN: '<!' -> pushMode(IN_DIRECTIVE);
INJECTION_OPEN: '<$' -> pushMode(IN_EXPR), pushMode(IN_EXPR);
TAG_OPEN: '<' -> pushMode(ON_TAG);
TEXT: ~[<]+;

mode ON_TAG;

TAG_NAME: [a-zA-Z0-9_-]+ -> popMode, pushMode(IN_TAG);

mode IN_TAG;

TAG_END: '>' -> popMode;
TAG_CLOSE: '/>' -> popMode;
TAG_EQ: '=' -> pushMode(IN_EXPR);
TAG_ATTRIBUTE_NAME: [a-zA-Z0-9_-]+;
TAG_WS: [ \t\n\r] -> skip;

mode IN_DIRECTIVE;

DIRECTIVE_IF: 'if' -> pushMode(IN_EXPR);
DIRECTIVE_ELIF: 'elif' -> pushMode(IN_EXPR);
DIRECTIVE_ELSE: 'else';
DIRECTIVE_FOREACH: 'foreach' -> pushMode(IN_DIRECTIVE_FOREACH_IDENTIFIER);
DIRECTIVE_IN: 'in' -> pushMode(IN_EXPR);
DIRECTIVE_INCLUDE: 'include' -> pushMode(IN_EXPR);
DIRECTIVE_INSERT: 'insert' -> pushMode(IN_DIRECTIVE_INSERT_IDENTIFIER);
DIRECTIVE_END: '>' -> popMode;
DIRECTIVE_CLOSE: '/>' -> popMode;
DIRECTIVE_WS: [ \t\n\r] -> skip;

mode IN_DIRECTIVE_FOREACH_IDENTIFIER;
DIRECTIVE_FOREACH_IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]* -> popMode;
DIRECTIVE_FOREACH_WS: [ \t\n\r] -> skip;

mode IN_DIRECTIVE_INSERT_IDENTIFIER;
DIRECTIVE_INSERT_IDENTIFIER: [a-zA-Z0-9_-]+ -> popMode;
DIRECTIVE_INSERT_WS: [ \t\n\r] -> skip;

// It's kinda scuffed, but in order for both <$.../> and expressions in <!...> to work and be
// parsed by the same mode, there is sometimes an extra IN_EXPR mode on the stack, and two modes
// are always popped when IN_EXPR sees a '>' or '/>'. Only one is popped when it sees a ';';
mode IN_EXPR;

EXPR_LPAREN: '(';
EXPR_RPAREN: ')';
EXPR_PLUS: '+';
EXPR_MINUS: '-';
EXPR_STAR: '*';
EXPR_SLASH: '/';
EXPR_MOD: 'mod';
EXPR_DOT: '.';
EXPR_EQEQ: '==';
EXPR_NEQ: '!=';
EXPR_LT: '<<';
EXPR_GT: '>>';
EXPR_LE: '<=';
EXPR_GE: '>=';
EXPR_NOT: 'not';
EXPR_AND: 'and';
EXPR_OR: 'or';
EXPR_COLON: ';' -> popMode;
EXPR_TAG_END: '>' -> popMode, popMode;
EXPR_TAG_CLOSE: '/>' -> popMode, popMode;
EXPR_INT_LITERAL: [0-9]+;
EXPR_FLOAT_LITERAL: [0-9]+ '.' [0-9]+;
EXPR_STRING_LITERAL: '"' ~["]* '"' | '\'' ~[']* '\'';
EXPR_WS: [ \t\n\r] -> skip;
EXPR_IDENT: [a-zA-Z_][a-zA-Z0-9_]*;
