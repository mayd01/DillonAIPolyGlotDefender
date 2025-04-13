use chrono::Local;
use colored::Colorize;
use fern::{Dispatch, log_file};
use log::{LevelFilter, Record};
use std::{env, fs, io::Write};
use tracing_appender::rolling::{RollingFileAppender, Rotation};
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt};

pub struct Logging;

impl Logging {
    pub fn setup_logger(log_file: &str, max_size_mb: u64, max_files: usize) -> Result<(), fern::InitError> {
        let log_level = env::var("RUST_LOG")
            .unwrap_or_else(|_| "debug".to_string())
            .parse::<LevelFilter>()
            .unwrap_or(LevelFilter::Debug);

        let rolling_file = RollingFileAppender::new(Rotation::DAILY, ".", log_file);

        Dispatch::new()
            .format(|out, message, record| {
                let level_str = match record.level() {
                    log::Level::Error => record.level().to_string().red(),
                    log::Level::Warn => record.level().to_string().yellow(),
                    log::Level::Info => record.level().to_string().green(),
                    log::Level::Debug => record.level().to_string().cyan(),
                    log::Level::Trace => record.level().to_string().purple(),
                };

                out.finish(format_args!(
                    "[{}] [{}] [{}] [{}] {}",
                    Local::now().format("%Y-%m-%d %H:%M:%S"),
                    level_str,
                    record.target(),
                    std::thread::current().name().unwrap_or("main"),
                    message
                ))
            })
            .level(log_level)
            .chain(std::io::stdout()) 
            .chain(Box::new(rolling_file) as Box<dyn Write + Send>)     
            .apply()?;

        Self::cleanup_old_logs(log_file, max_files);

        Ok(())
    }

    fn cleanup_old_logs(log_file: &str, max_files: usize) {
        if let Some(log_dir) = std::path::Path::new(log_file).parent() {
            if let Ok(entries) = fs::read_dir(log_dir) {
                let mut log_files: Vec<_> = entries
                    .filter_map(|entry| entry.ok())
                    .filter(|entry| entry.file_name().to_string_lossy().starts_with("app.log"))
                    .collect();

                log_files.sort_by_key(|entry| entry.metadata().and_then(|m| m.modified()).ok());

                if log_files.len() > max_files {
                    for old_file in log_files[..log_files.len() - max_files].iter() {
                        let _ = fs::remove_file(old_file.path());
                    }
                }
            }
        }
    }
}
