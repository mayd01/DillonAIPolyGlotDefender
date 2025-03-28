use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Result};
use std::path::Path;

struct FileType {
    magic_bytes: Vec<u8>,
    extension: String,
}

impl FileType {
    fn new(magic_bytes: Vec<u8>, extension: &str) -> Self {
        Self {
            magic_bytes,
            extension: extension.to_string(),
        }
    }
}

struct FileChecker {
    file_types: HashMap<String, FileType>,
}

impl FileChecker {
    fn new() -> Self {
        let mut file_types = HashMap::new();

        file_types.insert(
            "exe".to_string(),
            FileType::new(vec![0x4D, 0x5A], "exe"),
        );
        file_types.insert(
            "elf".to_string(),
            FileType::new(vec![0x7F, 0x45, 0x4C, 0x46], "elf"),
        );
        file_types.insert(
            "zip".to_string(),
            FileType::new(vec![0x50, 0x4B, 0x03, 0x04], "zip"),
        );

        Self { file_types }
    }

    fn get_extension(file_path: &str) -> Option<String> {
        Path::new(file_path)
            .extension()
            .and_then(|ext| ext.to_str())
            .map(|ext| ext.to_lowercase())
    }

    pub fn check_file_extension_mismatch(&self, file_path: &str) -> bool {
        let mut file = match File::open(file_path) {
            Ok(file) => file,
            Err(e) => {
                eprintln!("Error opening file: {}", e);
                return false; 
            }
        };
    
        let mut buffer = [0; 8];
        if let Err(e) = file.read_exact(&mut buffer) {
            eprintln!("Error reading file: {}", e);
            return false; 
        }
    
        let mut detected_type = "unknown";
        for file_type in self.file_types.values() {
            if buffer.starts_with(&file_type.magic_bytes) {
                detected_type = &file_type.extension;
                break;
            }
        }
    
        if let Some(extension) = FileChecker::get_extension(file_path) {
            if extension != detected_type {
                return false;
            } else {
                return true;
            }
        } else {
            return false;
        }
    }
    
}
