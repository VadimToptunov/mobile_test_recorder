//! File I/O Utilities
//!
//! High-performance file operations using Rust's async I/O

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::fs;
use std::path::{Path, PathBuf};
use std::io::{self, Read, Write};
use rayon::prelude::*;
use walkdir::WalkDir;

/// Read a file quickly
#[pyfunction]
pub fn read_file_fast(path: &str) -> PyResult<String> {
    fs::read_to_string(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e))
    })
}

/// Write a file quickly
#[pyfunction]
pub fn write_file_fast(path: &str, content: &str) -> PyResult<()> {
    fs::write(path, content).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write file: {}", e))
    })
}

/// Read multiple files in parallel
#[pyfunction]
pub fn read_files_parallel(py: Python, paths: Vec<String>) -> PyResult<PyObject> {
    let results: Vec<(String, Result<String, io::Error>)> = paths
        .par_iter()
        .map(|path| {
            let content = fs::read_to_string(path);
            (path.clone(), content)
        })
        .collect();

    // Convert to Python dict
    let py_dict = PyDict::new(py);
    for (path, result) in results {
        match result {
            Ok(content) => {
                py_dict.set_item(path, content)?;
            }
            Err(_) => {
                py_dict.set_item(path, py.None())?;
            }
        }
    }

    Ok(py_dict.into())
}

/// Find files matching a pattern
#[pyfunction]
pub fn find_files(py: Python, root_dir: &str, pattern: &str) -> PyResult<PyObject> {
    let mut matching_files = Vec::new();

    for entry in WalkDir::new(root_dir)
        .follow_links(true)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        let path = entry.path();
        if path.is_file() {
            if let Some(file_name) = path.file_name() {
                if file_name.to_string_lossy().contains(pattern) {
                    matching_files.push(path.to_string_lossy().to_string());
                }
            }
        }
    }

    // Convert to Python list
    let py_list = PyList::empty(py);
    for file in matching_files {
        py_list.append(file)?;
    }

    Ok(py_list.into())
}

/// Get file size quickly
#[pyfunction]
pub fn get_file_size(path: &str) -> PyResult<u64> {
    let metadata = fs::metadata(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to get file size: {}", e))
    })?;

    Ok(metadata.len())
}

/// Check if file exists
#[pyfunction]
pub fn file_exists(path: &str) -> bool {
    Path::new(path).exists()
}

/// Get directory size recursively
#[pyfunction]
pub fn get_directory_size(path: &str) -> PyResult<u64> {
    let mut total_size = 0u64;

    for entry in WalkDir::new(path)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        if entry.path().is_file() {
            if let Ok(metadata) = entry.metadata() {
                total_size += metadata.len();
            }
        }
    }

    Ok(total_size)
}

/// List directory contents quickly
#[pyfunction]
pub fn list_directory(py: Python, path: &str) -> PyResult<PyObject> {
    let entries = fs::read_dir(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to list directory: {}", e))
    })?;

    let py_list = PyList::empty(py);

    for entry in entries.filter_map(|e| e.ok()) {
        if let Ok(file_name) = entry.file_name().into_string() {
            py_list.append(file_name)?;
        }
    }

    Ok(py_list.into())
}

/// Copy file with progress
#[pyfunction]
pub fn copy_file_fast(source: &str, destination: &str) -> PyResult<u64> {
    fs::copy(source, destination).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to copy file: {}", e))
    })
}

/// Move/rename file
#[pyfunction]
pub fn move_file(source: &str, destination: &str) -> PyResult<()> {
    fs::rename(source, destination).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to move file: {}", e))
    })
}

/// Delete file
#[pyfunction]
pub fn delete_file(path: &str) -> PyResult<()> {
    fs::remove_file(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to delete file: {}", e))
    })
}

/// Create directory
#[pyfunction]
pub fn create_directory(path: &str) -> PyResult<()> {
    fs::create_dir_all(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to create directory: {}", e))
    })
}

/// Delete directory recursively
#[pyfunction]
pub fn delete_directory(path: &str) -> PyResult<()> {
    fs::remove_dir_all(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to delete directory: {}", e))
    })
}

/// Get file modification time (Unix timestamp)
#[pyfunction]
pub fn get_file_mtime(path: &str) -> PyResult<f64> {
    let metadata = fs::metadata(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to get file metadata: {}", e))
    })?;

    let modified = metadata.modified().map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to get modified time: {}", e))
    })?;

    let duration = modified
        .duration_since(std::time::UNIX_EPOCH)
        .map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid timestamp: {}", e))
        })?;

    Ok(duration.as_secs_f64())
}

/// Read file in chunks (for large files)
#[pyfunction]
pub fn read_file_chunked(py: Python, path: &str, chunk_size: usize) -> PyResult<PyObject> {
    let file = fs::File::open(path).map_err(|e| {
        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to open file: {}", e))
    })?;

    let mut reader = io::BufReader::new(file);
    let mut chunks = Vec::new();
    let mut buffer = vec![0u8; chunk_size];

    loop {
        match reader.read(&mut buffer) {
            Ok(0) => break, // EOF
            Ok(n) => {
                let chunk = String::from_utf8_lossy(&buffer[..n]).to_string();
                chunks.push(chunk);
            }
            Err(e) => {
                return Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                    "Failed to read chunk: {}",
                    e
                )));
            }
        }
    }

    // Convert to Python list
    let py_list = PyList::empty(py);
    for chunk in chunks {
        py_list.append(chunk)?;
    }

    Ok(py_list.into())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::tempdir;

    #[test]
    fn test_read_write_file() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test.txt");
        let file_path_str = file_path.to_str().unwrap();

        // Write
        write_file_fast(file_path_str, "Hello, Rust!").unwrap();

        // Read
        let content = read_file_fast(file_path_str).unwrap();
        assert_eq!(content, "Hello, Rust!");
    }

    #[test]
    fn test_file_exists() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test.txt");
        let file_path_str = file_path.to_str().unwrap();

        assert!(!file_exists(file_path_str));

        fs::write(&file_path, "test").unwrap();

        assert!(file_exists(file_path_str));
    }

    #[test]
    fn test_get_file_size() {
        let dir = tempdir().unwrap();
        let file_path = dir.path().join("test.txt");
        let file_path_str = file_path.to_str().unwrap();

        let content = "Hello, Rust!";
        write_file_fast(file_path_str, content).unwrap();

        let size = get_file_size(file_path_str).unwrap();
        assert_eq!(size, content.len() as u64);
    }

    #[test]
    fn test_copy_move_delete() {
        let dir = tempdir().unwrap();
        let source = dir.path().join("source.txt");
        let dest = dir.path().join("dest.txt");
        let source_str = source.to_str().unwrap();
        let dest_str = dest.to_str().unwrap();

        // Create source file
        write_file_fast(source_str, "Test content").unwrap();

        // Copy
        copy_file_fast(source_str, dest_str).unwrap();
        assert!(file_exists(dest_str));

        // Delete
        delete_file(dest_str).unwrap();
        assert!(!file_exists(dest_str));
    }
}
