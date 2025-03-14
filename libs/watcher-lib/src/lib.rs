use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::Path;
use std::sync::mpsc::channel;
use std::thread;
use std::time::Duration;

/// A file watcher that monitors a directory and triggers a callback on new files.
pub struct FileWatcher {
    path: String,
}

impl FileWatcher {
    /// Creates a new FileWatcher instance.
    ///
    /// # Arguments
    ///
    /// * `path` - The directory to watch.
    pub fn new(path: &str) -> Self {
        Self {
            path: path.to_string(),
        }
    }

    /// Starts watching the directory and executes the callback when a new file is detected.
    ///
    /// # Arguments
    ///
    /// * `callback` - A function to call when a new file is detected.
    pub fn watch<F>(&self, callback: F) -> Result<(), Box<dyn std::error::Error>>
    where
        F: Fn(String) + Send + 'static,
    {
        let (tx, rx) = channel();

        // Create a watcher instance
        let mut watcher = RecommendedWatcher::new(tx, Config::default())?;

        // Watch the directory (non-recursive to track only top-level files)
        let path = Path::new(&self.path);
        watcher.watch(path, RecursiveMode::NonRecursive)?;

        println!("Watching for new files in: {:?}", path);

        thread::spawn(move || {
            for res in rx {
                match res {
                    Ok(Event { paths, .. }) => {
                        for path in paths {
                            if let Some(file_path) = path.to_str() {
                                println!("New file detected: {}", file_path);
                                callback(file_path.to_string());
                            }
                        }
                    }
                    Err(e) => eprintln!("Watch error: {:?}", e),
                }
            }
        });

        Ok(())
    }
}
