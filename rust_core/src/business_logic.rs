//! Business Logic Analysis
//!
//! High-performance analysis of business logic patterns in mobile applications

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;
use regex::Regex;

/// A business logic pattern found in code
#[derive(Debug, Clone)]
#[pyclass]
pub struct BusinessLogicPattern {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub category: String,
    #[pyo3(get)]
    pub confidence: f64,
    #[pyo3(get)]
    pub file_path: String,
    #[pyo3(get)]
    pub line_number: usize,
    #[pyo3(get)]
    pub code_snippet: String,
}

#[pymethods]
impl BusinessLogicPattern {
    fn __repr__(&self) -> String {
        format!(
            "BusinessLogicPattern(name={}, category={}, confidence={:.2})",
            self.name, self.category, self.confidence
        )
    }
}

/// Categories of business logic
#[derive(Debug, Clone)]
pub enum LogicCategory {
    Validation,
    Authentication,
    Authorization,
    DataTransformation,
    BusinessRule,
    StateManagement,
    ErrorHandling,
    Integration,
}

impl LogicCategory {
    fn as_str(&self) -> &str {
        match self {
            LogicCategory::Validation => "Validation",
            LogicCategory::Authentication => "Authentication",
            LogicCategory::Authorization => "Authorization",
            LogicCategory::DataTransformation => "DataTransformation",
            LogicCategory::BusinessRule => "BusinessRule",
            LogicCategory::StateManagement => "StateManagement",
            LogicCategory::ErrorHandling => "ErrorHandling",
            LogicCategory::Integration => "Integration",
        }
    }
}

/// Business logic analyzer
#[pyclass]
pub struct RustBusinessLogicAnalyzer {
    patterns: Vec<BusinessLogicPattern>,
    validation_patterns: Vec<Regex>,
    auth_patterns: Vec<Regex>,
    state_patterns: Vec<Regex>,
}

#[pymethods]
impl RustBusinessLogicAnalyzer {
    #[new]
    fn new() -> Self {
        let validation_patterns = vec![
            Regex::new(r"(?i)(validate|check|verify|ensure|require|assert)[A-Z]\w+").unwrap(),
            Regex::new(r"(?i)(is_?valid|is_?empty|is_?null|has_?error)").unwrap(),
            Regex::new(r"\.length\s*[<>=]+\s*\d+").unwrap(),
            Regex::new(r"(?i)(email|phone|password|username).*validation").unwrap(),
        ];

        let auth_patterns = vec![
            Regex::new(r"(?i)(login|logout|sign_?in|sign_?out|authenticate)").unwrap(),
            Regex::new(r"(?i)(token|session|credentials|password|auth)").unwrap(),
            Regex::new(r"(?i)(is_?authenticated|is_?logged_?in|has_?permission)").unwrap(),
        ];

        let state_patterns = vec![
            Regex::new(r"(?i)(state|store|redux|mobx|riverpod)").unwrap(),
            Regex::new(r"(?i)(get_?state|set_?state|update_?state)").unwrap(),
            Regex::new(r"(?i)(observable|stream|subject|controller)").unwrap(),
        ];

        Self {
            patterns: Vec::new(),
            validation_patterns,
            auth_patterns,
            state_patterns,
        }
    }

    /// Analyze a source file for business logic
    fn analyze_file(&mut self, file_path: String, source: String) -> PyResult<()> {
        self.patterns.clear();

        // Split into lines for analysis
        for (line_num, line) in source.lines().enumerate() {
            self.analyze_line(&file_path, line_num + 1, line);
        }

        Ok(())
    }

    /// Get all found patterns
    fn get_patterns(&self, py: Python) -> PyResult<PyObject> {
        let py_list = PyList::empty(py);
        for pattern in &self.patterns {
            py_list.append(Py::new(py, pattern.clone())?)?;
        }
        Ok(py_list.into())
    }

    /// Get patterns by category
    fn get_patterns_by_category(&self, py: Python, category: String) -> PyResult<PyObject> {
        let filtered: Vec<_> = self.patterns
            .iter()
            .filter(|p| p.category == category)
            .cloned()
            .collect();

        let py_list = PyList::empty(py);
        for pattern in filtered {
            py_list.append(Py::new(py, pattern)?)?;
        }
        Ok(py_list.into())
    }

    /// Get statistics about found patterns
    fn get_statistics(&self, py: Python) -> PyResult<PyObject> {
        let mut by_category: HashMap<String, usize> = HashMap::new();
        
        for pattern in &self.patterns {
            *by_category.entry(pattern.category.clone()).or_insert(0) += 1;
        }

        let total = self.patterns.len();
        let avg_confidence = if total > 0 {
            self.patterns.iter().map(|p| p.confidence).sum::<f64>() / total as f64
        } else {
            0.0
        };

        let stats = PyDict::new(py);
        stats.set_item("total_patterns", total)?;
        stats.set_item("avg_confidence", avg_confidence)?;

        let by_cat_dict = PyDict::new(py);
        for (category, count) in by_category {
            by_cat_dict.set_item(category, count)?;
        }
        stats.set_item("by_category", by_cat_dict)?;

        Ok(stats.into())
    }

    /// Clear all found patterns
    fn clear(&mut self) {
        self.patterns.clear();
    }

    /// Get pattern count
    fn len(&self) -> usize {
        self.patterns.len()
    }
}

// Implementation methods (not exposed to Python)
impl RustBusinessLogicAnalyzer {
    /// Analyze a single line of code
    fn analyze_line(&mut self, file_path: &str, line_num: usize, line: &str) {
        // Check for validation patterns
        for pattern in &self.validation_patterns {
            if let Some(mat) = pattern.find(line) {
                self.patterns.push(BusinessLogicPattern {
                    name: mat.as_str().to_string(),
                    category: LogicCategory::Validation.as_str().to_string(),
                    confidence: 0.8,
                    file_path: file_path.to_string(),
                    line_number: line_num,
                    code_snippet: line.trim().to_string(),
                });
            }
        }

        // Check for authentication patterns
        for pattern in &self.auth_patterns {
            if let Some(mat) = pattern.find(line) {
                self.patterns.push(BusinessLogicPattern {
                    name: mat.as_str().to_string(),
                    category: LogicCategory::Authentication.as_str().to_string(),
                    confidence: 0.85,
                    file_path: file_path.to_string(),
                    line_number: line_num,
                    code_snippet: line.trim().to_string(),
                });
            }
        }

        // Check for state management patterns
        for pattern in &self.state_patterns {
            if let Some(mat) = pattern.find(line) {
                self.patterns.push(BusinessLogicPattern {
                    name: mat.as_str().to_string(),
                    category: LogicCategory::StateManagement.as_str().to_string(),
                    confidence: 0.75,
                    file_path: file_path.to_string(),
                    line_number: line_num,
                    code_snippet: line.trim().to_string(),
                });
            }
        }

        // Check for error handling
        if line.contains("try") || line.contains("catch") || line.contains("except") {
            self.patterns.push(BusinessLogicPattern {
                name: "ErrorHandling".to_string(),
                category: LogicCategory::ErrorHandling.as_str().to_string(),
                confidence: 0.9,
                file_path: file_path.to_string(),
                line_number: line_num,
                code_snippet: line.trim().to_string(),
            });
        }

        // Check for API integration
        if line.contains("fetch") || line.contains("request") || line.contains("api") {
            self.patterns.push(BusinessLogicPattern {
                name: "APIIntegration".to_string(),
                category: LogicCategory::Integration.as_str().to_string(),
                confidence: 0.7,
                file_path: file_path.to_string(),
                line_number: line_num,
                code_snippet: line.trim().to_string(),
            });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_analyzer_creation() {
        let analyzer = RustBusinessLogicAnalyzer::new();
        assert_eq!(analyzer.len(), 0);
    }

    #[test]
    fn test_validation_detection() {
        let mut analyzer = RustBusinessLogicAnalyzer::new();
        
        let source = r#"
            def validateEmail(email):
                return email.contains('@')
        "#;

        analyzer.analyze_file("test.py".to_string(), source.to_string()).unwrap();
        
        assert!(analyzer.len() > 0);
        assert!(analyzer.patterns.iter().any(|p| p.category == "Validation"));
    }

    #[test]
    fn test_auth_detection() {
        let mut analyzer = RustBusinessLogicAnalyzer::new();
        
        let source = "await login(username, password)";
        
        analyzer.analyze_file("test.py".to_string(), source.to_string()).unwrap();
        
        assert!(analyzer.len() > 0);
        assert!(analyzer.patterns.iter().any(|p| p.category == "Authentication"));
    }

    #[test]
    fn test_error_handling_detection() {
        let mut analyzer = RustBusinessLogicAnalyzer::new();
        
        let source = r#"
            try:
                risky_operation()
            except Exception as e:
                log_error(e)
        "#;

        analyzer.analyze_file("test.py".to_string(), source.to_string()).unwrap();
        
        assert!(analyzer.len() > 0);
        assert!(analyzer.patterns.iter().any(|p| p.category == "ErrorHandling"));
    }
}
