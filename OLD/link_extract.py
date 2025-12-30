import fitz  # PyMuPDF

pdf_path = "Last/100-MPP1285-INTRODUCTION.PDF"
doc = fitz.open(pdf_path)
print(doc)

links = []

for page_num, page in enumerate(doc, start=1):
    for link in page.get_links():
        if "file" in link:
            links.append((page_num, link["file"]))

doc.close()
#print(links)
for page, file in links:
    print(f"Page {page}: {file}")
##########

# from pypdf import PdfReader
#
# reader = PdfReader("100-MPP1285-INTRODUCTION.PDF")
#
# for page_num, page in enumerate(reader.pages, start=1):
#     if "/Annots" in page:
#         for annot in page["/Annots"]:
#             annot_obj = annot.get_object()
#             if "/A" in annot_obj and "/URI" in annot_obj["/A"]:
#                 print(f"Page {page_num}: {annot_obj['/A']['/URI']}")

