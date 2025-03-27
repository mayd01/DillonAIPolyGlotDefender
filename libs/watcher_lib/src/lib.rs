use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::Path;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;
use log::{error, info};

pub struct FileWatcher {
    path: String,
}

impl FileWatcher {
    pub fn new(path: &str) -> Self {
        Self {
            path: path.to_string(),
        }
    }

    pub fn watch<F>(&self, callback: F) -> Result<(), Box<dyn std::error::Error>>
    where
        F: Fn(String) + Send + 'static,
    {
        let (tx, rx) = channel();

        let mut watcher = RecommendedWatcher::new(tx, Config::default())?;

        let path = Path::new(&self.path);

        let result = watcher.watch(path, RecursiveMode::Recursive);
        if let Err(e) = result {
            return Err(Box::new(e));
        }

        if !path.exists() {
            panic!("ERROR: Directory does not exist - {}", self.path);
        }

        info!("Watching for new files in: {:?}", path);

        thread::spawn(move || {
            for res in rx {
                match res {
                    Ok(Event { kind, paths, .. }) => {
                        match kind {
                            EventKind::Create(_) | EventKind::Modify(_) => {
                                for path in paths {
                                    if let Some(file_path) = path.to_str() {
                                        callback(file_path.to_string());
                                    }
                                }
                            }
                            _ => {} 
                        }
                    }
                    Err(e) => {
                        error!("Watch error: {:?}", e);
                    }
                }
            }
        });
        loop {
            thread::sleep(Duration::from_secs(1)); 
        }
    }
}
