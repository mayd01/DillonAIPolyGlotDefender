use tensorflow::{Graph, Session, SessionOptions, SessionRunArgs, Tensor};
use std::fs::File;
use std::io::{self, Read};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum PolyglotError {
    #[error("File I/O error: {0}")]
    FileIO(#[from] io::Error),
    #[error("TensorFlow error: {0}")]
    TensorFlowError(#[from] tensorflow::Status),
    #[error("Invalid data format")]
    InvalidData,
}

pub fn extract_features(file_path: &str, regions: &[(usize, Option<usize>)]) -> Result<Vec<f32>, PolyglotError> {
    let mut file = File::open(file_path)?;
    let mut data = Vec::new();
    file.read_to_end(&mut data)?;

    if data.len() < 256 {
        eprintln!("Skipping {}: File too small", file_path);
        return Err(PolyglotError::InvalidData);
    }

    let mut features = Vec::new();
    for &(start, end) in regions {
        let end_index = end.unwrap_or(data.len());
        features.extend(data[start..end_index].iter().map(|&b| b as f32 / 255.0));
    }

    Ok(features)
}

pub fn classify_file(model_path: &str, file_path: &str) -> Result<f32, PolyglotError> {
    let features = extract_features(file_path, &[(0, 256), (data.len().saturating_sub(256), None)])?;
    
    let mut graph = Graph::new();
    let mut session = Session::new(&SessionOptions::new(), &graph)?;

    let input_tensor = Tensor::new(&[1, features.len() as u64, 1]).with_values(&features)?;
    let output_tensor = Tensor::new(&[1]);

    let mut run_args = SessionRunArgs::new();
    run_args.add_feed("input_node", 0, &input_tensor);
    let output_token = run_args.request_fetch("output_node", 0);

    session.run(&mut run_args)?;
    let output: f32 = run_args.fetch(output_token)?[0];

    Ok(output)
}
