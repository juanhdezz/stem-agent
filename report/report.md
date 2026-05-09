# StemAgent



## 1) Introducción

La idea de este reto es imaginar un **agente “célula madre”**. Una célula madre no sabe qué será hasta que observa señales del entorno y se transforma. Del mismo modo, este agente **no nace especializado**: recibe un **tipo de problema** (por ejemplo “QA”, “Seguridad”, “Investigación”) y **aprende a convertirse** en el agente adecuado.

En este proyecto construimos un agente base que:
1. **Descubre** cómo expertos resuelven ese tipo de problema.
2. **Diseña** su propio comportamiento (prompt + herramientas).
3. **Se valida** con métricas objetivas.
4. **Decide cuándo parar** y “cristaliza”.

Escogimos **Code Review / QA** porque es un dominio donde podemos medir resultados fácilmente (precision, recall, F1).

## 2) ¿Qué es un agente en este contexto?

Un agente es un programa que:
- Recibe un input (por ejemplo un fragmento de código).
- Aplica un proceso (prompt + herramientas).
- Devuelve un output (lista de problemas, soluciones, hallazgos).

En nuestro caso, el “ADN” del agente es su **system prompt**. Cambiar ese prompt significa cambiar cómo piensa, qué prioriza y qué devuelve.

## 3) Vista rápida de la arquitectura (dibujo)

```
					  ┌─────────────────────┐
					  │  STEM AGENT (BASE)  │
					  └─────────┬───────────┘
									│
									▼
					 ┌─────────────────────┐
					 │  DISCOVERY NODE     │
					 │  (aprende señales)  │
					 └─────────┬───────────┘
								  ▼
					 ┌─────────────────────┐
					 │   DESIGN NODE       │
					 │  (cambia su ADN)    │
					 └─────────┬───────────┘
								  ▼
					 ┌─────────────────────┐
					 │  VALIDATION NODE    │
					 │ (mide performance)  │
					 └───────┬─────────────┘
								│ score >= threshold
								│
								▼
					 ┌─────────────────────┐
					 │ CRYSTALLIZATION     │
					 │ (exporta agente)    │
					 └─────────────────────┘
```

Si la validación no llega al umbral, el flujo vuelve a **Design** y el agente se vuelve a ajustar.

## 4) Explicación paso a paso de cada fase

### 4.1 Discovery (Descubrimiento)
**Objetivo:** descubrir cómo expertos resuelven ese tipo de problema.

¿Qué hace?
- Busca en la web estrategias, herramientas y patrones comunes.
- El LLM resume la información en una lista breve de ideas.

Esto permite que el agente no “invente” su enfoque desde cero, sino que se base en señales reales.

### 4.2 Design (Diseño)
**Objetivo:** convertir el conocimiento en un agente especializado.

¿Qué genera?
- Un `AgentConfig` con:
  - `system_prompt`
  - herramientas (`tools`)
  - flujo de trabajo (`flow`)

Si el agente ya hizo iteraciones anteriores, el diseño se ajusta usando **métricas reales** del último intento.

### 4.3 Validation (Validación)
**Objetivo:** medir si el agente funciona.

¿Qué hace?
- Ejecuta el agente sobre un benchmark.
- Calcula precision, recall y F1.
- Decide si **se cristaliza** o si vuelve a diseñar.

### 4.4 Crystallization (Cristalización)
**Objetivo:** guardar el agente final.

¿Qué exporta?
- `agent_config.json`
- `system_prompt.txt`

Esto es el agente especializado listo para producción o evaluación.

## 5) Flujo de datos (simplificado)

```
task_class (ej: "code_review")
	│
	▼
Discovery -> discovered_knowledge
	│
	▼
Design -> AgentConfig
	│
	▼
Validation -> score + métricas
	│
	├─ si score >= threshold -> Crystallization
	└─ si score < threshold  -> Design (otra iteración)
```

## 6) Estructura del proyecto explicada por carpetas

```
stem-agent/
├── src/                 # Código principal del agente
│   ├── graph/           # Grafo LangGraph (orquestación)
│   │   ├── nodes/        # Cada fase: discovery, design, validation, crystal
│   │   └── state.py      # Estado global tipado (StemAgentState)
│   ├── models/          # Dataclasses: AgentConfig, EvalResult
│   ├── tools/           # Herramientas auxiliares (web, análisis)
│   └── evaluation/      # Dataset, métricas, runner
│
├── data/
│   ├── benchmark/       # Dataset de evaluación
│   └── outputs/         # Agentes cristalizados + resultados
│
├── scripts/             # Scripts CLI (run_stem_agent, baseline, evaluate)
├── tests/               # Tests unitarios
├── report/              # Este informe
└── README.md            # Documentación general
```

**Resumen rápido de responsabilidades**:
- `src/graph`: decide el flujo de especialización.
- `src/models`: define los “objetos oficiales” del agente.
- `src/tools`: funciones auxiliares que el agente puede usar.
- `src/evaluation`: cómo medimos si el agente es bueno.
- `data/benchmark`: datos de prueba.
- `scripts`: ejecución real.

## 7) Evaluación y métricas

### Baseline
El baseline es un agente genérico con prompt simple. Sirve para comparar “antes” y “después”.

### Métricas principales
- **Precision**: de todo lo que el agente dijo, ¿cuánto era correcto?
- **Recall**: de todo lo correcto posible, ¿cuánto encontró?
- **F1**: balance entre ambos.

### Resultados actuales (benchmark ampliado)

```
precision: 0.788
recall:    0.703
f1:        0.743
```

### Comparación medible (before/after)

| Métrica | Baseline | StemAgent especializado |
| --- | --- | --- |
| Precision | 0.108 | 0.788 |
| Recall | 0.541 | 0.703 |
| F1 | 0.180 | 0.743 |

**Interpretación sencilla**: el agente especializado ya supera claramente al baseline. Esto indica que **la auto‑especialización está funcionando**.

## 8) Lo que salió bien

- El ciclo Discovery → Design → Validation funciona y es estable.
- La cristalización produce un agente reutilizable.
- El agente mejora sus métricas con el proceso de especialización.

## 9) Problemas reales encontrados

- **Precision baja al inicio**: el agente reportaba demasiados issues.
- **Dataset pequeño**: el benchmark original era limitado, por eso lo ampliamos.
- **Etiquetas inconsistentes**: se resolvió con canonicalización.

## 10) Qué haríamos con más tiempo

- Integrar **BugsInPy** para evaluación real.
- Añadir **confidence scoring** para reducir falsos positivos.
- Permitir especialización en dominios no‑QA (seguridad, performance, UX).

## 11) Conclusión

Este proyecto **cumple el reto**: existe un agente base que **se auto‑especializa**, se valida y se cristaliza. Además, el proceso es reproducible y medible. El sistema es extensible y está listo para crecer hacia benchmarks reales y dominios adicionales.
