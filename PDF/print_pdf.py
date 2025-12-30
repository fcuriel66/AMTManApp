import os
import platform
import shutil
import subprocess


def print_pdf(path_to_pdf, printer_name=None):
    """
    Send a PDF file to a printer.

    - On Windows, by default prints to the system default printer.
      If printer_name is given, pywin32 is required.
    - On macOS/Linux, uses 'lp' (or 'lpr' fallback) and supports specifying -d/-P.

    Raises:
        FileNotFoundError: if the PDF file does not exist.
        RuntimeError: on unsupported OS or printing errors.
    """
    if not os.path.isfile(path_to_pdf):
        raise FileNotFoundError(f"No such file: {path_to_pdf}")

    system = platform.system()

    if system == "Windows":
        if printer_name:
            # requires: pip install pywin32
            import win32print, win32api
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                # start a raw print job
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("PDF Print", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)
                with open(path_to_pdf, "rb") as f:
                    data = f.read()
                    win32print.WritePrinter(hPrinter, data)
                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        else:
            # default printer
            # note: this will return immediately; the print dialog may not appear
            os.startfile(path_to_pdf, "print")

    elif system in ("Darwin", "Linux"):
        # choose lp (macOS) or fallback to lpr
        cmd = ["lp"] if shutil.which("lp") else ["lpr"]
        # printer flags differ: -d for lp, -P for lpr
        if printer_name:
            if cmd[0] == "lp":
                cmd += ["-d", printer_name]
            else:
                cmd += ["-P", printer_name]
        cmd.append(path_to_pdf)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Printing failed: {e}") from e

    else:
        raise RuntimeError(f"Unsupported OS: {system}")

# Example usage:
# print_pdf("C:/path/to/file.pdf")
# print_pdf("/Users/alice/Documents/report.pdf", printer_name="MyOfficePrinter")