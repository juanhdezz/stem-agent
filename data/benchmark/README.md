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

## Cómo añadir nuevos samples
1. Agrega una línea JSON válida en `samples.jsonl`.
2. Incluye un snippet de Python con un issue real.
3. Añade `expected_issues` descriptivos y `metadata` consistente.
