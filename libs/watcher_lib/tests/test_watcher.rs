use std::{fs::File, io::Write, thread, time::Duration};
use tempfile::TempDir;
use watcher_lib::FileWatcher;

#[test]
fn test_file_watcher() {
    let temp_dir = TempDir::new().expect("Failed to create temp dir");
    let temp_dir_path = temp_dir.path().to_str().expect("Failed to get temp dir path");

    let watcher = FileWatcher::new(temp_dir_path);

    let callback = |file: String| {
        assert!(file.contains("test"));
    };

    thread::spawn(move || {
        watcher.watch(callback).unwrap();
    });

    let file_path = temp_dir.path().join("test_file.txt");
    let mut file = File::create(&file_path).expect("Failed to create file");
    writeln!(file, "This is a test file").expect("Failed to write to file");

    thread::sleep(Duration::from_secs(2));

}
