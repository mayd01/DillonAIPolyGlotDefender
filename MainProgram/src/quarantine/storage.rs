use super::hash::sha256_hash;
use super::zip_encrypt::zip_and_encrypt_file;
use super::quarantine::{log_to_json, create_log};
use std::fs;
use std::path::{Path, PathBuf};
pub struct QuarantineManager {
    quarantine_dir: PathBuf,
    metadata_path: PathBuf,
    password: String,
}
impl QuarantineManager {
    pub fn new<P: Into<PathBuf>>(dir: P, password: String) -> Self {
        let dir = dir.into();
        fs::create_dir_all(&dir).unwrap();
        let metadata_path = dir.join("quarantine_log.json");
        Self {
            quarantine_dir: dir,
            metadata_path,
            password,
        }
    }

    pub fn quarantine_file(&self, original_path: &Path) -> std::io::Result<PathBuf> {
        let hash = sha256_hash(original_path)?;
        let file_name = format!("{}.zip", hash);
        let zip_path = self.quarantine_dir.join(&file_name);
        zip_and_encrypt_file(original_path, &zip_path, &self.password)?;
        fs::remove_file(original_path)?;
        let log = create_log(
            &original_path.display().to_string(),
            &hash,
            &zip_path.display().to_string(),
        );
        log_to_json(&self.metadata_path, &log)?;
        Ok(zip_path)
    }

    pub fn list_quarantined_files(&self) -> Vec<PathBuf> {
        let mut files = Vec::new();
        if let Ok(entries) = fs::read_dir(&self.quarantine_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|s| s.to_str()) == Some("zip") {
                    files.push(path);
                }
            }
        }
        files
    }

    pub fn restore_file(&self, quarantined_path: &Path, restore_dir: &Path) -> std::io::Result<()> {
        // Create the restore directory if it doesn't exist
        std::fs::create_dir_all(restore_dir)?;

        // Build the full restore path
        let file_name = quarantined_path.file_stem().unwrap_or_default();
        let restored_file_path = restore_dir.join(file_name);
        super::zip_encrypt::decrypt_and_extract_file(quarantined_path, &restored_file_path, &self.password)?;

        Ok(())
    }
}
