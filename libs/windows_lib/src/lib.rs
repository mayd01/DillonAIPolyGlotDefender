// notification_lib/src/lib.rs

use notify_rust::Notification;
#[cfg(target_os = "windows")]
pub mod password_manager; 

#[cfg(target_os = "windows")]
pub fn send_notification(title: &str, message: &str) -> Result<(), Box<dyn std::error::Error>> {
    Notification::new()
        .app_id(r"{6D809377-6AF0-444B-8957-A3773F02200E}\DillyDefender\dilly_defender.exe") // Use exact AppUserModelID
        .summary(title)
        .body(message)
        .icon(r"{6D809377-6AF0-444B-8957-A3773F02200E}\Defender.ico")
        .show()?;

    Ok(())
}


#[cfg(not(target_os = "windows"))]
pub fn send_notification(_: &str, _: &str) -> Result<(), Box<dyn std::error::Error>> {
    // No-op for non-Windows platforms, you can add other platform-specific code here if needed.
    Ok(())
}
