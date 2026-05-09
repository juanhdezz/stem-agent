# Benchmark Dataset

Este dataset usa archivos JSONL con la estructura:

```json
{"code": "...", "expected_issues": ["..."], "metadata": {"difficulty": "easy", "category": "logic"}}
```

## Categorías de issues
- logic
- security
- style
- maintainability
- reliability
- performance

## Etiquetas canónicas recomendadas
- off-by-one: range excludes n
- division by zero when values is empty
- SQL injection risk via string formatting
- file handle is not closed (use context manager)
- path traversal risk when filename is user-controlled
- use 'is None' when comparing to None
- crashes when scores is empty
- mutates input list 'a' unexpectedly
- send is undefined and will raise NameError
- function lacks default argument but mutates shared list, example confusing
- mutable default argument causes shared state
- bare except hides errors
- shell injection risk via shell=True
- missing handling for empty iterable
- missing None check before attribute access
- platform-specific path handling
- sensitive data logged to stdout
- string concatenation without type casting
- broad exception swallowing
- unsafe yaml load without SafeLoader
- mass assignment without validation
- linear search could be slow for large lists
- nested loops could be inefficient

## Cómo añadir nuevos samples
1. Agrega una línea JSON válida en `samples.jsonl`.
2. Incluye un snippet de Python con un issue real.
3. Añade `expected_issues` descriptivos y `metadata` consistente.
