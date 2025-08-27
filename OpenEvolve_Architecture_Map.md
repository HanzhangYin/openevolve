# OpenEvolve Architecture Map & Customization Guide

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Entry     │───▶│   Controller    │───▶│ Process Workers │
│ openevolve-run  │    │   (Main Loop)   │    │   (Parallel)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Ensemble  │◀───│    Database     │───▶│   Evaluator     │
│  (Multi-Model)  │    │  (MAP-Elites)   │    │  (Your Logic)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Prompt Sampler  │
                       │   (Templates)   │
                       └─────────────────┘
```

## 🔧 Key Components & Their Roles

### 1. **Entry Points** (Where you start)
- **`openevolve-run.py`** → **`cli.py`** → **`OpenEvolve` class**
- Takes: `initial_program.py`, `evaluator.py`, `config.yaml`

### 2. **Controller** (`controller.py` / `process_parallel.py`)
- **Main orchestrator** - runs the evolution loop
- Manages checkpointing, logging, early stopping
- Spawns parallel worker processes for iterations

### 3. **Database** (`database.py`)
- **MAP-Elites implementation** with island-based evolution
- Stores all programs, tracks best performers
- Handles selection (elite, diverse, random)
- **Feature dimensions**: complexity, diversity, custom metrics

### 4. **Evaluator** (`evaluator.py` + **YOUR custom evaluator**)
- **Your domain logic lives here**
- Executes programs and returns metrics
- Supports cascade evaluation (early filtering)
- Returns: `{"score": float, "custom_metric": float, ...}`

### 5. **LLM Ensemble** (`llm/ensemble.py`)
- Manages multiple models with weights
- Handles retries, timeouts, rate limiting
- Uses OpenAI-compatible APIs (Google, OpenAI, etc.)

### 6. **Prompt Sampler** (`prompt/sampler.py`)
- Builds prompts with examples from database
- Template-based with stochasticity
- Includes artifacts (program outputs/errors)

## 🎯 Major Customization Points

### 🔥 **HIGH IMPACT** Customizations:

#### **1. Custom Evaluator** (Most Important!)
**File**: `examples/your_domain/evaluator.py`
```python
def evaluate(program_path, **kwargs):
    """Your domain-specific evaluation logic"""
    # Execute the evolved program
    # Return metrics: {"score": float, "custom_metric": float}
    return {"score": performance, "memory_usage": mem, "accuracy": acc}
```

#### **2. Initial Program** (What gets evolved)
**File**: `examples/your_domain/initial_program.py`
```python
# EVOLVE-BLOCK-START
def your_algorithm():
    # Code that OpenEvolve will evolve
    pass
# EVOLVE-BLOCK-END
```

#### **3. Configuration** (Behavior tuning)
**File**: `config.yaml`
```yaml
# Evolution parameters
llm:
  models: [...]
  temperature: 0.7
  
database:
  feature_dimensions: ["complexity", "your_custom_metric"]
  population_size: 100
  num_islands: 5
  
evaluator:
  timeout: 300
  cascade_thresholds: [0.5, 0.8]
```

### 🛠️ **MEDIUM IMPACT** Customizations:

#### **4. Prompt Templates** 
**Directory**: `openevolve/prompt/templates/`
- Modify how LLM receives examples and instructions
- Add domain-specific guidance

#### **5. Feature Dimensions**
**Location**: Config `database.feature_dimensions`
- Add custom metrics from your evaluator
- Controls diversity in MAP-Elites grid

#### **6. LLM Models**
**Location**: Config `llm.models`
- Switch between different models
- Adjust weights and parameters

### 🔧 **LOW IMPACT** Customizations:

#### **7. Selection Strategy**
**Location**: `database.py` selection methods
- Modify elite/diverse/random ratios
- Change diversity metrics

#### **8. Checkpointing**
**Location**: Controller classes
- Modify save/load behavior
- Add custom metadata

## 🎯 Data Flow Diagram

```
┌─────────────┐
│ Iteration N │
└─────┬───────┘
      │
      ▼
┌─────────────────┐    ┌──────────────────┐
│ 1. Sample       │───▶│ 2. Build Prompt  │
│    Programs     │    │    (Examples +   │
│    from DB      │    │     Templates)   │
└─────────────────┘    └────────┬─────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐
│ 4. Evaluate     │◀───│ 3. LLM Generate  │
│    New Program  │    │    New Program   │
│    (Your Logic) │    │    Code          │
└────────┬────────┘    └──────────────────┘
         │
         ▼
┌─────────────────┐    ┌──────────────────┐
│ 5. Store in DB  │───▶│ 6. Update Best   │
│    (MAP-Elites  │    │    Programs &    │
│     Features)   │    │    Statistics    │
└─────────────────┘    └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ 7. Checkpoint    │
                       │    (Every N      │
                       │     Iterations)  │
                       └──────────────────┘
```

## 🔄 Evolution Process Details

### Iteration Workflow:
1. **Sample Programs**: Database selects elite + diverse + random programs
2. **Build Prompt**: Sampler creates LLM prompt with examples and templates
3. **LLM Generate**: Ensemble generates new program code
4. **Evaluate**: Your custom evaluator tests the new program
5. **Store**: Database maps program to feature grid (MAP-Elites)
6. **Update**: Track best programs and statistics
7. **Checkpoint**: Periodically save state for resuming

### Key Algorithms:
- **MAP-Elites**: Maintains diversity through feature-based grid
- **Island Model**: Multiple populations with periodic migration
- **Cascade Evaluation**: Multi-stage filtering (fast → comprehensive)
- **Template Stochasticity**: Randomized prompt variations

## 📁 File Structure Guide

```
openevolve/
├── openevolve-run.py          # Main entry point
├── openevolve/
│   ├── cli.py                 # Command-line interface
│   ├── controller.py          # Main evolution controller
│   ├── process_parallel.py    # Parallel process management
│   ├── database.py            # MAP-Elites database
│   ├── evaluator.py           # Base evaluator class
│   ├── config.py              # Configuration handling
│   ├── llm/
│   │   ├── ensemble.py        # Multi-model LLM management
│   │   └── openai.py          # OpenAI-compatible API client
│   ├── prompt/
│   │   ├── sampler.py         # Prompt building logic
│   │   └── templates/         # Prompt templates
│   └── utils/                 # Utility functions
├── examples/
│   ├── function_minimization/ # Example optimization problem
│   │   ├── initial_program.py # Starting algorithm
│   │   ├── evaluator.py       # Domain-specific evaluation
│   │   ├── config.yaml        # Problem configuration
│   │   └── openevolve_output/ # Results and checkpoints
│   └── [other_examples]/
└── configs/
    └── default_config.yaml    # Default configuration template
```

## 🚀 Quick Start Customization Template

### Step-by-Step Process:

1. **Copy Example Directory**:
   ```bash
   cp -r examples/function_minimization examples/my_domain
   ```

2. **Modify Evaluator** (`examples/my_domain/evaluator.py`):
   ```python
   def evaluate(program_path, **kwargs):
       # Your domain logic here
       result = run_your_test(program_path)
       return {
           "score": result.performance,
           "custom_metric": result.quality
       }
   ```

3. **Modify Initial Program** (`examples/my_domain/initial_program.py`):
   ```python
   # EVOLVE-BLOCK-START
   def my_algorithm():
       # Starting point algorithm
       pass
   # EVOLVE-BLOCK-END
   ```

4. **Configure** (`examples/my_domain/config.yaml`):
   ```yaml
   database:
     feature_dimensions: ["complexity", "custom_metric"]
   evaluator:
     timeout: 60  # Adjust for your domain
   ```

5. **Run Evolution**:
   ```bash
   python openevolve-run.py \
     examples/my_domain/initial_program.py \
     examples/my_domain/evaluator.py \
     --config examples/my_domain/config.yaml \
     --iterations 100
   ```

## 🎯 Common Customization Patterns

### Pattern 1: **Performance Optimization**
- **Goal**: Optimize algorithm speed/efficiency
- **Key Files**: evaluator.py (timing), config (feature_dimensions)
- **Metrics**: execution_time, memory_usage, operations_count

### Pattern 2: **Accuracy Maximization**
- **Goal**: Improve correctness on test cases
- **Key Files**: evaluator.py (test suite), initial_program.py
- **Metrics**: accuracy, precision, recall, f1_score

### Pattern 3: **Multi-Objective Optimization**
- **Goal**: Balance competing objectives
- **Key Files**: config.yaml (feature_dimensions), evaluator.py
- **Metrics**: Multiple conflicting metrics in feature space

### Pattern 4: **Domain-Specific Languages**
- **Goal**: Evolve non-Python code
- **Key Files**: evaluator.py (compilation/execution), config.yaml (language)
- **Examples**: CUDA kernels, SQL queries, MLIR code

## 🔧 Advanced Customization Points

### Custom Selection Strategies:
- Modify `database.py` selection methods
- Implement domain-specific diversity metrics
- Add problem-specific elite criteria

### Custom Prompt Engineering:
- Create domain templates in `prompt/templates/`
- Add problem-specific examples and guidance
- Implement dynamic prompt adaptation

### Custom LLM Integration:
- Add new model providers in `llm/`
- Implement specialized prompting strategies
- Add domain-specific fine-tuned models

## 📊 Monitoring & Analysis

### Key Metrics to Track:
- **Fitness Progress**: Best/average scores over time
- **Diversity**: Population spread in feature space
- **Convergence**: Rate of improvement
- **Efficiency**: Evaluations per improvement

### Output Analysis:
- **Checkpoints**: Complete system state at intervals
- **Logs**: Detailed execution traces
- **Best Programs**: Evolution of top performers
- **Artifacts**: Program outputs and debugging info

## 🐛 Common Issues & Solutions

### Issue: Slow Evolution
- **Solution**: Reduce population_size, increase cascade_thresholds
- **Files**: config.yaml (database, evaluator sections)

### Issue: Premature Convergence
- **Solution**: Increase diversity, lower exploitation_ratio
- **Files**: config.yaml (database.exploitation_ratio)

### Issue: LLM Generation Failures
- **Solution**: Adjust temperature, improve prompts, add retries
- **Files**: config.yaml (llm section), prompt templates

### Issue: Evaluation Timeouts
- **Solution**: Increase timeout, optimize evaluator, add early stopping
- **Files**: config.yaml (evaluator.timeout), evaluator.py

---

## 📚 Additional Resources

- **CLAUDE.md**: Project-specific instructions and commands
- **README.md**: General usage and setup
- **Examples/**: Working demonstrations for various domains
- **Tests/**: Unit tests showing component usage
- **Configs/**: Template configurations for different scenarios

---

*This architecture map provides a comprehensive guide to understanding and customizing OpenEvolve for your specific domain. Focus on the HIGH IMPACT customizations first, then expand to more advanced modifications as needed.*