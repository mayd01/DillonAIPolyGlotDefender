use clap::{Arg, Command};
use colored::*;
use std::time::Duration;
use std::{fs, thread};
use std::path::Path;
mod scanners;
mod scrubber;
use watcher_lib;
use logging_lib;
use std::env;
use ai_lib::{
    classify_file,
    PolyglotError,
};

fn main() 
{

    let log_file = env::var("DLogger");

    if let Err(e) = logging_lib::Logging::setup_logger(log_file.unwrap_or("DillyDefender.log".to_string()).as_str()) {
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
                    .help("Enable verbose output"))
                .arg(Arg::new("sanitize")
                    .short('s')
                    .long("sanitize")
                    .help("Sanitize the after before scanning")
                    .action(clap::ArgAction::SetTrue)),
        )
        .subcommand( 
            Command::new("passive-scan")
                .about("This is a passive scan that will run in the background, watching for new files and scanning them")
                .arg(Arg::new("directory")
                    .required(true)
                    .short('d')
                    .long("directory")
                    .help("The directory to watch for new files"))
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
                .arg(Arg::new("sanitize")
                    .short('s')
                    .long("sanitize")
                    .action(clap::ArgAction::SetTrue)
                    .help("Sanitize the after before scanning")
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
            

            if sub_m.get_flag("sanitize") 
            {
                println!("{}", "Sanitizing file...".yellow());
                match scrubber::fileTypeScrubber::PdfScrubber::sanitize_pdf(&file) {
                        Ok(_) => println!("PDF sanitized successfully."),
                        Err(err) => println!("Sanitization failed: {}", err),
                    }
            }

            if scanners::headersearch::is_polyglot(file) {
                println!("{}", "Potential polyglot file detected!".red());
            } else {
                println!("{}", "Scan complete. No threats detected.".blue());
            }

        }

        Some (("passive-scan", sub_m)) => {
            let dir = sub_m.get_one::<String>("directory").unwrap();
            log::info!("Watching directory: {}", dir);
            
            let watcher = watcher_lib::FileWatcher::new(dir);
            
            let callback = |file_path: String| {
                log::info!("Callback invoked with file: {}", file_path);
                if scanners::headersearch::is_polyglot(&file_path) {
                    log::info!("{}", "Potential polyglot file detected!".red());
                } else {
                    log::info!("{}", "Scan complete. No threats detected.".blue());
                }
            };

            if let Err(e) = watcher.watch(callback) {
                log::info!("Error: {:?}", e);
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

                        if sub_m.get_flag("sanitize") 
                        {
                            println!("{}", "Sanitizing file...".yellow());
                            match scrubber::fileTypeScrubber::PdfScrubber::sanitize_pdf(&entry) {
                                    Ok(_) => println!("PDF sanitized successfully."),
                                    Err(err) => println!("Sanitization failed: {}", err),
                                }
                        }

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
            
            let model_path = "polyglot_cnn_detector_best.h5";

            match classify_file(model_path, file) {
                Ok(score) if score > 0.8 => println!("The file {} is predicted as Polyglot.", file_path),
                Ok(_) => println!("The file {} is predicted as Non-Polyglot.", file_path),
                Err(e) => eprintln!("Error: {}", e),
            }
            
            println!("{}", "AI scan complete. Potential threats found: 0.".green());
        }

        Some(("info", _)) => {
            println!("{}", "Dilly Defender - Polyglot File Detection CLI".cyan());
            println!("{}", "Supported file types:".magenta());
        
            let supported_types = vec![
                "PDF", "ZIP", "RAR", "7Z", "JAR",
                "JPEG", "PNG", "GIF", "BMP", "TIFF",
                "MP3", "OGG", "WAV", "FLV", "FLAC", "MP4", "WEBM",
                "EXE/DLL", "ELF", "Shell Script",
                "AR", "TAR", "BZ2", "GZIP", "XZ",
                "ISO 9660", "VHD Disk Image", "Microsoft CAB", "MSCF (Microsoft System File)",
                "Parted Magic", "VMS Filesystem"
            ];
        
            println!("\nDetection list:");
            for file_type in supported_types {
                println!("{}", format!("- {}", file_type).green());
            }
        
            let sanitizable_files = vec![
                "PDF", "comming soon JPG, PNG, GIF"
            ];
        
            println!("\nSanitizable files (can be cleaned/removed):");
            for file_type in sanitizable_files {
                println!("{}", format!("- {}", file_type).yellow());
            }
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
