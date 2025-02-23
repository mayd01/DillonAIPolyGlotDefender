import pikepdf

# Open an existing PDF
pdf = pikepdf.Pdf.open("../Resume+mayd+3_23.pdf")

# Add custom metadata (often hidden in the document)
pdf.docinfo["/CustomMetadata"] = "Sensitive data"
pdf.docinfo["/Author"] = "Hidden Author"
pdf.docinfo["/Company"] = "Fake Corp"

# Add JavaScript action to execute on opening the PDF
pdf.Root.AA = pikepdf.Dictionary(O=pikepdf.Array(["JavaScript code"]))

# Add a hidden text layer (potential steganography attempt)
hidden_text_page = pdf.pages[0]  # Assuming we modify the first page
hidden_text_page.Annots = [
    pikepdf.Dictionary(
        Subtype=pikepdf.Name("/Text"),
        Contents="This is hidden text that won't be visible but is embedded in the PDF",
        Rect=[0, 0, 1, 1],  # Very small invisible annotation
    )
]

# Embed a file (potential security risk)
embedded_file = pikepdf.Stream(pdf, b"This is a hidden embedded file")
pdf.Root.Names = pikepdf.Dictionary(
    EmbeddedFiles=pikepdf.Dictionary(
        Names=["hidden.txt", embedded_file]
    )
)

# Add an embedded URL (phishing simulation)
pdf.Root.OpenAction = pikepdf.Array([
    pikepdf.Name("/URI"),
    pikepdf.Dictionary(
        URI="https://malicious-site.example.com"
    )
])

# Save the modified PDF
pdf.save("infected_output.pdf")
