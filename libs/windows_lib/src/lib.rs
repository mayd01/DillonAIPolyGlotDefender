// notification_lib/src/lib.rs

use notify_rust::Notification;

#[cfg(target_os = "windows")]
pub fn send_notification(title: &str, message: &str) -> Result<(), Box<dyn std::error::Error>> {
    Notification::new()
        .summary(title)
        .body(message)
        .show()?;

    Ok(())
}

#[cfg(not(target_os = "windows"))]
pub fn send_notification(_: &str, _: &str) -> Result<(), Box<dyn std::error::Error>> {
    // No-op for non-Windows platforms, you can add other platform-specific code here if needed.
    Ok(())
}
