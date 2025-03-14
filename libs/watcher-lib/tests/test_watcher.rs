use std::{fs::File, io::Write, thread, time::Duration};
use tempfile::TempDir;
use watcher_lib::FileWatcher;

#[test]
fn test_file_watcher() {
    // Step 1: Create a temporary directory for testing
    let temp_dir = TempDir::new().expect("Failed to create temp dir");
    let temp_dir_path = temp_dir.path().to_str().expect("Failed to get temp dir path");

    // Step 2: Create a file watcher for the temporary directory
    let watcher = FileWatcher::new(temp_dir_path);

    // Step 3: Simulate the callback logic for testing purposes
    let callback = |file: String| {
        // Assert that the filename contains "test"
        assert!(file.contains("test"));
    };

    // Step 4: Spawn a thread to run the file watcher
    thread::spawn(move || {
        // Watch the directory
        watcher.watch(callback).unwrap();
    });

    // Step 5: Simulate file creation (this would trigger the watcher)
    let file_path = temp_dir.path().join("test_file.txt");
    let mut file = File::create(&file_path).expect("Failed to create file");
    writeln!(file, "This is a test file").expect("Failed to write to file");

    // Wait for the watcher to detect the file (you can adjust the duration if necessary)
    thread::sleep(Duration::from_secs(2));

    // Step 6: Clean up (the TempDir will be automatically cleaned up at the end of the test)
    // No additional cleanup needed, as tempfile handles it.
}
