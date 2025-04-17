use dilly_defender::QuarantineManager;
use eframe::egui;
use std::path::PathBuf;
struct DillyDefenderApp {
    qm: QuarantineManager,
    files: Vec<PathBuf>,
}
impl eframe::App for DillyDefenderApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Dilly Defender - Quarantine");
            if ui.button("Refresh").clicked() {
                self.files = self.qm.list_quarantined_files();
            }
            for file in &self.files {
                ui.horizontal(|ui| {
                    ui.label(file.display().to_string());
                    if ui.button("Restore").clicked() {
                        let _ = self.qm.restore_file(file, &PathBuf::from("C:/Restored/"));
                    }
                });
            }
        });
    }
}

fn main() -> eframe::Result<()> {
    let qm = QuarantineManager::new(
        "C:/ProgramData/DillyDefender/Quarantine",
        "supersecurepassword".to_string(),
    );
    let files = qm.list_quarantined_files();
    let app = DillyDefenderApp { qm, files };
    let options = eframe::NativeOptions::default();
    
    eframe::run_native(
        "Dilly Defender Quarantine",
        options,
        Box::new(|_cc| Ok(Box::new(app))),
    )
}
