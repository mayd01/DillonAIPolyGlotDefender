use lopdf::{Document, Object};
use std::fs::{self, File};
use std::error::Error as StdError;
use std::io::Read;
use log::{debug, error, info, warn};
use std::fmt::Write;

pub fn sanitize_pdf(file_path: &str) -> Result<(), String> {
    if !file_path.to_lowercase().ends_with(".pdf") {
        return Err("Invalid file type: Not a PDF.".to_string());
    }

    
    let mut file = match File::open(file_path) {
        Ok(f) => f,
        Err(_) => return Err("Failed to open file.".to_string()),
    };
    
    let mut buffer = [0; 5]; 
    if let Err(_) = file.read_exact(&mut buffer) {
        return Err("Failed to read file header.".to_string());
    }

    if buffer != *b"%PDF-" {
        return Err("Invalid file format: Missing PDF signature.".to_string());
    }

    match Document::load(file_path) {
        Ok(mut doc) => {
            sanitize_pdf_structure(&mut doc)?;
            doc.save(file_path).map_err(|_| "Failed to save sanitized PDF.".to_string())?;
            Ok(())
        }
        Err(_) => Err("Invalid PDF structure.".to_string()),
    }
}

fn sanitize_pdf_structure(doc: &mut Document) -> Result<(), String> {
    println!("Started sanitization...");

    for (_, obj) in doc.objects.iter_mut() {
        match obj {
            Object::Dictionary(dict) => {
                let mut removed_keys = Vec::new();

                let keys_to_remove: [&[u8]; 10] = [
                    b"JavaScript", b"JS", b"EmbeddedFiles", b"AA", b"OpenAction",
                    b"Launch", b"URI", b"GoTo", b"Metadata", b"CustomMetadata"
                ];

                for key in keys_to_remove {
                    if dict.get(key).is_ok() {
                        removed_keys.push(String::from_utf8_lossy(key).to_string());
                        dict.remove(key);
                    }
                }

                if !removed_keys.is_empty() {
                    let mut log_message = String::new();
                    write!(&mut log_message, "Removed keys: ").map_err(|_| "Log write error")?;

                    for key in &removed_keys {
                        write!(&mut log_message, "{} ", key).map_err(|_| "Log write error")?;
                    }

                    println!("{}", log_message);
                }
            }
            _ => {}
        }
    }
    println!("Sanitization complete.");
    Ok(())
}
