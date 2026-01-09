# Project Architecture Improvements & Modularization Plan

**Date:** 2026-01-09
**Status:** Proposal for Discussion

## 🎯 Overview

Comprehensive plan for improving the mobile-observe-test-framework architecture through modularization, separation of concerns, and enhanced extensibility.

---

## 1. 📦 Module Restructuring

### Current Structure Issues:
- Monolithic `framework/` directory with many sub-packages
- Mixed responsibilities (analysis, generation, integration, CLI)
- Tight coupling between components
- Hard to test individual components

### Proposed Structure:

```
mobile-test-recorder/
├── recorder/                    # Core recording & observation logic
│   ├── __init__.py
│   ├── observers/              # Platform-specific observers
│   │   ├── android_observer.py
│   │   ├── ios_observer.py
│   │   └── base_observer.py
│   ├── capture/                # Event capture & processing
│   │   ├── event_processor.py
│   │   ├── network_interceptor.py
│   │   └── ui_hierarchy_capture.py
│   └── exporters/              # Export to different formats
│       ├── json_exporter.py
│       ├── yaml_exporter.py
│       └── har_exporter.py
│
├── analyzer/                    # Static & dynamic analysis (NEW!)
│   ├── __init__.py
│   ├── static/                 # Static code analysis
│   │   ├── ast_analyzer.py
│   │   ├── business_logic_analyzer.py
│   │   ├── android/
│   │   │   ├── kotlin_analyzer.py
│   │   │   └── java_analyzer.py
│   │   └── ios/
│   │       ├── swift_analyzer.py
│   │       └── objc_analyzer.py
│   ├── dynamic/                # Runtime analysis
│   │   ├── performance_analyzer.py
│   │   ├── security_analyzer.py
│   │   └── visual_analyzer.py
│   └── integrators/            # Cross-reference static + dynamic
│       ├── model_enricher.py
│       ├── api_correlator.py
│       └── flow_detector.py
│
├── model/                       # Data models (EXTRACTED)
│   ├── __init__.py
│   ├── app_model.py            # Core AppModel
│   ├── element.py              # Element, Selector, Action
│   ├── api.py                  # APICall, APIContract
│   ├── flow.py                 # Flow, StateMachine
│   ├── validation.py           # Model validators
│   └── serializers.py          # Pydantic serializers
│
├── generators/                  # Code generation (EXTRACTED)
│   ├── __init__.py
│   ├── templates/              # Jinja2 templates
│   │   ├── page_object.py.j2
│   │   ├── api_client.py.j2
│   │   ├── test_case.py.j2
│   │   └── bdd_feature.feature.j2
│   ├── page_object_gen.py
│   ├── api_client_gen.py
│   ├── bdd_gen.py
│   ├── test_gen.py
│   └── base_generator.py       # Abstract generator
│
├── cli/                         # CLI interface (EXTRACTED)
│   ├── __init__.py
│   ├── main.py                 # Main CLI entry
│   ├── commands/               # Command groups
│   │   ├── __init__.py
│   │   ├── analyze.py
│   │   ├── record.py
│   │   ├── generate.py
│   │   ├── project.py
│   │   └── healing.py
│   ├── formatters/             # Output formatters
│   │   ├── table_formatter.py
│   │   ├── json_formatter.py
│   │   └── progress_display.py
│   └── utils.py
│
├── ml/                          # Machine learning (KEEP)
│   ├── __init__.py
│   ├── element_classifier.py
│   ├── pattern_recognizer.py
│   ├── selector_healer.py
│   └── training/
│       ├── data_generator.py
│       └── model_trainer.py
│
├── healing/                     # Self-healing (KEEP)
│   ├── __init__.py
│   ├── element_matcher.py
│   ├── failure_analyzer.py
│   ├── selector_discovery.py
│   └── orchestrator.py
│
├── integrations/                # Third-party integrations (NEW!)
│   ├── __init__.py
│   ├── ci/                     # CI/CD integrations
│   │   ├── github_actions.py
│   │   ├── gitlab_ci.py
│   │   └── jenkins.py
│   ├── cloud/                  # Cloud testing platforms
│   │   ├── browserstack.py
│   │   ├── saucelabs.py
│   │   └── aws_device_farm.py
│   ├── test_frameworks/        # Test framework adapters
│   │   ├── pytest_adapter.py
│   │   ├── unittest_adapter.py
│   │   └── robot_adapter.py
│   └── reporting/              # Reporting integrations
│       ├── allure.py
│       ├── junit.py
│       └── slack_notifier.py
│
├── utils/                       # Shared utilities (NEW!)
│   ├── __init__.py
│   ├── file_utils.py
│   ├── path_utils.py
│   ├── string_utils.py
│   ├── validation.py
│   └── logging_config.py
│
├── config/                      # Configuration (NEW!)
│   ├── __init__.py
│   ├── settings.py             # Global settings
│   ├── defaults.yaml           # Default configuration
│   └── schema.py               # Config validation
│
└── tests/                       # Tests
    ├── unit/
    ├── integration/
    └── fixtures/
```

---

## 2. 🔌 Plugin Architecture

### Goal: Make framework extensible without modifying core code

### Proposed Plugin System:

```python
# framework/plugins/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class Plugin(ABC):
    """Base plugin interface"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute plugin logic"""
        pass


class AnalyzerPlugin(Plugin):
    """Plugin for custom analyzers"""
    
    @abstractmethod
    def analyze(self, source_path: Path) -> Dict[str, Any]:
        """Analyze source code"""
        pass


class GeneratorPlugin(Plugin):
    """Plugin for custom generators"""
    
    @abstractmethod
    def generate(self, model: AppModel, output_path: Path) -> List[Path]:
        """Generate code from model"""
        pass


class FormatterPlugin(Plugin):
    """Plugin for custom output formatters"""
    
    @abstractmethod
    def format(self, data: Any) -> str:
        """Format data for display"""
        pass
```

### Plugin Discovery:

```python
# framework/plugins/manager.py
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type, List

class PluginManager:
    """Manages plugin discovery and lifecycle"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_dirs = [
            Path("~/.observe/plugins").expanduser(),
            Path("./plugins"),
        ]
    
    def discover_plugins(self) -> None:
        """Discover plugins from plugin directories"""
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for finder, name, ispkg in pkgutil.iter_modules([str(plugin_dir)]):
                try:
                    module = importlib.import_module(name)
                    if hasattr(module, 'Plugin'):
                        plugin = module.Plugin()
                        self.register_plugin(plugin)
                except Exception as e:
                    logger.warning(f"Failed to load plugin {name}: {e}")
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name} v{plugin.version}")
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugins"""
        return list(self.plugins.keys())
```

### Usage Example:

```python
# Custom analyzer plugin
# ~/.observe/plugins/custom_analyzer.py
from observe.plugins import AnalyzerPlugin

class CustomAnalyzer(AnalyzerPlugin):
    name = "custom-analyzer"
    version = "1.0.0"
    
    def analyze(self, source_path: Path) -> Dict[str, Any]:
        # Custom analysis logic
        return {
            "custom_metrics": {...},
            "findings": [...],
        }

Plugin = CustomAnalyzer  # Export for discovery
```

---

## 3. 🎨 Adapter Pattern for Test Frameworks

### Goal: Seamlessly integrate with existing test frameworks

```python
# integrations/test_frameworks/base.py
from abc import ABC, abstractmethod

class TestFrameworkAdapter(ABC):
    """Base adapter for test frameworks"""
    
    @abstractmethod
    def detect(self, project_path: Path) -> bool:
        """Detect if this framework is used in project"""
        pass
    
    @abstractmethod
    def extract_tests(self, project_path: Path) -> List[TestCase]:
        """Extract existing test cases"""
        pass
    
    @abstractmethod
    def generate_test(self, test_spec: TestSpec, output_path: Path) -> Path:
        """Generate test in framework-specific format"""
        pass
    
    @abstractmethod
    def run_tests(self, test_paths: List[Path]) -> TestResults:
        """Run tests using framework"""
        pass
```

---

## 4. 📊 Event-Driven Architecture

### Goal: Decouple components using event system

```python
# framework/events/bus.py
from typing import Callable, Dict, List
from dataclasses import dataclass
from enum import Enum

class EventType(Enum):
    ANALYSIS_STARTED = "analysis.started"
    ANALYSIS_COMPLETED = "analysis.completed"
    MODEL_ENRICHED = "model.enriched"
    CODE_GENERATED = "code.generated"
    TEST_EXECUTED = "test.executed"
    HEALING_TRIGGERED = "healing.triggered"

@dataclass
class Event:
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime

class EventBus:
    """Central event bus for pub/sub messaging"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
    
    def publish(self, event: Event) -> None:
        """Publish event to subscribers"""
        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")
```

### Usage:

```python
# Subscriber
event_bus.subscribe(
    EventType.ANALYSIS_COMPLETED,
    lambda e: generate_report(e.data['results'])
)

# Publisher
event_bus.publish(Event(
    type=EventType.ANALYSIS_COMPLETED,
    data={'results': analysis_results},
    timestamp=datetime.now()
))
```

---

## 5. 🔧 Configuration Management

### Multi-level Configuration System:

```python
# config/settings.py
from pydantic import BaseSettings, Field
from typing import Optional, List
from pathlib import Path

class AnalysisSettings(BaseSettings):
    """Analysis configuration"""
    max_file_size_mb: int = 10
    excluded_dirs: List[str] = [".git", "node_modules", "__pycache__"]
    include_patterns: List[str] = ["*.kt", "*.java", "*.swift"]
    parallel_processing: bool = True
    max_workers: int = 4

class GenerationSettings(BaseSettings):
    """Code generation configuration"""
    template_dir: Optional[Path] = None
    line_length: int = 120
    add_type_hints: bool = True
    add_docstrings: bool = True
    format_with_black: bool = True

class ObserveSettings(BaseSettings):
    """Global application settings"""
    
    # Paths
    project_root: Path = Field(default_factory=Path.cwd)
    output_dir: Path = Field(default="./observe_output")
    log_level: str = "INFO"
    
    # Sub-configurations
    analysis: AnalysisSettings = Field(default_factory=AnalysisSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    
    class Config:
        env_prefix = "OBSERVE_"
        env_file = ".observe.env"
        case_sensitive = False

# Load from multiple sources
settings = ObserveSettings(
    _env_file=".observe.env",  # Local project config
    _env_file_encoding="utf-8"
)
```

### Configuration Files:

```yaml
# .observe.yaml - Project-specific configuration
analysis:
  max_file_size_mb: 20
  excluded_dirs:
    - .git
    - build
    - node_modules
  parallel_processing: true

generation:
  line_length: 120
  add_type_hints: true
  template_dir: ./custom_templates

plugins:
  enabled:
    - custom-analyzer
    - advanced-reporter
  
integrations:
  ci:
    provider: github-actions
    auto_commit: true
  
  reporting:
    allure:
      enabled: true
      results_dir: ./allure-results
    slack:
      enabled: true
      webhook_url: ${SLACK_WEBHOOK}
```

---

## 6. 📈 Improved CLI with Rich Output

### Use `rich` library for beautiful CLI:

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.panel import Panel

console = Console()

def display_analysis_results(results: AnalysisResults):
    """Display analysis results with rich formatting"""
    
    # Create table
    table = Table(title="Analysis Summary", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="magenta")
    table.add_column("Status", style="green")
    
    table.add_row("User Flows", str(len(results.user_flows)), "✓")
    table.add_row("Business Rules", str(len(results.business_rules)), "✓")
    table.add_row("API Contracts", str(len(results.api_contracts)), "✓")
    
    console.print(table)
    
    # Show tree of screens
    tree = Tree("📱 Screens")
    for screen in results.screens:
        screen_node = tree.add(f"[bold]{screen.name}[/bold]")
        for element in screen.elements[:5]:
            screen_node.add(f"├─ {element.id} ({element.type})")
    
    console.print(tree)

# Progress bars
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("Analyzing Android source...", total=100)
    # ... analysis
    progress.update(task, advance=50)
```

---

## 7. 🧪 Testing Strategy

### Comprehensive Testing Pyramid:

```
tests/
├── unit/                        # Fast, isolated tests
│   ├── test_analyzers/
│   ├── test_generators/
│   ├── test_model/
│   └── test_utils/
│
├── integration/                 # Component integration
│   ├── test_analysis_pipeline/
│   ├── test_generation_pipeline/
│   └── test_healing_flow/
│
├── e2e/                         # End-to-end scenarios
│   ├── test_android_workflow/
│   ├── test_ios_workflow/
│   └── test_fullcycle/
│
├── fixtures/                    # Test data
│   ├── sample_projects/
│   │   ├── android_kotlin/
│   │   ├── android_java/
│   │   ├── ios_swift/
│   │   └── ios_objc/
│   └── expected_outputs/
│
└── conftest.py                  # Pytest configuration
```

---

## 8. 📚 Documentation Structure

```
docs/
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── configuration.md
│
├── guides/
│   ├── analyzing-android.md
│   ├── analyzing-ios.md
│   ├── generating-tests.md
│   ├── self-healing.md
│   └── ml-powered-features.md
│
├── api/
│   ├── analyzers.md
│   ├── generators.md
│   ├── model.md
│   └── plugins.md
│
├── architecture/
│   ├── overview.md
│   ├── event-system.md
│   ├── plugin-system.md
│   └── data-flow.md
│
├── contributing/
│   ├── development-setup.md
│   ├── code-style.md
│   └── plugin-development.md
│
└── examples/
    ├── custom-analyzer/
    ├── custom-generator/
    └── integration-examples/
```

---

## 9. 🚀 Performance Optimizations

### 1. **Parallel Processing**

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import cpu_count

class ParallelAnalyzer:
    """Analyze multiple files in parallel"""
    
    def analyze_files(self, files: List[Path], max_workers: Optional[int] = None) -> List[AnalysisResult]:
        max_workers = max_workers or cpu_count()
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self._analyze_file, files))
        
        return results
```

### 2. **Caching**

```python
from functools import lru_cache
from diskcache import Cache

# Memory cache for fast lookups
@lru_cache(maxsize=1000)
def parse_file(file_path: str) -> AST:
    return ast.parse(Path(file_path).read_text())

# Disk cache for expensive operations
cache = Cache("./cache")

@cache.memoize(expire=3600)  # 1 hour
def analyze_large_project(project_path: str) -> Dict:
    # Expensive analysis
    return results
```

### 3. **Lazy Loading**

```python
class LazyAppModel:
    """Lazy-load model components"""
    
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self._screens = None
        self._api_calls = None
    
    @property
    def screens(self) -> Dict[str, Screen]:
        if self._screens is None:
            # Load only when accessed
            self._screens = self._load_screens()
        return self._screens
```

---

## 10. 🔒 Security Enhancements

### 1. **Secrets Detection**

```python
class SecretsDetector:
    """Detect hardcoded secrets in code"""
    
    PATTERNS = {
        'api_key': r'api[_-]?key\s*=\s*["\']([^"\']+)["\']',
        'password': r'password\s*=\s*["\']([^"\']+)["\']',
        'token': r'token\s*=\s*["\']([^"\']+)["\']',
        'aws_key': r'AKIA[0-9A-Z]{16}',
    }
    
    def scan_file(self, file_path: Path) -> List[SecretFinding]:
        findings = []
        content = file_path.read_text()
        
        for secret_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                findings.append(SecretFinding(
                    type=secret_type,
                    value=match.group(1),
                    file=file_path,
                    line=content[:match.start()].count('\n') + 1
                ))
        
        return findings
```

### 2. **Input Validation**

```python
from pydantic import validator, constr

class AnalysisRequest(BaseModel):
    source_path: Path
    output_dir: Path
    
    @validator('source_path')
    def validate_source_path(cls, v):
        if not v.exists():
            raise ValueError(f"Source path does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Source path must be a directory: {v}")
        return v.resolve()  # Resolve to absolute path
```

---

## 11. 🌐 API Server Mode

### RESTful API for remote usage:

```python
# framework/server/api.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="Observe Test Framework API")

class AnalysisRequest(BaseModel):
    project_url: str
    platform: str
    options: Dict[str, Any]

class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    results_url: Optional[str]

@app.post("/api/v1/analyze")
async def analyze_project(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    job_id = str(uuid.uuid4())
    background_tasks.add_task(run_analysis, job_id, request)
    return AnalysisResponse(job_id=job_id, status="queued")

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    job = get_job(job_id)
    return {"job_id": job_id, "status": job.status, "progress": job.progress}
```

---

## 12. 📊 Metrics & Telemetry

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
analysis_counter = Counter('observe_analyses_total', 'Total analyses run')
analysis_duration = Histogram('observe_analysis_duration_seconds', 'Analysis duration')
active_jobs = Gauge('observe_active_jobs', 'Number of active analysis jobs')

class MetricsCollector:
    @analysis_duration.time()
    def analyze(self, project_path: Path):
        analysis_counter.inc()
        active_jobs.inc()
        try:
            # ... analysis
            pass
        finally:
            active_jobs.dec()
```

---

## 📋 Implementation Priority

### Phase 1: Critical Foundation (Week 1-2)
- [ ] Restructure into separate modules
- [ ] Extract utils and config packages
- [ ] Fix all critical bugs from code review
- [ ] Add comprehensive logging

### Phase 2: Plugin System (Week 3-4)
- [ ] Implement plugin base classes
- [ ] Add plugin discovery mechanism
- [ ] Create 2-3 example plugins
- [ ] Document plugin development

### Phase 3: Test Framework Adapters (Week 5-6)
- [ ] Implement pytest adapter
- [ ] Implement unittest adapter
- [ ] Add adapter auto-detection
- [ ] Test with real projects

### Phase 4: Performance & Polish (Week 7-8)
- [ ] Add parallel processing
- [ ] Implement caching layer
- [ ] Rich CLI output
- [ ] Comprehensive testing

### Phase 5: Advanced Features (Week 9-12)
- [ ] Event-driven architecture
- [ ] API server mode
- [ ] Metrics & telemetry
- [ ] Security enhancements

---

## 💡 Additional Ideas

1. **VS Code Extension**: Integrate directly into IDE
2. **GitHub Action**: Ready-to-use CI integration
3. **Docker Images**: Pre-configured environments
4. **Cloud Service**: SaaS version of the tool
5. **Dashboard**: Web UI for visualization
6. **AI Assistant**: ChatGPT integration for test suggestions
7. **Cross-Platform**: Support React Native, Flutter
8. **Visual Regression**: Screenshot comparison testing
9. **Accessibility Testing**: WCAG compliance checks
10. **Performance Profiling**: Integrated performance testing

---

**End of Architecture Improvement Plan**

