//! Fast AST Analysis Engine
//!
//! Provides high-performance AST parsing and complexity metric calculation.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use rayon::prelude::*;
use walkdir::WalkDir;

/// Complexity metrics for a code element
#[derive(Debug, Clone)]
#[pyclass]
pub struct ComplexityMetrics {
    #[pyo3(get)]
    pub cyclomatic_complexity: usize,
    #[pyo3(get)]
    pub cognitive_complexity: usize,
    #[pyo3(get)]
    pub max_nesting_depth: usize,
    #[pyo3(get)]
    pub lines_of_code: usize,
}

#[pymethods]
impl ComplexityMetrics {
    #[new]
    fn new() -> Self {
        Self::default()
    }

    fn __repr__(&self) -> String {
        format!(
            "ComplexityMetrics(cyclomatic={}, cognitive={}, nesting={}, loc={})",
            self.cyclomatic_complexity,
            self.cognitive_complexity,
            self.max_nesting_depth,
            self.lines_of_code
        )
    }
}

impl Default for ComplexityMetrics {
    fn default() -> Self {
        Self {
            cyclomatic_complexity: 1,
            cognitive_complexity: 0,
            max_nesting_depth: 0,
            lines_of_code: 0,
        }
    }
}

/// High-performance AST analyzer
#[pyclass]
pub struct RustAstAnalyzer {
    cache: HashMap<String, ComplexityMetrics>,
}

#[pymethods]
impl RustAstAnalyzer {
    #[new]
    fn new() -> Self {
        Self {
            cache: HashMap::new(),
        }
    }

    /// Analyze a single Python file
    #[pyo3(signature = (file_path))]
    fn analyze_file(&mut self, file_path: String) -> PyResult<ComplexityMetrics> {
        // Check cache
        if let Some(metrics) = self.cache.get(&file_path) {
            return Ok(metrics.clone());
        }

        // Read file
        let content = std::fs::read_to_string(&file_path)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))?;

        // Parse and analyze
        let metrics = self.analyze_source(&content)?;

        // Cache result
        self.cache.insert(file_path, metrics.clone());

        Ok(metrics)
    }

    /// Analyze entire directory in parallel
    #[pyo3(signature = (directory_path, extensions = None))]
    fn analyze_directory(
        &mut self,
        py: Python,
        directory_path: String,
        extensions: Option<Vec<String>>,
    ) -> PyResult<PyObject> {
        let default_exts = vec!["py".to_string()];
        let exts = extensions.as_ref().unwrap_or(&default_exts);

        // Collect all files
        let files: Vec<_> = WalkDir::new(&directory_path)
            .into_iter()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_type().is_file())
            .filter(|e| {
                e.path()
                    .extension()
                    .and_then(|s| s.to_str())
                    .map(|ext| exts.contains(&ext.to_string()))
                    .unwrap_or(false)
            })
            .map(|e| e.path().to_string_lossy().to_string())
            .collect();

        println!("🔍 Analyzing {} files...", files.len());

        // Parallel processing with rayon
        let results: HashMap<String, ComplexityMetrics> = files
            .par_iter()
            .filter_map(|file_path| {
                match std::fs::read_to_string(file_path) {
                    Ok(content) => {
                        match self.analyze_source(&content) {
                            Ok(metrics) => Some((file_path.clone(), metrics)),
                            Err(_) => None,
                        }
                    }
                    Err(_) => None,
                }
            })
            .collect();

        // Convert to Python dict
        let dict = PyDict::new(py);
        for (file, metrics) in results.iter() {
            // Convert ComplexityMetrics to Py<ComplexityMetrics>
            let py_metrics = Py::new(py, metrics.clone())?;
            dict.set_item(file, py_metrics)?;
        }

        Ok(dict.into())
    }

    /// Analyze Python source code
    fn analyze_source(&self, source: &str) -> PyResult<ComplexityMetrics> {
        // Parse Python AST using syn (simplified for now)
        // In production, use tree-sitter-python for full Python parsing
        
        let mut metrics = ComplexityMetrics::default();
        metrics.lines_of_code = source.lines().count();

        // Calculate complexity (simplified version)
        // Count control flow statements
        let control_flow_keywords = ["if", "else", "elif", "for", "while", "try", "except", "with"];
        let mut complexity = 1;
        let mut cognitive = 0;
        let mut max_nesting = 0;
        let mut current_nesting = 0;

        for line in source.lines() {
            let trimmed = line.trim();
            
            // Count control flow
            for keyword in &control_flow_keywords {
                if trimmed.starts_with(keyword) {
                    complexity += 1;
                    cognitive += 1 + current_nesting;
                    
                    if *keyword != "else" && *keyword != "elif" && *keyword != "except" {
                        current_nesting += 1;
                        max_nesting = max_nesting.max(current_nesting);
                    }
                }
            }

            // Decrease nesting on dedent (simplified)
            if trimmed.is_empty() {
                current_nesting = 0;
            }
        }

        metrics.cyclomatic_complexity = complexity;
        metrics.cognitive_complexity = cognitive;
        metrics.max_nesting_depth = max_nesting;

        Ok(metrics)
    }

    /// Clear analysis cache
    fn clear_cache(&mut self) {
        self.cache.clear();
    }

    /// Get cache size
    fn cache_size(&self) -> usize {
        self.cache.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_function() {
        let analyzer = RustAstAnalyzer::new();
        let source = r#"
def simple_function():
    return 42
"#;
        let metrics = analyzer.analyze_source(source).unwrap();
        assert_eq!(metrics.lines_of_code, 4);
        assert_eq!(metrics.cyclomatic_complexity, 1);
    }

    #[test]
    fn test_complex_function() {
        let analyzer = RustAstAnalyzer::new();
        let source = r#"
def complex_function(x):
    if x > 10:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    else:
        return 0
"#;
        let metrics = analyzer.analyze_source(source).unwrap();
        assert!(metrics.cyclomatic_complexity > 3);
        assert!(metrics.max_nesting_depth >= 2);
    }
}
