use tensorflow as tf;
use ndarray::Array;
use std::fs::File;
use std::path::Path;
use std::io::prelude::*;

fn extract_byte_sequence(file_path: &str, seq_length: usize) -> Vec<f32> {
    let mut file = File::open(file_path).expect("Unable to open file");
    let mut buffer = vec![0; seq_length];
    
    file.read_exact(&mut buffer).expect("Unable to read file");

    // Normalize the byte sequence (as you did in Python)
    let max_value = 255.0;  // since byte values are between 0 and 255
    buffer.iter().map(|&byte| byte as f32 / max_value).collect()
}

fn predict_file(model: &tf::SavedModel, file_path: &str, seq_length: usize) -> String {
    // Extract byte sequence from file
    let byte_sequence = extract_byte_sequence(file_path, seq_length);

    // Convert to a TensorFlow tensor
    let tensor = tf::Tensor::new(&[1, seq_length as i64, 1])
        .with_values(&byte_sequence)
        .expect("Unable to create tensor");

    // Create a session and run inference
    let mut session = model.session().expect("Unable to create session");
    let result = session
        .run(&[("serving_default_input:0", &tensor)], &["dense_1/Softmax:0"])
        .expect("Failed to run inference");

    // Check if the file is "bad" or "good" based on the prediction
    if result[0].to_vec()[0] > 0.5 {
        "Bad file".to_string()
    } else {
        "Good file".to_string()
    }
}

fn main() {
    // Load the trained model
    let model_path = Path::new("bad_file_anomaly_detector"); // Path to the saved model directory
    let model = tf::SavedModel::load(model_path, &["serve"]).expect("Failed to load model");

    // Predict on a file
    let file_path = "path/to/your/file"; // Replace with actual file path
    let result = predict_file(&model, file_path, 4096);
    
    println!("Prediction result: {}", result);
}
