use std::fs;
use std::path::{Path, PathBuf};
use std::io::{self, Write};
use std::collections::HashSet;
use crate::scrubber::fileTypeScrubber;

#[derive(Debug)]
pub enum FileType {
    Pdf,
    Docx,
    Txt,
}

pub struct FileSanitizer {
    allowed_extensions: HashSet<String>,
}

impl FileSanitizer {
    pub fn new() -> Self {
        let mut allowed_extensions = HashSet::new();
        allowed_extensions.insert("pdf".to_string());
        allowed_extensions.insert("docx".to_string());
        allowed_extensions.insert("txt".to_string());

        FileSanitizer {
            allowed_extensions,
        }
    }

    pub fn sanitize(&self, file_path: &Path) -> io::Result<()> {
        let extension = match file_path.extension() {
            Some(ext) => ext.to_string_lossy().to_lowercase(),
            None => return Err(io::Error::new(io::ErrorKind::InvalidInput, "No extension found")),
        };

        if !self.allowed_extensions.contains(&extension) {
            return Err(io::Error::new(io::ErrorKind::InvalidInput, "Unsupported file type"));
        }

        match extension.as_str() {
            // "pdf" => fileTypeScrubber::sanitize_pdf(file_path),
            // "docx" => self.sanitize_docx(file_path),
            // "txt" => self.sanitize_txt(file_path),
            _ => Err(io::Error::new(io::ErrorKind::InvalidInput, "Sanitization not implemented for this type")),
        }
    }
}
