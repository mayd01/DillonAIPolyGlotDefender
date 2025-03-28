use std::process::{Command, Stdio};
use std::io::{self, Write};
use std::{env, fs};
use regex::Regex;

pub fn classify_file_with_python(file_path: &str) -> Result<String, io::Error> {
    
    let exe_dir = env::current_exe()?
        .parent() 
        .ok_or(io::Error::new(io::ErrorKind::NotFound, "Executable directory not found"))?
        .to_path_buf();
    
    let script: std::path::PathBuf = exe_dir.join("Detect.py");
    
    let command = format!("python {} -F {}", script.display(), file_path);
     print!("***{}", command);
    
    let output = Command::new("/home/dmay/myenv/bin/python")
        .arg(script)
        .arg("-F")
        .arg(file_path) 
        .stdout(Stdio::piped()) 
        .stderr(Stdio::piped()) 
        .output()?; 

    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout).to_string();
        // Print the output for debugging purposes
        println!("Output: {}", stdout);
        match parse_prediction_score(&stdout) {
            Some(score) => Ok(score),
            None => Err(io::Error::new(io::ErrorKind::NotFound, "Prediction Score not found")),
        }
    } else {
        let error_message = String::from_utf8_lossy(&output.stderr).to_string();
        Err(io::Error::new(io::ErrorKind::Other, error_message))
    }
}

fn parse_prediction_score(output: &str) -> Option<String> {
    let re = Regex::new(r"predicted as\s+(\w+)").unwrap();

    if let Some(caps) = re.captures(output) {
        return Some(caps[1].to_string());
    }
    None
}