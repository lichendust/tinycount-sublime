# ✒️ Tiny Count

A simple, no-nonsense word count plugin for Sublime Text.

- Selections: Tiny Count measures the whole buffer, but will also report on any active selections as they become available.
- Ignores comments: in Markdown, [Fountain](https://github.com/qxoko/meander-sublime), or any other active syntaxes, whole-line and block comments won't count toward the total[^1].

[^1]: Comments *inside* a sentence still do because it would massive increase the complexity and that's not something I want to do right now.  Word counting is already innaccurate business at best anyway.
