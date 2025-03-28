
use fern::Dispatch;
use chrono::Local;
use std::fs::OpenOptions;
pub struct Logging {
}

impl Logging {
    
    pub fn setup_logger(log_file: &str) -> Result<(), fern::InitError> {
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
    
}
