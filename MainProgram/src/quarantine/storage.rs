

use super::hash::sha256_hash;
use super::zip_encrypt::zip_and_encrypt_file;
use super::quarantine::{log_to_json, create_log, QuarantineLog};

#[cfg(target_os = "windows")]
use windows_lib::{send_notification, password_manager};
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
    #[cfg(target_os = "windows")]
    pub fn restore_file(&self, quarantined_path: &Path, restore_dir: &Path) -> std::io::Result<()> {
        std::fs::create_dir_all(restore_dir)?;
        
        if let Some(password) = Self::get_password() {
            super::zip_encrypt::decrypt_and_extract_file(quarantined_path, &restore_dir, &password)?;
        } else {
            return Err(std::io::Error::new(
                std::io::ErrorKind::Other,
                "Failed to retrieve password",
            ));
        }

        Ok(())
    }
    #[cfg(target_os = "windows")]
    pub fn get_original_path(&self, quarantined_file: &PathBuf) -> std::io::Result<PathBuf> {
        let metadata_path = self.get_metadata_path(); 
        let data = std::fs::read_to_string(&metadata_path)?;
        let logs: Vec<QuarantineLog> = serde_json::from_str(&data).unwrap_or_default();

        for log in logs {
            if quarantined_file.ends_with(&log.quarantined_path) {
                return Ok(PathBuf::from(log.original_path));
            }
        }

        Err(std::io::Error::new(
            std::io::ErrorKind::NotFound,
            "Original path not found in metadata",
        ))
    }

    #[cfg(target_os = "windows")]
    fn get_password() -> Option<String> {
        let target_name = "dilly_defender_service";
        match windows_lib::password_manager::retrieve_password_from_credential_manager(target_name) {
            Some(password) => {
                print!("Password retrieved from credential manager: {}", password);
                Some(password)
            },
            None => {
                let password = windows_lib::password_manager::generate_random_password(16);
                println!("No password found, generated a random one: {}", password);
    
                if windows_lib::password_manager::store_password_in_credential_manager(&password, target_name) {
                    Some(password)
                } else {
                    println!("Failed to store password in credential manager.");
                    None
                }
            }
        }
    }

    #[cfg(target_os = "windows")]
    fn get_metadata_path(&self) -> PathBuf {
        PathBuf::from("C:/ProgramData/DillyDefender/Quarantine/quarantine_log.json")
    }
}
