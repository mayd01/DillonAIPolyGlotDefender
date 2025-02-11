use lopdf::{Document, Object};
use std::fs;
use std::error::Error;
use log::{debug, error, info, warn};

fn sanitize_pdf(input_path: &str, output_path: &str) -> Result<(), Box<dyn Error>> {
    let mut doc = Document::load(input_path)?;

    info!("Sanitizing PDF: {}", input_path);
    
    // Remove the "Info" entry from the trailer if it exists
    if let Some(trailer) = doc.trailer.as_dict_mut() {
        trailer.remove(b"Info");
    }

    // Remove annotations from the pages
    for (_, page) in doc.get_pages() {
        if let Ok(contents) = doc.get_object_mut(page) {
            if let Object::Dictionary(ref mut dict) = contents {
                dict.remove(b"Annots");
            }
        }
    }

    // Save the sanitized PDF
    doc.save(output_path)?;
    println!("Sanitized PDF saved as {}", output_path);

    Ok(())
}

fn sanitize_pdf_for_polyglot(pdf_path: &str, output_path: &str) -> Result<(), Box<dyn Error>> {
    let mut doc = Document::load(pdf_path)?;

    // Remove metadata info from trailer
    if let Some(trailer) = doc.trailer.as_dict_mut() {
        trailer.remove(b"Info");
    }

    // Iterate over all objects to remove JavaScript if it exists
    for (_, obj) in doc.objects.iter_mut() {
        if let Object::Dictionary(ref mut dict) = obj {
            if dict.contains_key(b"JavaScript") {
                dict.remove(b"JavaScript");
            }
        }
    }

    // Remove annotations from the pages
    for (_, page) in doc.get_pages() {
        if let Ok(contents) = doc.get_object_mut(page) {
            if let Object::Dictionary(ref mut dict) = contents {
                dict.remove(b"Annots");
            }
        }
    }

    // Clear embedded files
    if let Some(files) = doc.trailer.get_mut(b"EmbeddedFiles") {
        if let Ok(dict) = files.as_dict_mut() {
            dict.clear();
        }
    }

    // Save the sanitized PDF
    doc.save(output_path)?;
    println!("Sanitized PDF saved to {}", output_path);

    Ok(())
}

fn view_pdf_metadata(pdf_path: &str) -> Result<(), Box<dyn Error>> {
    let doc = Document::load(pdf_path)?;

    if let Some(info_obj) = doc.trailer.get(b"Info") {
        if let Ok(info_dict) = info_obj.as_dict() {
            println!("PDF Metadata:");
            for (key, value) in info_dict.iter() {
                println!(
                    "{}: {}",
                    String::from_utf8_lossy(key),
                    value.to_string()
                );
            }
        } else {
            println!("The 'Info' entry is not a dictionary.");
        }
    } else {
        println!("No metadata found.");
    }

    Ok(())
}
