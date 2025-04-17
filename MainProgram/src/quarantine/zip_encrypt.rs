use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;
use zip::write::FileOptions;

pub fn zip_and_encrypt_file(
    original: &Path,
    destination: &Path,
    password: &str,
) -> std::io::Result<()> {
    let zip_file = File::create(destination)?;
    let mut zip = zip::ZipWriter::new(zip_file);
    let options = FileOptions::default().compression_method(zip::CompressionMethod::Stored);
    let file_name = original.file_name().unwrap().to_string_lossy();
    zip.start_file(file_name, options)?;

    let mut source = File::open(original)?;
    let mut buffer = Vec::new();
    source.read_to_end(&mut buffer)?;
    let encrypted: Vec<u8> = buffer
        .iter()
        .zip(password.bytes().cycle())
        .map(|(&b, p)| b ^ p)
        .collect();
    zip.write_all(&encrypted)?;
    zip.finish()?;
    Ok(())
}

pub fn decrypt_and_extract_file(
    zip_path: &Path,
    extract_to: &Path,
    password: &str,
) -> std::io::Result<()> {
    let zip_file = File::open(zip_path)?;
    let mut archive = zip::ZipArchive::new(zip_file)?;
    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let out_path = extract_to.join(file.name());
        let mut encrypted_data = Vec::new();
        file.read_to_end(&mut encrypted_data)?;
        // XOR decryption
        let decrypted: Vec<u8> = encrypted_data
            .iter()
            .zip(password.bytes().cycle())
            .map(|(&b, p)| b ^ p)
            .collect();
        let mut out_file = File::create(out_path)?;
        out_file.write_all(&decrypted)?;
    }
    Ok(())
}
