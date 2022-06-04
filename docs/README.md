# Durak Documentation

## The Basics
The entirety of your website's sources has to be in one directory (although symlinks should work),
and can nest subdirectories however deep you want. Here is an example file layout for a website:

```
my-website/
	foo/
		bar.dr
		bar.py
		bar.json
	baz/
		foobar.dr
		foobar.json
	foobar.dr
```

There are two types of resources – site resources and component resources. Each `.dr` file is a
site resource, and each `.drc` file is a component resource. Each site resource will correspond
to exactly one HTML file in the output, meanwhile component resources do not make for output by
themselves, but are used by other resources instead. Every resource has a name, which is just `/`
followed by its path in the source directory without the `.dr` or `.drc` extension.

### Site Resources

#### Resource Template
The site resource template is contained in its `.dr` source file. The template language used is
described later in the documentation.

#### Resource Metadata
Each site resource may be accompanied by a `.json` file right next to it, which can contain
arbitrary data (in JSON format) to be accessed from inside expressions in the template as the
variable `_`.

#### Resource Model
The site resource's template can make use of the resource's *model* inside expressions. The model is
generated using a `.py` file located right next to the template file. It is completely optional; if
there is no `.py` file, the model is just empty. The file should contain Python code defining a
function called `generate_model` taking exactly one argument and returning a `dict`. More
information on model generation can be found later in the documentation.

### Component Resources
Component resources cannot have metadata or model generators. A component resource comprises only
of a `.drc` file containing its template.

## The Template Language
Durak uses its own template language for resources. It is similar to HTML and XML – every document
is hierarchically structured.

### Comments
Comments are text that is ignored for the actual output. A comment starts with `<!--` and ends with
`-->`.
```dr
<!-- Hello, I'm a comment -->
```

### Verbatim blocks
Verbatim blocks are blocks of text that are copied into the output exactly as-is – their content is
not parsed. They begin with `<!>` and end with `<!/>`.
```dr
<!><!DOCTYPE html><!/>
```

### Elements
In general, elements directly correspond to HTML elements on the output. They can either appear in
the form of a closed tag, or an opening tag, body and closing tag. They look almost exactly the
same as in HTML, but note that a closing tag is always `</>` (you don't repeat the element's name).
An element can have attributes (that correspond 1:1 to HTML attributes), whose values are not just
strings, but can be full expressions. If an attribute that is not the last one in the tag has a
value, it needs to be followed semicolon. Attributes don't have to have values. In fact, when an
attribute's value is `None`, it appears in the output HTML as if it had no value.
```dr
<!-- A closed tag: -->
<hr/>

<!-- A tag with a body: -->
<b>Hello</>

<!-- With attributes: >
<a download id=("link-" + foo.id); href=foo.link>...</>
```

### Injections
An injection is starts with `<$` and ends with `/>`, between which lies an expression. The
expression language is described later.
```dr
<$ 4 + 2 />
<$foo/>
```

### Directives
All directives start with `<!`, which is followed by different syntax depending on the directive.

#### `if` Directives
The `if` directive can be used to output different content depending on an expression's value.
Python's `bool` is called on the value of the `if ...` and `elif ...` expressions during rendering
and that is used to decide which branch is rendered.
```dr
<!if x >= 10>
	A lot
<!elif x >= 3>
	A few
<!elif x == 2>
	A couple
<!elif x == 1>
	One
<!else>
	None
</>
```

#### `foreach` Directives
The `foreach` directive can be used to iterate through a collection and render its body multiple
times using a different value for a variable. They can also have `<!else>` sections that are
rendered instead of the main body when the given collection is empty (when `len(collection) == 0`).
```dr
<!foreach foo in _.foos>
	<a href=foo.href><$ foo.name /></>
<!else>
	No foo :(
</>
```

#### `include` Directives
You can make use of component resources with the `include` directive. It can either be a closed tag
or a tag with a body of elements whose contents are used to replace `insert` tags in the component.
`<!include` is followed by an expression evaluating to a string containing the name of the component
resource.
```dr
<!include "/header" />
<!include "/foobar">
	<foo>Some foo.</>
	<bar>A bar.</>
</>
```

#### `insert` Directives
`insert` directives can only appear in component resources' templates. They are replaced by the
content of a corresponding element when the component resource is included using an `include`
directive. `<!insert` is followed by an element name and `/>`.
```dr
<html>
<head><title><!insert title/></></>
<body>
	<h1><!insert title/></>
	<!insert body />
</>
</>
```

## Model Generation
Site resources can have model generators, which are python files containing a global
`generate_model` function taking one argument and returning a `dict`. The argument is a
`ResourceContext` object, which you can use to access the `Resource` whose model is currently being
generated and the `Durak` object which, among other things, contains a `dict` of all the
`Resource`s. You can look at the code to see what's in store.

## The Expression Language
Operators: (operator associativity and priority the same as in Python)
- `(`, `)`
- `+`, `-`, `*`, `/`, `and`, `or`, `==`, `!=`, `>=`, `<=` – binary operators working exactly like their Python equivalents.
- `<<`, `>>` – also binary, work like Python `<` and `>` respectively
- `not` – unary, works like Python's `not`
- `.` – binary, works like Python's `.` if the left hand side has the attribute, and like `[]`
  if it does not. Also, if the value of that is a function, it is called without arguments and the
  value of that is taken.

There are integer literals, float literals and string literals. Currently no escaping or
interpolation is supported for string literals and float literals can't use scientific notation.
