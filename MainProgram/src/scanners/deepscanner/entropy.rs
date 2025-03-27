use std::fs::File;
use std::io::{self, Read};
use std::collections::HashMap;



pub fn calculate_entropy(file_path: &str) -> io::Result<(f64, Vec<f64>)> {
    let chunk_size = 1024; 
    let mut file = File::open(file_path)?;
    let mut buffer = vec![0; chunk_size];
    let mut chunk_entropies = Vec::new();
    let mut total_entropy = 0.0;
    let mut chunk_count = 0;

    while let Ok(bytes_read) = file.read(&mut buffer) {
        if bytes_read == 0 {
            break;
        }

        let entropy = compute_entropy(&buffer[..bytes_read]);
        chunk_entropies.push(entropy);
        total_entropy += entropy;
        chunk_count += 1;
    }

    let average_entropy = if chunk_count > 0 {
        total_entropy / chunk_count as f64
    } else {
        0.0
    };

    Ok((average_entropy, chunk_entropies))
}

fn compute_entropy(data: &[u8]) -> f64 {
    let mut frequency_map: HashMap<u8, usize> = HashMap::new();
    for &byte in data {
        *frequency_map.entry(byte).or_insert(0) += 1;
    }

    let total_bytes = data.len() as f64;
    frequency_map.values().fold(0.0, |acc, &count| {
        let probability = count as f64 / total_bytes;
        acc - probability * probability.log2()
    })
}