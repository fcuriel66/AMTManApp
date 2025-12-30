import fitz  # PyMuPDF

#-----------------
# Extract selected (allowed) links from text
#-----------------

def extract_links_by_text(file_path:str, task_numbers:list):
    """
    Extracts only links whose visible TEXT matches an allowed list.

    allowed_texts: list of strings (text to look for inside the link rectangle)
                   Example: ["21-51-03/400", "21-51-03-000-801-A"]

    Returns list of strings with:
      ##  - "visible_text"  (text shown in PDF) ##
        - "target_pdf"    (linked PDF path)
    """

    task_numbers = [a.lower() for a in task_numbers]  # normalize

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
                if any(a in visible_lc for a in task_numbers):
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
        path_pdf_MPP = r["target_pdf"].split("#")[0].split("../")[-1]
        pdf_links.append(path_pdf_MPP)

    #return results
    return pdf_links


def extract_chapter(list_of_tasks:list)->str:
    return list_of_tasks[0].split("-")[0]   # e.g. for '32-00-01/200' it gets '32'

# list of task numbers (extracted by AI Agent?)
#task_num = ["21-51-03/400", "21-51-03-000-801-A", "21-00-00/200", "21-00-00-860-801-A"]
task_num = ["36-12-02-000-801-A", "36-12-02-400-801-A", "36-12-02/600"]
# Extraction of chapter number to put in the search path
tasks_chapter = extract_chapter(task_num)
#print(tasks_chapter)

# Extraction of the links in pdf TOC chapter files associated with the text of tasks in task_num list
matches = extract_links_by_text(f"PDF/025-MPP1285_{tasks_chapter}-TOC.PDF", task_num)

for m in matches:
    print(m)

#print(matches)
# ----------------------
# Copy all PDF's to a single Directory
# -----------------------

import os
import shutil

def copy_pdf_list(pdf_paths, destination_dir, base_dir=None):
    """
    Copies PDF files listed in `pdf_paths` into `destination_dir`.

    Args:
        pdf_paths (list[str]):
            List of file paths, relative or absolute.
            Example: ["../../AMM_PART2_1285/CHAPTER_21/MPP1285_21-00-00-02-1.PDF"]

        destination_dir (str):
            The folder where all PDFs will be copied.

        base_dir (str or None):
            Used to resolve relative paths.
            If None, uses current working directory.

    Returns:
        dict with:
            - "copied": list of copied file paths
            - "missing": list of missing file paths
    """

    if base_dir is None:
        base_dir = os.getcwd()

    # Ensure destination folder exists
    os.makedirs(destination_dir, exist_ok=True)

    copied = []
    missing = []

    for path in pdf_paths:
        # Build absolute path
        abs_path = os.path.abspath(os.path.join(base_dir, path))

        if os.path.isfile(abs_path):
            try:
                shutil.copy(abs_path, destination_dir)
                copied.append(abs_path)
            except Exception as e:
                print(f"ERROR copying {abs_path}: {e}")
                missing.append(abs_path)
        else:
            missing.append(abs_path)

    return {"copied": copied, "missing": missing}

#-------------------
# Usage
#---------------

pdf_list = matches
print(pdf_list)

result = copy_pdf_list(
    pdf_list,
    destination_dir="/PDF/AMM_EXTRACTED",
    base_dir="/PDF"
)

print("Copied:")
for f in result["copied"]:
    print("  ✓", f)

print("\nMissing:")
for f in result["missing"]:
    print("  ✗", f)

