use aes::Aes128;
use block_modes::{BlockMode, Cbc};
use block_modes::block_padding::Pkcs7;
use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;
use zip::write::FileOptions;
use rand::Rng;

type Aes128Cbc = Cbc<Aes128, Pkcs7>;

pub fn zip_and_encrypt_file(
    original: &Path,
    destination: &Path,
    password: &str,
) -> std::io::Result<()> {
    let mut rng = rand::thread_rng();
    let mut iv = [0u8; 16];
    rng.fill(&mut iv);

    let key = password.as_bytes();

    let zip_file = File::create(destination)?;
    let mut zip = zip::ZipWriter::new(zip_file);
    let options = FileOptions::default().compression_method(zip::CompressionMethod::Stored);
    let file_name = original.file_name().unwrap().to_string_lossy();
    zip.start_file(file_name, options)?;

    let mut source = File::open(original)?;
    let mut buffer = Vec::new();
    source.read_to_end(&mut buffer)?;

    let cipher = Aes128Cbc::new_from_slices(key, &iv).unwrap();
    let encrypted_data = cipher.encrypt_vec(&buffer);

    zip.write_all(&iv)?;
    zip.write_all(&encrypted_data)?;
    zip.finish()?;
    Ok(())
}

pub fn decrypt_and_extract_file(
    zip_path: &Path,
    extract_to: &Path,
    password: &str,
) -> std::io::Result<()> {
    let key = password.as_bytes();

    let zip_file = File::open(zip_path)?;
    let mut archive = zip::ZipArchive::new(zip_file)?;

    for i in 0..archive.len() {
        let mut file = archive.by_index(i)?;
        let out_path = extract_to.join(file.name());

        let mut encrypted_data = Vec::new();
        file.read_to_end(&mut encrypted_data)?;

        let (iv, encrypted_data) = encrypted_data.split_at(16); 

        let cipher = Aes128Cbc::new_from_slices(key, iv).unwrap();
        let decrypted_data = cipher.decrypt_vec(encrypted_data).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;

        let mut out_file = File::create(out_path)?;
        out_file.write_all(&decrypted_data)?;
    }
    Ok(())
}
