from link_extract import extract_links_by_text, extract_chapter, copy_pdf_list


gradient_text_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700;900&display=swap');

.snowchat-title {
  font-family: 'Poppins', sans-serif;
  font-weight: 900;
  font-size: 4em;
  background: linear-gradient(90deg, #ff6a00, #ee0979);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);
  margin: 0;
  padding: 20px 0;
  text-align: center;
}
</style>
<div class="snowchat-title">AMTMan</div>
"""


def find_pdf_from_task_numbers(task_numbers: list):
    """ Find PDF files from a list of task numbers."""

    # Extraction of chapter number to put in the search path
    tasks_chapter = extract_chapter(task_numbers)

    # Extraction of the links in pdf TOC chapter files associated with the text of tasks in task_num list
    matches = extract_links_by_text(f"PDF/025-MPP1285_{tasks_chapter}-TOC.PDF", task_numbers)

    # Copy selected PDF files from MPP original directory to single working directory (AMM_EXTRACTED)
    result = copy_pdf_list(
        matches,
        destination_dir="/Users/fernandocuriel/PycharmProjects/RAG/PDF/AMM_EXTRACTED/" + f"{tasks_chapter}",
        base_dir="/Users/fernandocuriel/PycharmProjects/RAG/PDF"
    )

    print(f"Copied in ../AMM_EXTRACTED/{tasks_chapter}")
    print()
    for f in result["copied"]:
        print("  ✓", f)

    print("\nMissing:")
    for f in result["missing"]:
        print("  ✗", f)

    return result