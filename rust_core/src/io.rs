//! File I/O utilities

pub fn read_file_fast(path: &str) -> Result<String, std::io::Error> {
    std::fs::read_to_string(path)
}
