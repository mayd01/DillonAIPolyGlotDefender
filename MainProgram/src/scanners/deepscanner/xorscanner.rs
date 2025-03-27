use std::fs::File;
use std::io::{self, Read};

const XOR_THRESHOLD: usize = 4; 


pub fn detect_xor_anomalies(file_path: &str) -> io::Result<()> {
    let mut file = File::open(file_path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    for key_size in 1..=XOR_THRESHOLD {
        let mut score = 0;
        for i in 0..(buffer.len() - key_size) {
            if buffer[i] == buffer[i + key_size] {
                score += 1;
            }
        }
        if score > buffer.len() / 10 {
            println!("Potential XOR anomaly detected with key size: {}", key_size);
        }
    }
    
    Ok(())
}