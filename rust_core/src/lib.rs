//! Observe Core - High-Performance Rust Engine
//!
//! This library provides high-performance implementations of CPU-intensive
//! operations for the Mobile Test Recorder framework.
//!
//! # Modules
//!
//! - `ast_analyzer`: Fast AST parsing and complexity analysis
//! - `correlator`: Event correlation engine
//! - `business_logic`: Business logic pattern extraction
//! - `io`: Optimized file I/O operations

use pyo3::prelude::*;

// Module declarations
pub mod ast_analyzer;
pub mod correlator;
pub mod business_logic;
pub mod io;
pub mod utils;

// Re-exports
pub use ast_analyzer::{RustAstAnalyzer, ComplexityMetrics};
pub use correlator::RustCorrelator;
pub use business_logic::RustBusinessLogicAnalyzer;

/// Python module definition
#[pymodule]
fn observe_core(_py: Python, m: &PyModule) -> PyResult<()> {
    // Initialize logging
    env_logger::init();

    // Register classes
    m.add_class::<RustAstAnalyzer>()?;
    m.add_class::<ComplexityMetrics>()?;
    m.add_class::<RustCorrelator>()?;
    m.add_class::<RustBusinessLogicAnalyzer>()?;

    // Module metadata
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__author__", "Vadim Toptunov")?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_module_loads() {
        // Basic smoke test
        assert!(true);
    }
}
