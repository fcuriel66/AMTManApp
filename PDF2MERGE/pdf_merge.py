# pip install PyPDF2
import os
from PyPDF2 import PdfMerger


def merge_pdfs(pdf_paths, output_path):
    """
    Merge a list of PDF files into a single PDF.

    Args:
        pdf_paths (list of str): paths to input PDF files, in the order you want them merged.
        output_path (str): path to write the merged PDF.

    Raises:
        FileNotFoundError: if any input file does not exist.
        ValueError: if pdf_paths is empty.
    """
    if not pdf_paths:
        raise ValueError("No PDF files provided for merging.")

    merger = PdfMerger()
    try:
        for pdf in pdf_paths:
            if not os.path.isfile(pdf):
                raise FileNotFoundError(f"File not found: {pdf}")
            merger.append(pdf)

        # Write out the merged PDF
        with open(output_path, "wb") as fout:
            merger.write(fout)
    finally:
        merger.close()


# Example usage:
if __name__ == "__main__":
    inputs = [
        "100-MPP1285-INTRODUCTION.PDF",
        "025-MPP1285_21-TOC.PDF"
    ]

    output = "full_book.pdf"
    merge_pdfs(inputs, output)
    print(f"Merged {len(inputs)} files into {output}")