import frappe
import base64
from PyPDF4 import PdfFileMerger
from frappe.utils.file_manager import save_file
from io import BytesIO


def save_and_attach(content, to_doctype, to_name):
    file_name = filename(to_name)
    save_file(file_name, content, to_doctype,
              to_name, is_private=1)


def get_pdf_data(doctype, name):
    html = frappe.get_print(doctype, name)
    return frappe.utils.pdf.get_pdf(html)


def filename(docname):
    return "{}-QRBILL.pdf".format(docname)


def merge_pdf(pdf_list):
    """
    Merge PDF with Integral Frappe Data
    """
    merger = PdfFileMerger()

    for pdf in pdf_list:
        merger.append(pdf)

    output = BytesIO()
    merger.write(output)
    merger.close()

    file_content = output.getvalue()

    return file_content


@frappe.whitelist()
def attach_pdf(**kwargs):
    """
    Attach Pdf
    ----------
    """
    kwargs = frappe._dict(**kwargs)
    print(kwargs)
    doctype = 'Sales Invoice'
    pdf = kwargs['pdf_data']
    docname = kwargs['docname']
    frappe.local.lang = kwargs['doclang']
    pdf_data = pdf.split(',')[1]
    encoded_data = pdf_data.encode('utf-8')

    # PDF's
    bts = base64.decodebytes(encoded_data)
    invoice = get_pdf_data(doctype, docname)

    # Merge
    merged_pdf = merge_pdf([BytesIO(invoice), BytesIO(bts)])

    # Attach
    save_and_attach(merged_pdf, doctype, docname)
