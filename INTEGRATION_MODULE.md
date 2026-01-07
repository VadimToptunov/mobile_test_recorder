# Framework Extension - Integration Module

## Overview

The `mobile-observe-test-framework` has been extended with a new **Integration Module** that enables seamless integration with existing test projects.

## New Features

### 1. Model Enrichment (`ModelEnricher`)

Enriches existing App Models with analysis results without breaking existing tests.

```python
from framework.integration import ModelEnricher

enricher = ModelEnricher(preserve_existing=True)
enriched_model = enricher.enrich_model(existing_model, analysis_results)

print(f"Added {enricher.result.elements_added} elements")
print(f"Added {enricher.result.api_endpoints_added} API endpoints")
```

**Features:**
- ✅ Non-destructive merging
- ✅ Conflict resolution
- ✅ Selector fallback addition
- ✅ API endpoint discovery
- ✅ Navigation flow integration

### 2. Project Integration (`ProjectIntegrator`)

Automatically detects and integrates with existing test frameworks.

```python
from framework.integration import ProjectIntegrator

integrator = ProjectIntegrator(project_path)

# Detect framework type
framework = integrator.detect_framework()  # pytest, unittest, robot

# Find existing Page Objects
page_objects = integrator.find_page_objects()

# Full integration
result = integrator.integrate(analysis_results)
```

**Capabilities:**
- ✅ Framework detection (pytest, unittest, robot)
- ✅ Page Object discovery
- ✅ Element extraction from existing code
- ✅ Automatic enrichment

### 3. CLI Commands

#### `observe integrate`

Integrate framework with existing project:

```bash
# Basic integration
observe integrate ./my-project --analysis android_analysis.yaml

# Replace instead of merge
observe integrate ./my-project --analysis analysis.yaml --replace-all

# Custom output
observe integrate ./my-project --analysis analysis.yaml --output enriched.yaml
```

#### `observe enrich model`

Enrich specific App Model:

```bash
# Enrich model with analysis
observe enrich model app_model.yaml android_analysis.yaml

# Custom output
observe enrich model app_model.yaml analysis.yaml --output new_model.yaml
```

#### `observe enrich pageobject`

Enrich existing Page Object:

```bash
# Add discovered elements to Page Object
observe enrich pageobject pages/home_page.py android_analysis.yaml
```

## Usage Examples

### Example 1: Enrich Existing Project

```bash
# 1. Analyze source code
observe analyze android --source ./app/src --output android_analysis.yaml

# 2. Integrate with existing tests
observe integrate ./test-project --analysis android_analysis.yaml

# 3. Review changes
cat test-project/config/app_model_enriched.yaml

# 4. Apply changes
cp test-project/config/app_model.yaml test-project/config/app_model.backup.yaml
mv test-project/config/app_model_enriched.yaml test-project/config/app_model.yaml

# 5. Regenerate artifacts
cd test-project
observe generate page-objects
```

### Example 2: Programmatic Integration

```python
from pathlib import Path
from framework.integration import ProjectIntegrator
from framework.analyzers.android_analyzer import AndroidAnalyzer

# Analyze source
analyzer = AndroidAnalyzer()
analysis = analyzer.analyze("./app/src")

# Integrate with existing project
integrator = ProjectIntegrator(Path("./test-project"))
result = integrator.integrate(analysis.model_dump())

print(f"✅ Integration complete!")
print(f"   Screens enriched: {result.screens_enriched}")
print(f"   Elements added: {result.elements_added}")
print(f"   APIs added: {result.api_endpoints_added}")
```

### Example 3: Selective Enrichment

```python
from framework.integration import ModelEnricher

# Only add high-priority elements
enricher = ModelEnricher()

# Custom filtering
for screen in analysis.screens:
    for element in screen.ui_elements:
        if element.test_priority == 'high':
            # Add to model
            pass
```

## Integration Workflow

```
┌─────────────────┐
│  Source Code    │
│  (Kotlin/Swift) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Analyzer     │
│  (Static/AST)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analysis       │
│  Results        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ModelEnricher  │
│  (Integration)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Enriched       │
│  App Model      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Regenerate     │
│  Artifacts      │
└─────────────────┘
```

## API Reference

### `ModelEnricher`

```python
class ModelEnricher:
    def __init__(self, preserve_existing: bool = True):
        """
        Initialize enricher
        
        Args:
            preserve_existing: Keep existing elements (default: True)
        """
    
    def enrich_model(
        self,
        existing_model: Dict,
        analysis_result: Dict
    ) -> Dict:
        """
        Enrich model with analysis results
        
        Returns:
            Enriched model
        """
    
    def merge_selectors(
        self,
        existing: Dict,
        discovered: Dict
    ) -> Dict:
        """
        Merge selectors with fallback strategy
        """
```

### `ProjectIntegrator`

```python
class ProjectIntegrator:
    def __init__(self, project_path: Path):
        """Initialize integrator for project"""
    
    def detect_framework(self) -> str:
        """
        Detect test framework type
        
        Returns:
            'pytest', 'unittest', 'robot', or 'unknown'
        """
    
    def find_page_objects(self) -> List[Path]:
        """Find existing Page Object files"""
    
    def integrate(self, analysis_results: Dict) -> EnrichmentResult:
        """
        Perform full integration
        
        Returns:
            Enrichment result with statistics
        """
```

### `EnrichmentResult`

```python
class EnrichmentResult(BaseModel):
    screens_enriched: int = 0
    elements_added: int = 0
    selectors_updated: int = 0
    api_endpoints_added: int = 0
    navigation_added: int = 0
    warnings: List[str] = []
    errors: List[str] = []
```

## Configuration

### Integration Settings

Can be configured via `config/integration.yaml`:

```yaml
integration:
  preserve_existing: true
  merge_strategy: "fallback"  # fallback, replace, append
  priority_filter: "medium"   # only add medium+ priority elements
  
  selector_merging:
    add_to_fallback: true
    promote_stable: true       # promote stable fallbacks to primary
  
  api_discovery:
    add_all: false
    filter_by_service: ["IBffService", "IWalletService"]
```

## Best Practices

### 1. Always Backup Before Integration

```bash
# Backup original model
cp config/app_model.yaml config/app_model.backup.yaml

# Backup Page Objects
cp -r page_objects/ page_objects.backup/
```

### 2. Review Before Applying

```bash
# Generate enriched model
observe integrate ./project --analysis analysis.yaml

# Review diff
diff config/app_model.yaml config/app_model_enriched.yaml

# Apply if good
mv config/app_model_enriched.yaml config/app_model.yaml
```

### 3. Incremental Integration

```python
# Start with just API endpoints
enricher = ModelEnricher()
enriched = enricher.enrich_model(model, analysis)

# Review API endpoints first
for api in enriched['api_calls']:
    print(f"{api['method']} {api['endpoint']}")

# Then add UI elements
# Then update selectors
```

### 4. CI/CD Integration

```yaml
# .github/workflows/enrich-tests.yml
name: Weekly Test Enrichment

on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday

jobs:
  enrich:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Analyze Source
        run: |
          observe analyze android --source ./app/src --output analysis.yaml
      
      - name: Integrate
        run: |
          observe integrate ./tests --analysis analysis.yaml
      
      - name: Create PR
        if: ${{ github.event_name == 'schedule' }}
        run: |
          git checkout -b auto/enrich-tests
          git add config/app_model_enriched.yaml
          git commit -m "chore: enrich test model from source analysis"
          gh pr create --title "Auto: Enrich Test Model" --body "Weekly enrichment"
```

## Troubleshooting

### Issue: Duplicate Elements

**Cause:** Element IDs conflict

**Solution:**
```python
enricher = ModelEnricher()
# Enricher automatically deduplicates by element ID
```

### Issue: Breaking Changes

**Cause:** Selectors changed

**Solution:** Use fallback strategy
```python
# Old selector becomes fallback
# New selector becomes primary
enricher.merge_selectors(existing, discovered)
```

### Issue: Too Many Discovered Elements

**Solution:** Filter by priority
```python
# Only add high-priority elements
if element['test_priority'] == 'high':
    add_element()
```

## Migration Path

### For Existing Projects

1. **Phase 1: Analysis Only**
   - Run analysis
   - Review results
   - No changes to tests

2. **Phase 2: API Integration**
   - Add discovered API endpoints
   - Generate API tests
   - Low risk

3. **Phase 3: Selector Enrichment**
   - Add fallback selectors
   - Enable self-healing
   - Medium risk

4. **Phase 4: Full Integration**
   - Add new elements
   - Expand coverage
   - Higher benefit

## Summary

The Integration Module enables:
- ✅ **Non-destructive** enrichment
- ✅ **Automatic** discovery
- ✅ **Seamless** integration
- ✅ **Flexible** configuration
- ✅ **CI/CD** ready

Use it to keep your test framework in sync with your application!

