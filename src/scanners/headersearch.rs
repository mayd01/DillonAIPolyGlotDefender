use std::fs::File;
use std::io::{BufReader, Read};
use std::path::Path;

const MAGIC_BYTES: &[(&[u8], &str)] = &[
    (b"%PDF", "PDF"),                // PDF
    (b"PK\x03\x04", "ZIP"),          // ZIP
    (b"Rar!\x1A\x07\x00", "RAR"),    // RAR
    (b"7z\xBC\xAF\x27\x1C", "7Z"),   // 7z
    (b"PK\x07\x08", "JAR"),          // JAR (Java Archive)
    
    (b"\xFF\xD8\xFF", "JPEG"),      // JPEG
    (b"\x89PNG\r\n\x1A\n", "PNG"),  // PNG
    (b"GIF87a", "GIF"),             // GIF
    (b"GIF89a", "GIF"),             // GIF
    (b"BM", "BMP"),                 // BMP
    (b"\x00\x00\x00\x18", "TIFF"), // TIFF
    (b"II\x2A\x00", "TIFF"),        // TIFF (little-endian)
    (b"MM\x00\x2A\x00", "TIFF"),    // TIFF (big-endian)
    
    (b"ID3", "MP3"),                // MP3
    (b"OggS", "OGG"),               // OGG
    (b"RIFF", "WAV"),               // WAV
    (b"FLV", "FLV"),                // FLV
    (b"fLaC", "FLAC"),              // FLAC
    (b"MP4", "MP4"),                // MP4
    (b"ftyp", "MP4"),               // MP4 (ftyp box)
    (b"WEBM", "WEBM"),              // WEBM
    
    (b"MZ", "EXE/DLL"),             // Windows Executable (EXE/DLL)
    (b"ELF", "ELF"),                // ELF (Executable and Linkable Format)
    (b"#!/bin/sh", "Shell Script"), // Unix shell script
    (b"\x7FELF", "ELF"),            // ELF (with magic number)
    
    (b"!<arch>", "AR"),             // Unix Archive (AR)
    (b"USTAR", "TAR"),              // TAR Archive
    (b"bzip2", "BZ2"),              // BZIP2
    (b"\x1F\x8B", "GZIP"),          // GZIP
    (b"PK\x05\x06", "ZIP (Empty)"), // ZIP (Empty or Directory Entry)

    (b"PMagic", "Parted Magic"),    // Parted Magic
    (b"VHD", "VHD Disk Image"),     // VHD Disk Image
    (b"\xEB\x58\x90", "ISO 9660"), // ISO 9660 Disk Image

    (b"\x00\x01\x42\x44", "Microsoft CAB"), // Microsoft CAB (CABINET) Files
    (b"\x52\x61\x72\x21", "RAR (Version 1.x)"), // Old RAR (Version 1.x)
    (b"\x1F\x9D\x90\x00", "XZ"), // XZ compressed file
    (b"MSCF", "Microsoft System File"), // MSCF (Microsoft System File)
    (b"VMS", "VMS Filesystem")     // VMS Filesystem
];

pub fn is_polyglot(file: &str) -> bool {
    let path = Path::new(file);
    if !path.exists() {
        eprintln!("Error: File does not exist.");
        return false;
    }

    let mut buffer = [0; 10024]; 
    let file = File::open(file).expect("Unable to open file");
    let mut reader = BufReader::new(file);

    if let Ok(bytes_read) = reader.read(&mut buffer) {
        let file_content = &buffer[..bytes_read];
        let mut detected_signatures = Vec::new();
        for (magic, file_type) in MAGIC_BYTES.iter() {

            if file_content.windows(magic.len()).any(|window| window == *magic) {
                detected_signatures.push(*file_type);
            }
        }
        // print!()
        if detected_signatures.len() > 1 {
            println!(
                "Potential polyglot file detected! Contains signatures for: {:?}",
                detected_signatures
            );
            return true;
        }
    }

    false
}

/// Prints detailed file analysis, showing detected headers and offsets.
pub fn analyze_file(file: &str) {
    let path = Path::new(file);
    if !path.exists() {
        eprintln!("Error: File does not exist.");
        return;
    }

    let mut buffer = [0; 4096]; // Read the first 4KB for deeper analysis
    let file = File::open(file).expect("Unable to open file");
    let mut reader = BufReader::new(file);

    if let Ok(bytes_read) = reader.read(&mut buffer) {
        let file_content = &buffer[..bytes_read];
        println!("Analyzing file: {}", path.to_string_lossy());

        for (magic, file_type) in MAGIC_BYTES.iter() {
            if let Some(pos) = file_content.windows(magic.len()).position(|window| window == *magic) {
                println!("{} signature found at offset: {}", file_type, pos);
            }
        }
    }
}
