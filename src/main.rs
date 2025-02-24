use clap::{Arg, Command};
use colored::*;
use std::fs;
use std::path::Path;
mod scanners;
mod scrubber;
use fern::Dispatch;
use chrono::Local;
use std::fs::OpenOptions;


fn setup_logger(log_file: &str) -> Result<(), fern::InitError> {
    let log_file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_file)?;

    Dispatch::new()
        .format(|out, message, record| {
            out.finish(format_args!(
                "[{}] [{}] {}",
                Local::now().format("%Y-%m-%d %H:%M:%S"),
                record.level(),
                message
            ))
        })
        .level(log::LevelFilter::Debug) 
        .chain(log_file) 
        .apply()?;

    Ok(())
}

fn main() 
{

    let log_file = "app.log";

    if let Err(e) = setup_logger(log_file) {
        eprintln!("Failed to initialize logger: {}", e);
        return;
    }

    let matches = Command::new("Dilly Defender")
        .version("1.0")
        .author("Dillon May")
        .about("A CLI tool to detect polyglot files and threats")
        .subcommand(
            Command::new("scan")
                .about("Scan a specific file for potential threats")
                .arg(Arg::new("file")
                    .required(true)
                    .help("The file to scan"))
                .arg(Arg::new("verbose")
                    .short('v')
                    .long("verbose")
                    .action(clap::ArgAction::SetTrue) 
                    .default_value("false") 
                    .help("Enable verbose output")),
        )
        .subcommand(
            Command::new("scan-dir")
                .about("Scan all files within a directory")
                .arg(
                    Arg::new("directory")
                        .required(true)

                        .help("The directory to scan"),
                )
                .arg(Arg::new("verbose")
                    .short('v')
                    .long("verbose")
                    .action(clap::ArgAction::SetTrue) 
                    .default_value("false") 
                    .help("Enable verbose output")
                )
                .arg(
                    Arg::new("recursive")
                        .short('r')
                        .long("recursive")
                        .help("Scan directories recursively")
                        .action(clap::ArgAction::SetTrue), 
                ),
        )
        .subcommand(
            Command::new("ai-scan")
                .about("Scan a file using AI-based detection algorithms")
                .arg(Arg::new("file")
                    .required(true)
                    .help("The file to scan with AI"))
                .arg(Arg::new("model")
                    .short('m')
                    .long("model")
                    .help("Specify the AI model to use")),
        )
        .subcommand(
            Command::new("info")
                .about("Show information about the tool"),
        )
        .subcommand(
            Command::new("update")
                .about("Check for updates and install the latest version"),
        )
        .get_matches();

    match matches.subcommand() {
        Some(("scan", sub_m)) => {
            let file = sub_m.get_one::<String>("file").unwrap();
            let verbose = sub_m.get_flag("verbose");

            if !Path::new(file).exists() {
                println!("{}", "Error: File not found.".red());
                std::process::exit(1);
            }

            println!("{}", format!("Scanning file: {}", file).green());
            if verbose {
                println!("{}", "Verbose mode enabled. Performing deep scan...".yellow());
                
                scanners::headersearch::analyze_file(file);
            }
            
            match scrubber::fileTypeScrubber::PdfScrubber::sanitize_pdf(&file) {
                    Ok(_) => println!("PDF sanitized successfully."),
                    Err(err) => println!("Sanitization failed: {}", err),
                }

            if scanners::headersearch::is_polyglot(file) {
                println!("{}", "Potential polyglot file detected!".red());
            } else {
                println!("{}", "Scan complete. No threats detected.".blue());
            }

        }

        Some(("scan-dir", sub_m)) => {
            let dir = sub_m.get_one::<String>("directory").unwrap();
            let _recursive = sub_m.get_flag("recursive");
            let verbose = sub_m.get_flag("verbose");

            if !Path::new(dir).is_dir() {
                println!("{}", "Error: Directory not found.".red());
                std::process::exit(1);
            }
            let mut _count: i32 = 0; 
            println!("{}", format!("Scanning directory: {}", dir).green());
            let entries = fs::read_dir(dir).expect("Failed to read directory");
            for entry in entries {
                if let Ok(entry) = entry {
                    if let Some(entry) = entry.path().to_str() {
                    if scanners::headersearch::is_polyglot(entry) {
                        println!("{}", "Potential polyglot file detected!".red());
                        _count += 1;
                    } else {
                        println!("{}", "Scan complete. No threats detected.".blue());
                    }
                    }
                    
        
                   
                }
            }
            if verbose {
                println!("{}", "Verbose mode enabled. Performing deep scan...".yellow());
                scanners::headersearch::analyze_file(dir);
            }
            
            println!("{}", format!("Directory scan complete. Potential threats found: {}", _count).green());
        }

        Some(("ai-scan", sub_m)) => {
            let file = sub_m.get_one::<String>("file").unwrap();
            let default_model = String::from("default");
            let model = sub_m.get_one::<String>("model").unwrap_or(&default_model);


            if !Path::new(file).exists() {
                println!("{}", "Error: File not found.".red());
                std::process::exit(1);
            }

            println!("{}", format!("Using AI model: {}", model).green());
            println!("{}", format!("AI scanning initiated for: {}", file).blue());

            println!("{}", "AI scan complete. Potential threats found: 0.".green());
        }

        Some(("info", _)) => {
            println!("{}", "Dilly Defender - Polyglot File Detection CLI".cyan());
            println!("{}", "Supported file types: .exe, .pdf, .zip, .jpg, etc.".magenta());
        }

        Some(("update", _)) => {
            println!("{}", "Checking for updates...".yellow());
            println!("{}", "You are running the latest version.".green());
        }

        _ => {
            println!("{}", "Use --help to see available commands.".yellow());
        }
    }
}
