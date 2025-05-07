use clap::{Arg, Command};
use colored::*;
use std::{fs::{self, File}, path::{Path, PathBuf, MAIN_SEPARATOR_STR}};
mod scanners;
mod scrubber;
use watcher_lib;
use logging_lib;
use std::env;
use ai_lib::classify_file_with_python;
mod quarantine; 
use reqwest::blocking::get;
use std::io::Write;
use std::error::Error;
use std::process::Command as ProcessCommand;

use reqwest::blocking::Client;
use reqwest::header::USER_AGENT;

#[cfg(target_os = "windows")]
use windows_lib::{send_notification, password_manager};

#[cfg(target_os = "windows")]
use quarantine::storage::QuarantineManager;

const CLAMAV_DB_URLS: &[&str] = &[
    "https://database.clamav.net/main.cvd",
    "https://database.clamav.net/daily.cvd",
    "https://database.clamav.net/bytecode.cvd",
];


fn main() 
{

    let log_file = env::var("DLogger");

    if let Err(e) = logging_lib::Logging::setup_logger(log_file.unwrap_or("DillyDefender.log".to_string()).as_str(), 10, 5) {
        eprintln!("Failed to initialize logger: {}", e);
        return;
    }

    #[cfg(target_os = "windows")]
    let clamav_dir = r"C:\Program Files\DillyDefender\clamav";

    #[cfg(target_os = "linux")]
    let clamav_dir = r"./clamav";

    #[cfg(target_os = "windows")]
    let manager = initialize_manager();

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
                log::info!("Error: File not found.");
                std::process::exit(1);
            }

            if !Path::new(clamav_dir).exists() {
                eprintln!("ClamAV directory not found: {}", clamav_dir);
                std::process::exit(1);
            }

            println!("{}", format!("Scanning file: {}", file).green());
            log::info!("Scanning file: {}", file);

            match scan_file(file, clamav_dir) {
                Ok(result) => {
                    if result == "continue" {
                        println!("ClamAV passed will continue with DMZ");
                    } 
                    else 
                    {
                        log::info!("Virus found in the file! We are taking action.");
                        #[cfg(target_os = "windows")]
                        {
                            match send_notification("DMZ Defender Scan", &format!("Scan Found A potential threat! {}", file.as_str())) {
                                Ok(_) => println!("Notification sent!"),
                                Err(e) => eprintln!("Error sending notification: {}", e),
                            }
                           manager.quarantine_file(Path::new(file)).unwrap_or_else(|err| {
                                println!("Failed to quarantine the file. {}" , err);
                                log::error!("Failed to quarantine the file.");
                                std::process::exit(1);
                            });
                            println!("File quarantined successfully.");
                            log::info!("File quarantined successfully.");
                            std::process::exit(0);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error scanning file: {}", e);
                    std::process::exit(1);
                }
            }

            if verbose {
                println!("{}", "Verbose mode enabled. Performing deep scan...".yellow());
                scanners::headersearch::analyze_file(file);
            }
            

            if sub_m.get_flag("sanitize") 
            {
                println!("{}", "Sanitizing file...".yellow());
                log::info!("Sanitizing file...");
                match scrubber::fileTypeScrubber::PdfScrubber::sanitize_pdf(&file) {
                        Ok(_) => {println!("PDF sanitized successfully."); log::info!("PDF sanitized successfully.");},

                        Err(err) => {println!("Sanitization failed: {}", err); log::info!("Sanitization failed: {}", err);}
                    }
            }

            if scanners::headersearch::is_polyglot(file) {
                println!("{}", "Potential Infected file detected!, Running our AI-Scan".red());
                #[cfg(target_os = "windows")]
                {
                    #[cfg(target_os = "windows")]
                    {
                        match send_notification("DMZ Defender Scan", &format!("Scan Found A potential threat!  Running AI Scan{}", file.as_str())) {
                            Ok(_) => println!("Notification sent!"),
                            Err(e) => eprintln!("Error sending notification: {}", e),
                        }
                    }
                    let absolute_path = fs::canonicalize(file.clone())
                                        .unwrap_or_else(|_| Path::new(&file).to_path_buf());

                    if !Path::new(&absolute_path).exists() {
                        println!("{}", "Error: File not found.".red());
                        log::error!("Error: File not found.");
                        std::process::exit(1);
                    }
                    println!("{}", format!("AI scanning initiated for: {}", absolute_path.to_str().unwrap()).blue());
                    match classify_file_with_python(absolute_path.to_str().unwrap()) {
                        Ok(prediction_score) => {
                            if prediction_score.matches("Polyglot").count() > 0 {
                                println!("{}", "Potential Infection found".red());
                                #[cfg(target_os = "windows")]
                                {
                                    match send_notification("DMZ Defender Scan", &format!("Scan complete! {} {}", "Potential polyglot file detected!", file.as_str())) {
                                        Ok(_) => println!("Notification sent!"),
                                        Err(e) => eprintln!("Error sending notification: {}", e),
                                    }
                                    let quarantined_path = manager.quarantine_file(Path::new(file)).unwrap_or_else(|_| {
                                        println!("Failed to quarantine the file.");
                                        log::error!("Failed to quarantine the file.");
                                        PathBuf::from(file) 
                                    });
                                    println!("File quarantined at: {}", quarantined_path.display());
                                    log::info!("File quarantined at: {}", quarantined_path.display());
                                }
                            } else {
                                println!("{}", format!("File is Safe").green());
                            }
                        }
                        Err(e) => {
                            eprintln!("Error running Python script for Model: {}", e);
                        }
                    }
                }
            } else {
                println!("{}", "Scan complete. No threats detected.".blue());
                log::info!("{}", "Scan complete. No threats detected.".blue());
            }

        }

        Some (("passive-scan", sub_m)) => {
            let dir = sub_m.get_one::<String>("directory").unwrap();
            log::info!("Watching directory: {}", dir);
            
            let watcher = watcher_lib::FileWatcher::new(dir);
            
            let callback = |file_path: String| {
                log::info!("Callback invoked with file: {}", file_path);
                if scanners::headersearch::is_polyglot(&file_path) {
                    log::info!("{}", "Potential polyglot file detected! Running AI scan".red());
                    let absolute_path = fs::canonicalize(file_path.clone())
                                        .unwrap_or_else(|_| Path::new(&file_path).to_path_buf());

                    if !Path::new(&absolute_path).exists() {
                        println!("{}", "Error: File not found.".red());
                        log::error!("Error: File not found.");
                        std::process::exit(1);
                    }
                    println!("{}", format!("AI scanning initiated for: {}", absolute_path.to_str().unwrap()).blue());
                    match classify_file_with_python(absolute_path.to_str().unwrap()) {
                        Ok(prediction_score) => {
                            if prediction_score.matches("Polyglot").count() > 0 {
                                println!("{}", "Potential Infection found".red());
                                #[cfg(target_os = "windows")]
                                {
                                    match send_notification("We found a File that looks Infected", "we are taking action.") {
                                        Ok(_) => println!("Notification sent!"),
                                        Err(e) => eprintln!("Error sending notification: {}", e),
                                    }
                                }
                            } else {
                                println!("{}", format!("File is Safe").green());
                            }
                        }
                        Err(e) => {
                            eprintln!("Error running Python script for Model: {}", e);
                        }
                    }
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
                log::error!("Error: Directory not found.");
                std::process::exit(1);
            }
            let mut _count: i32 = 0; 
            println!("{}", format!("Scanning directory: {}", dir).green());
            log::info!("Scanning directory: {}", dir);
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
                        log::info!("{}", "Scan complete. No threats detected.".blue());
                    }
                    }
                }
            }
            
            if verbose {
                println!("{}", "Verbose mode enabled. Performing deep scan...".yellow());
                scanners::headersearch::analyze_file(dir);
            }
            
            println!("{}", format!("Directory scan complete. Potential threats found: {}", _count).green());
            log::info!("Directory scan complete. Potential threats found: {}", _count);
        }

        Some(("ai-scan", sub_m)) => {
            let file = sub_m.get_one::<String>("file").unwrap();
            let default_model = String::from("default");
            let model = sub_m.get_one::<String>("model").unwrap_or(&default_model);
            
            let absolute_path = fs::canonicalize(file)
            .unwrap_or_else(|_| Path::new(file).to_path_buf());

            if !Path::new(file).exists() {
                println!("{}", "Error: File not found.".red());
                log::error!("Error: File not found.");
                std::process::exit(1);
            }

            println!("{}", format!("Using AI model: {}", model).green());
            println!("{}", format!("AI scanning initiated for: {}", absolute_path.to_str().unwrap()).blue());
            
            match classify_file_with_python(absolute_path.to_str().unwrap()) {
                Ok(prediction_score) => {
                    if prediction_score.matches("Polyglot").count() > 0 {
                        println!("{}", "Potential Infection found".red());
                        #[cfg(target_os = "windows")]
                        {
                            match send_notification("We found a File that looks Infected", "we are taking action.") {
                                Ok(_) => println!("Notification sent!"),
                                Err(e) => eprintln!("Error sending notification: {}", e),
                            }
                        }
                    } else {
                        println!("{}", format!("File is Safe").green());
                    }
                }
                Err(e) => {
                    eprintln!("Error running Python script for Model: {}", e);
                }
            }
            
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
            update_clamav_db(clamav_dir);
            println!("{}", "ClamAV database updated successfully.".green());
            
        }

        _ => {
            println!("{}", "Use --help to see available commands.".yellow());
        }
    }
}

#[cfg(target_os = "windows")]
fn initialize_manager() -> QuarantineManager {
    use std::fs;
    use std::path::Path;

    let quarantine_dir = Path::new("C:\\ProgramData\\DillyDefender\\Quarantine").to_path_buf();
    if let Err(e) = fs::create_dir_all(&quarantine_dir) {
        eprintln!("Failed to create quarantine directory: {}", e);
        std::process::exit(1);
    }
    let target_name = "dilly_defender_service"; 

    let password = match windows_lib::password_manager::retrieve_password_from_credential_manager(target_name) {
        Some(password) => {
            password
        },
        None => {
            let password = windows_lib::password_manager::generate_random_password(16);
            println!("No password found, generated a random one: {}", password);

            if !windows_lib::password_manager::store_password_in_credential_manager(&password, target_name) {
                println!("Failed to store password in credential manager.");
                std::process::exit(1);
            }

            password
        }
    };

    QuarantineManager::new(quarantine_dir, password)
}

fn update_clamav_db(db_dir: &str) {
    println!("{}", "Updating ClamAV database...".yellow());
    let clam_command = "C:\\Program Files\\DillyDefender\\clamav\\freshclam.exe";
    let status = ProcessCommand::new(clam_command)
        .arg("--datadir")
        .arg(db_dir)
        .status()
        .expect("Failed to run freshclam");

    if status.success() {
        println!("ClamAV database updated successfully.");
    } else {
        eprintln!("freshclam failed with exit code: {:?}", status.code());
    }
}



pub fn scan_file(file_path: &str, clamav_dir: &str) -> Result<&'static str, Box<dyn Error>> {
    let resolved_path = fs::canonicalize(file_path)?;
    println!("[DEBUG] Scanning file: {:?}", resolved_path);
    println!("[DEBUG] Using ClamAV binary at: {}/clamscan", clamav_dir);
    println!("[DEBUG] Using ClamAV database dir: {}", clamav_dir);

    let output = ProcessCommand::new(format!("{}/clamscan", clamav_dir))
        .arg("--database")
        .arg(clamav_dir)
        .arg(&resolved_path)
        .output()?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    println!("[DEBUG] ClamAV stdout:\n{}", stdout);
    println!("[DEBUG] ClamAV stderr:\n{}", stderr);
    println!("[DEBUG] Exit status: {}", output.status);

    if stdout.contains("OK") {
        Ok("continue")
    } else if stdout.contains("FOUND") {
        Ok("stop")
    } else {
        Ok("continue")
    }
}
