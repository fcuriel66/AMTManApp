#import fitz  # PyMuPDF

def extract_pdf_links(file_path):
    doc = fitz.open(file_path)
    link_data = []

    for page in doc:
        # Extract links
        for link in page.get_links():
            if link["kind"] == 3:  # /F links only (3= FILE LINK)
                uri = link["file"]
                rect = fitz.Rect(link["from"])

                # Extract text within link rectangle
                text = page.get_text("text", clip=rect).strip()
                link_data.append({"text": text, "url": uri})

    return link_data

"""
# Use with some file_path = "/Users/fernandocuriel/.../025-MPP1285-TOC.PDF"
links = extract_pdf_links("025-MPP1285_21-TOC.PDF")

# Export results (csv used for testing)
with open("output.csv", "w") as f:
    f.write("Text,URL\n")
    for item in links:
        f.write(f"{item['text']},{item['url']}\n")

print(f"Extracted {len(links)} links to output.csv")
"""
#-----------------
# Extract selected (allowed) links from text
#-----------------

import fitz  # PyMuPDF

def extract_links_by_text(file_path, allowed_texts):
    """
    Extracts only links whose visible TEXT matches an allowed list.

    allowed_texts: list of strings (text to look for inside the link rectangle)
                   Example: ["21-51-03/400", "21-51-03-000-801-A"]

    Returns list of dicts with:
        - "visible_text"  (text shown in PDF)
        - "target_pdf"    (linked PDF path)
        - "page"          (page number)
    """

    allowed_texts = [a.lower() for a in allowed_texts]  # normalize

    doc = fitz.open(file_path)
    results = []

    for page_number, page in enumerate(doc, start=1):

        for link in page.get_links():

            if link.get("kind") == 3 and "file" in link:  # /F link
                rect = fitz.Rect(link["from"])

                # extract the text shown to the user
                visible = page.get_text("text", clip=rect).strip()
                visible_lc = visible.lower()

                # check if any allowed text is inside the visible text
                if any(a in visible_lc for a in allowed_texts):
                    results.append({
                        "visible_text": visible,
                        "target_pdf": link["file"]
                    })
                    # results.append({
                    #     "page": page_number,
                    #     "visible_text": visible,
                    #     "target_pdf": link["file"]
                    # })
    pdf_links = []
    for r in results:
        pdf_links.append(r["target_pdf"].split("#")[0])

    #return results
    return pdf_links


task_numbers = ["21-51-03/400", "21-51-03-000-801-A"]


matches = extract_links_by_text("../PDF/025-MPP1285_21-TOC.PDF", task_numbers)

for m in matches:
    print(m)

print(matches)
