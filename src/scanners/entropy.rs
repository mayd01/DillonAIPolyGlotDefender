use std::fs::File;
use std::io::{self, Read};
use std::collections::HashMap;

pub fn calculate_entropy(file_path: &str) -> io::Result<f64> {
   
    let mut file = File::open(file_path)?;
    
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;
    
    let mut frequency_map: HashMap<u8, usize> = HashMap::new();
    for &byte in &buffer {
        *frequency_map.entry(byte).or_insert(0) += 1;
    }
    
    let total_bytes = buffer.len() as f64;
    let entropy = frequency_map.values().fold(0.0, |acc, &count| {
        let probability = count as f64 / total_bytes;
        acc - probability * probability.log2()
    });

    Ok(entropy)
}