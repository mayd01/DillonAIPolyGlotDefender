use log::{error, info};
use notify::{Config, Event, EventKind, RecommendedWatcher, RecursiveMode, Watcher};
use std::{
    collections::HashSet,
    fs::OpenOptions,
    path::{Path, PathBuf},
    sync::{mpsc::channel, Arc, Mutex},
    thread,
    time::Duration,
};
pub struct FileWatcher {
    path: String,
    processed_files: Arc<Mutex<HashSet<PathBuf>>>,
}

impl FileWatcher {
    pub fn new(path: &str) -> Self {
        Self {
            path: path.to_string(),
            processed_files: Arc::new(Mutex::new(HashSet::new())),
        }
    }
    pub fn watch<F>(&self, callback: F) -> Result<(), Box<dyn std::error::Error>>
    where
        F: Fn(String) + Send + 'static + Clone,
    {
        let (tx, rx) = channel();
        let mut watcher = RecommendedWatcher::new(tx, Config::default())?;
        let path = Path::new(&self.path);
        if !path.exists() {
            panic!("ERROR: Directory does not exist - {}", self.path);
        }
        watcher.watch(path, RecursiveMode::Recursive)?;
        let processed_files = Arc::clone(&self.processed_files);
        info!("Watching for new files in: {:?}", path);
        thread::spawn(move || {
            for res in rx {
                match res {
                    Ok(Event { kind, paths, .. }) => {
                        if matches!(kind, EventKind::Create(_) | EventKind::Modify(_)) {
                            for path in paths {
                                let file_path = path.clone();
                                let file_str = file_path.to_string_lossy().to_string();
                                let mut processed = processed_files.lock().unwrap();
                                if processed.contains(&file_path) {
                                    continue; // Skip if already being processed
                                }
                                processed.insert(file_path.clone());
                                drop(processed);
                                let processed_files = Arc::clone(&processed_files);
                                let callback = callback.clone();
                                thread::spawn(move || {
                                    if Self::wait_for_file_ready(&file_path) {
                                        callback(file_str);
                                    }
                                    let mut processed = processed_files.lock().unwrap();
                                    processed.remove(&file_path);
                                });
                            }
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
    fn wait_for_file_ready(path: &Path) -> bool {
        for _ in 0..10 {
            if let Ok(_) = OpenOptions::new().read(true).open(path) {
                return true;
            }
            thread::sleep(Duration::from_secs(1));
        }
        false
    }
}
