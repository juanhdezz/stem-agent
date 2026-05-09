# 🧬 StemAgent — Agente Base Auto-Especializable

> Dominio elegido: **Code Review / QA automatizado**

---

## 📋 Índice

1. [El Problema](#el-problema)
2. [Entregables Requeridos](#entregables-requeridos)
3. [Criterios de Evaluación](#criterios-de-evaluación)
4. [Nuestro Enfoque](#nuestro-enfoque)
5. [Arquitectura](#arquitectura)
6. [Stack Tecnológico](#stack-tecnológico)
7. [Estructura del Proyecto](#estructura-del-proyecto)
8. [Setup e Instalación](#setup-e-instalación)
9. [Cómo Ejecutar](#cómo-ejecutar)
10. [Métricas y Evaluación](#métricas-y-evaluación)
11. [Decisiones de Diseño](#decisiones-de-diseño)

---

## El Problema

### Enunciado original (JetBrains)

> *"Una célula madre no sabe en qué se convertirá. Interpreta señales de su entorno y se transforma [...] ¿Y si los agentes de IA funcionaran de la misma manera?"*

El reto pide construir un **agente base mínimo** que, dado una **clase de problemas** (no una tarea concreta), sea capaz de:

1. **Descubrir** cómo los expertos abordan ese tipo de problema
2. **Decidir** qué arquitectura, herramientas y habilidades necesita
3. **Reconstruirse** a sí mismo adoptando esa especialización
4. **Validarse** antes de declararse listo para ejecutar
5. **Ejecutar** ya como agente especializado

El resultado **no** es un agente universal: es un agente que se ha vuelto específico mediante su propio proceso. Para una clase diferente de tareas, se crearía un nuevo agente base desde cero.

### Preguntas clave que plantea el reto

- ¿Cómo descubre el agente la forma habitual de abordar su dominio?
- ¿Cómo decide qué arquitectura, herramientas y habilidades adoptar?
- ¿Cómo se reconstruye sin fallar en el proceso?
- ¿Cómo sabe cuándo está suficientemente especializado para parar?


---

## El Enfoque

### Dominio elegido: Code Review / QA automatizado

**¿Por qué este dominio?**

- **Medible objetivamente**: existen benchmarks públicos (SWE-bench, CodeReviewer dataset, BugsInPy) con ground truth
- **Relevante para JetBrains**: el core de su negocio son herramientas de desarrollo; un agente de QA resuena directamente
- **Rico en estrategias diversas**: hay múltiples enfoques documentados (análisis estático, revisión semántica, detección de patrones, etc.) que justifican una fase de descubrimiento real
- **Complejidad controlable**: el scope puede acotarse (Python, un tipo de bug, un tamaño de PR)

### La metáfora aplicada

```
AGENTE BASE (célula madre)
    │
    ├─ Recibe: "quiero especializarme en Code Review"
    │
    ├─ FASE 1 - DISCOVERY
    │   ¿Cómo hacen code review los expertos?
    │   ¿Qué herramientas usan? ¿Qué taxonomías de bugs existen?
    │   ¿Qué heurísticas aplican los mejores reviewers humanos?
    │
    ├─ FASE 2 - DESIGN  
    │   Propone: system prompt especializado, herramientas a usar,
    │   flujo de análisis, criterios de aceptación
    │
    ├─ FASE 3 - VALIDATION
    │   Se evalúa contra N ejemplos etiquetados
    │   Si no supera el umbral → itera el diseño
    │   Si supera el umbral → cristaliza
    │
    └─ RESULTADO: Agente especializado en Code Review
        (system prompt fijo, herramientas seleccionadas, flujo definido)
```

---

## Arquitectura

### Visión general

```
┌─────────────────────────────────────────────────────────────────┐
│                         STEM AGENT                              │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  DISCOVERY   │───▶│    DESIGN    │───▶│   VALIDATION     │  │
│  │    NODE      │    │    NODE      │    │     NODE         │  │
│  │              │    │              │    │                  │  │
│  │ - Web search │    │ - Genera     │    │ - Evalúa contra  │  │
│  │ - Lee docs   │    │   system     │    │   benchmark      │  │
│  │ - Extrae     │    │   prompt     │    │ - Calcula        │  │
│  │   patrones   │    │ - Selecciona │    │   métricas       │  │
│  │   y estrateg.│    │   tools      │    │ - Decide si      │  │
│  │              │    │ - Define     │    │   iterar o       │  │
│  │              │    │   flujo      │    │   cristalizar    │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                  │              │
│                          ┌───────────────────────┘              │
│                          ▼                                      │
│                   ¿Score >= umbral?                             │
│                    NO ──▶ DESIGN (itera, max K rondas)         │
│                    SÍ ──▶ CRYSTALLIZATION                       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   CRYSTALLIZATION                        │   │
│  │  Exporta el agente especializado:                        │   │
│  │  - system_prompt.txt (final, optimizado)                 │   │
│  │  - agent_config.json (herramientas, parámetros)          │   │
│  │  - Agente ejecutable listo para producción               │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Grafo de estados (LangGraph)

```
START
  │
  ▼
[discovery_node]
  │  knowledge: List[str]  (estrategias, herramientas, patrones encontrados)
  ▼
[design_node]
  │  draft_config: AgentConfig  (system_prompt, tools, flow)
  ▼
[validation_node]
  │  score: float  (métrica elegida, e.g. F1 en dataset de evaluación)
  │
  ├─── score < threshold ──▶ [design_node]  (bucle, máx. MAX_ITERATIONS)
  │
  └─── score >= threshold ──▶ [crystallization_node]
                                      │
                                    END
```

### Estado del grafo

```python
class StemAgentState(TypedDict):
    # Input
    task_class: str                    # "code_review", "security", etc.
    
    # Discovery
    discovered_knowledge: List[str]    # Estrategias y patrones encontrados
    
    # Design (evoluciona entre iteraciones)
    current_config: AgentConfig        # system_prompt + tools + flow
    iteration: int                     # Número de iteración actual
    
    # Validation
    eval_results: List[EvalResult]     # Historial de evaluaciones
    current_score: float               # Score de la iteración actual
    
    # Output
    final_config: Optional[AgentConfig]  # Config cristalizada
    is_crystallized: bool
```

---

## Stack Tecnológico

| Componente | Tecnología | Razón |
|------------|------------|-------|
| **Orquestación de agente** | LangGraph | Control explícito del grafo de estados, fácil de inspeccionar y debuggear |
| **LLM backbone** | OpenAI API (GPT-4o) | Potencia necesaria para razonamiento meta y generación de prompts |
| **Búsqueda web** | Tavily API | Integración nativa con LangGraph, resultados limpios para el agente |
| **Evaluación** | Dataset personalizado + métricas automáticas | Ground truth propio sobre el dominio elegido |
| **Lenguaje** | Python 3.11+ | Ecosistema más maduro para agentes LLM |
| **Config & secrets** | python-dotenv | Gestión limpia de API keys |
| **Testing** | pytest | Pruebas unitarias de cada nodo |

### Por qué LangGraph y no un SDK directo

LangGraph ofrece:
- **Estado explícito y tipado**: el `State` del grafo es auditable en cada paso
- **Ciclos controlados**: el bucle `validation → design` es un ciudadano de primera clase
- **Streaming y observabilidad**: logs nativos de cada nodo sin instrumentación manual
- **Separación de concerns**: cada fase del agente (discovery, design, validation) es un nodo independiente, testeable por separado

---

## Estructura del Proyecto

```
stem-agent/
│
├── README.md                    # Este archivo
│
├── .env.example                 # Variables de entorno requeridas
├── requirements.txt             # Dependencias Python
│
├── src/
│   ├── __init__.py
│   │
│   ├── graph/                   # LangGraph: definición del grafo
│   │   ├── __init__.py
│   │   ├── state.py             # StemAgentState y tipos auxiliares
│   │   ├── graph.py             # Construcción del StateGraph
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── discovery.py     # Nodo: búsqueda y síntesis de conocimiento
│   │       ├── design.py        # Nodo: generación de AgentConfig
│   │       ├── validation.py    # Nodo: evaluación y decisión de cristalizar
│   │       └── crystallization.py  # Nodo: exportación del agente final
│   │
│   ├── models/                  # Tipos de datos compartidos
│   │   ├── __init__.py
│   │   ├── agent_config.py      # AgentConfig, ToolSpec, FlowStep
│   │   └── eval_result.py       # EvalResult, Metric
│   │
│   ├── tools/                   # Herramientas disponibles para el agente
│   │   ├── __init__.py
│   │   ├── web_search.py        # Búsqueda web (Tavily)
│   │   ├── code_analysis.py     # Análisis estático básico
│   │   └── prompt_generator.py  # Generación y refinamiento de prompts
│   │
│   └── evaluation/              # Sistema de evaluación
│       ├── __init__.py
│       ├── dataset.py           # Carga del dataset de benchmark
│       ├── metrics.py           # F1, precision, recall, etc.
│       └── runner.py            # Ejecuta el agente candidato contra el dataset
│
├── data/
│   ├── benchmark/               # Dataset de evaluación (PR/código + labels)
│   │   ├── samples.jsonl        # Ejemplos: {code, expected_issues, metadata}
│   │   └── README.md            # Descripción del dataset
│   └── outputs/                 # Agentes cristalizados (generados en runtime)
│       └── .gitkeep
│
├── experiments/                 # Notebooks de análisis y experimentos
│   ├── 01_baseline.ipynb        # Agente naive antes de especialización
│   └── 02_evolution_trace.ipynb # Trazas de las iteraciones de evolución
│
├── tests/
│   ├── test_discovery.py
│   ├── test_design.py
│   ├── test_validation.py
│   └── test_full_graph.py
│
├── scripts/
│   ├── run_stem_agent.py        # Entry point principal
│   ├── run_baseline.py          # Ejecuta el agente naive para comparación
│   └── evaluate_final.py        # Evalúa el agente cristalizado final
│
└── report/
    └── report.md                # Informe final (máx. 4 páginas)
```

---

## Setup e Instalación

### Prerrequisitos

- Python 3.11+
- API keys: OpenAI, Tavily

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/stem-agent.git
cd stem-agent

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

### Variables de entorno (`.env`)

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Parámetros del agente (opcionales, tienen defaults)
MAX_ITERATIONS=5
VALIDATION_THRESHOLD=0.70
EVAL_DATASET_PATH=data/benchmark/samples.jsonl
```

---

## Cómo Ejecutar

### Ejecutar el agente base completo (especialización)

```bash
python scripts/run_stem_agent.py --task-class code_review
```

El script imprimirá el progreso de cada fase e indicará cuántas iteraciones necesitó para cristalizar. El agente resultante se guarda en `data/outputs/`.

### Ejecutar el baseline (agente naive, para comparación)

```bash
python scripts/run_baseline.py
```

Ejecuta un agente GPT-4o con un system prompt genérico sobre el mismo dataset. Sus métricas son el "antes".

### Evaluar el agente cristalizado final

```bash
python scripts/evaluate_final.py --config data/outputs/latest/agent_config.json
```

Produce la tabla de métricas "después" para incluir en el informe.

---

## Métricas y Evaluación

### Dataset

El dataset de evaluación contiene fragmentos de código Python con bugs/issues reales y una lista de problemas esperados etiquetados manualmente. Fuente: combinación de BugsInPy y ejemplos sintéticos cubriendo:

- Bugs lógicos (off-by-one, condiciones incorrectas)
- Problemas de estilo y mantenibilidad
- Vulnerabilidades de seguridad simples (SQL injection, path traversal)
- Code smells (funciones demasiado largas, duplicación)

### Métricas principales

| Métrica | Descripción | Objetivo |
|---------|-------------|---------|
| **Precision** | De los issues reportados, ¿cuántos son reales? | Minimizar falsos positivos |
| **Recall** | De los issues reales, ¿cuántos detectó? | No perder bugs críticos |
| **F1-score** | Media armónica de precision y recall | Métrica de optimización principal |
| **Issue Categorization Accuracy** | ¿Clasifica correctamente el tipo de issue? | Calidad del análisis |

### Umbral de cristalización

El agente se considera suficientemente especializado cuando alcanza **F1 ≥ 0.70** en el dataset de validación. Este umbral es deliberado: exige mejora real sobre el baseline naive (que estimamos en F1 ~0.35-0.45) sin requerir perfección imposible.

---

## Decisiones de Diseño

Esta sección documenta las decisiones clave y su razonamiento (ampliado en el informe final).

### ¿Por qué Code Review y no Deep Research o Security?

Deep Research: difícil de evaluar objetivamente. Security: requiere datasets especializados de acceso complicado. Code Review tiene benchmarks públicos, métricas automáticas claras y relevancia directa para JetBrains.

### ¿Por qué LangGraph y no CrewAI o AutoGen?

LangGraph ofrece control explícito del grafo, sin magia implícita. Los bucles de iteración (`validation → design`) son ciudadanos de primera clase. El estado es tipado y auditable. Para un reto donde el proceso importa tanto como el resultado, la transparencia del grafo es esencial.

### ¿Por qué el agente modifica su propio system prompt?

Es la forma más directa de implementar la metáfora: el agente "se reconstruye" editando las instrucciones que definen su comportamiento. El system prompt es el ADN del agente; modificarlo es especializarse.

### ¿Por qué un umbral fijo (F1 ≥ 0.70) como criterio de parada?

Un criterio de parada subjetivo ("cuando crea que está listo") sería imposible de evaluar. Un umbral fijo hace el proceso reproducible y la comparación antes/después completamente objetiva. El valor 0.70 es un balance entre ambición y viabilidad en un reto de tiempo limitado.

---

## Contexto para el Agente

> **Nota para uso como contexto**: Este README contiene toda la información necesaria para entender el problema, el enfoque y la arquitectura. Al iniciar una nueva sesión de trabajo, proporcionar este documento como contexto es suficiente para retomar el diseño y la implementación desde cualquier punto.

**Estado actual del proyecto**: Fase de diseño / inicio de implementación  
**Próximo paso**: Implementar `StemAgentState` y el nodo `discovery_node`  
**Decisiones pendientes**: Tamaño y composición definitivos del dataset de benchmark

---

*Desarrollado por Juan Hernández Sánchez-Agesta*
