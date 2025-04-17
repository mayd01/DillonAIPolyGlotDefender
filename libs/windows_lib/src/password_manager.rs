use std::{ffi::{CString, OsString}, os::windows::ffi::OsStrExt, ptr};
use rand::Rng;
use winapi::um::wincred::{CredWriteW, CredReadW, CREDENTIALW, CRED_TYPE_GENERIC};
use winapi::um::combaseapi::CoTaskMemFree;
use winapi::shared::minwindef::BOOL;

pub fn generate_random_password(length: usize) -> String {
    let charset = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()";
    let mut rng = rand::thread_rng();
    let password: String = (0..length)
        .map(|_| charset[rng.gen_range(0..charset.len())] as char)
        .collect();
    password
}

pub fn store_password_in_credential_manager(password: &str, target_name: &str) -> bool {
    let target_name_wide: Vec<u16> = OsString::from(target_name)
        .encode_wide()
        .chain(Some(0).into_iter()) // Null-terminate the wide string
        .collect();
    
    let password_wide: Vec<u16> = OsString::from(password)
        .encode_wide()
        .chain(Some(0).into_iter()) // Null-terminate the wide string
        .collect();

    let cred = CREDENTIALW {
        Flags: 0,
        Type: CRED_TYPE_GENERIC,
        TargetName: target_name_wide.as_ptr() as *mut u16,
        Comment: ptr::null_mut(),
        LastWritten: winapi::shared::minwindef::FILETIME { dwLowDateTime: 0, dwHighDateTime: 0 },
        CredentialBlobSize: password.len() as u32,
        CredentialBlob: password_wide.as_ptr() as *mut u8,
        Persist: 2, // CRED_PERSIST_LOCAL_MACHINE
        AttributeCount: 0,
        Attributes: ptr::null_mut(),
        TargetAlias: ptr::null_mut(),
        UserName: ptr::null_mut(),
    };

    unsafe {
        let result = CredWriteW(&cred as *const _ as *mut _, 0);
        if result == 0 {
            eprintln!("Failed to write credential to manager.");
            return false;
        }
        true
    }
}


pub fn retrieve_password_from_credential_manager(target_name: &str) -> Option<String> {
    let target_name_wide: Vec<u16> = OsString::from(target_name)
        .encode_wide()
        .chain(Some(0).into_iter()) 
        .collect();

    let mut cred_ptr: *mut CREDENTIALW = ptr::null_mut();

    unsafe {
        let result = CredReadW(target_name_wide.as_ptr(), CRED_TYPE_GENERIC, 0, &mut cred_ptr);
        if result == 0 {
            return None;
        }

        let cred = &*cred_ptr;
        let cred_blob = std::slice::from_raw_parts(cred.CredentialBlob, cred.CredentialBlobSize as usize);
        let password = String::from_utf8_lossy(cred_blob).to_string();

        CoTaskMemFree(cred_ptr as *mut _); // Free the memory allocated by the system
        Some(password)
    }
}
