from pygments.styles import get_style_by_name
from pygments.lexers import guess_lexer

style = get_style_by_name('monokai')

code = "#!/bin/python\n\ndef fn(x):\n  x**2\n\n# That was a fn\n# Yep"
lexer = guess_lexer(code)

tokensource = lexer.get_tokens("def x: return x")
for (ttype, fulltoken) in tokensource:
    style._styles[ttype][0]
    break


    # print(repr(ttype) + ': ' + fulltoken.replace('\n','\\n'))
