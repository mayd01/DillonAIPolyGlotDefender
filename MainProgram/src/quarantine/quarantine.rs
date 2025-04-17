use serde::{Deserialize, Serialize};
use std::{fs, io::Write, path::Path};
use time::OffsetDateTime;
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct QuarantineLog {
    pub original_path: String,
    pub hash: String,
    pub quarantined_path: String,
    pub timestamp: String,
}
pub fn log_to_json(metadata_path: &Path, log: &QuarantineLog) -> std::io::Result<()> {
    let mut logs = if metadata_path.exists() {
        let data = fs::read_to_string(metadata_path)?;
        serde_json::from_str::<Vec<QuarantineLog>>(&data).unwrap_or_default()
    } else {
        Vec::new()
    };
    logs.push((*log).clone());
    let json = serde_json::to_string_pretty(&logs)?;
    let mut file = fs::File::create(metadata_path)?;
    file.write_all(json.as_bytes())?;
    Ok(())
}
pub fn create_log(original: &str, hash: &str, quarantined: &str) -> QuarantineLog {
    QuarantineLog {
        original_path: original.to_string(),
        hash: hash.to_string(),
        quarantined_path: quarantined.to_string(),
        timestamp: match time::format_description::parse("%Y-%m-%d %H:%M:%S") {
            Ok(format) => OffsetDateTime::now_utc().format(&format).unwrap_or_else(|_| "Invalid timestamp".to_string()),
            Err(_) => "Invalid timestamp".to_string(),
        },
    }
}

