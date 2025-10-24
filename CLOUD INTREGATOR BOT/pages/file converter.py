import streamlit as st
import pandas as pd
import io
from pdf2docx import Converter # type: ignore
from docx2pdf import convert as docx2pdf_convert # type: ignore
import tempfile
import os

def csv_to_xlsx(file_bytes):
    df = pd.read_csv(io.BytesIO(file_bytes))
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def pdf_to_docx(pdf_path, docx_path):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

def docx_to_pdf(docx_path, pdf_path):
    docx2pdf_convert(docx_path, pdf_path)

def main():
    st.title("File Conversion Bot")

    conversion_options = {
        'csv': ['xlsx'],
        'pdf': ['docx'],
        'docx': ['pdf']
    }

    uploaded_file = st.file_uploader("Choose a CSV, PDF or DOCX file", type=['csv','pdf','docx'])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type not in conversion_options:
            st.error(f"Conversion FROM .{file_type} is not supported.")
            return  # inside function

        to_format = st.selectbox("Convert to:", conversion_options[file_type])

        if st.button("Convert"):
            if file_type == 'csv' and to_format == 'xlsx':
                st.info("Converting CSV to Excel...")
                converted_bytes = csv_to_xlsx(uploaded_file.read())
                st.success("Conversion complete!")
                st.download_button("Download XLSX file", data=converted_bytes,
                                   file_name=uploaded_file.name.replace('.csv','.xlsx'),
                                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            elif file_type == 'pdf' and to_format == 'docx':
                st.info("Converting PDF to Word DOCX...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_temp:
                    pdf_temp.write(uploaded_file.read())
                    pdf_temp.flush()
                    docx_temp_path = pdf_temp.name.replace('.pdf','.docx')
                    pdf_to_docx(pdf_temp.name, docx_temp_path)
                with open(docx_temp_path, "rb") as f:
                    docx_bytes = f.read()
                os.unlink(pdf_temp.name)
                os.unlink(docx_temp_path)
                st.success("Conversion complete!")
                st.download_button("Download DOCX file", data=docx_bytes,
                                   file_name=uploaded_file.name.replace('.pdf','.docx'),
                                   mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

            elif file_type == 'docx' and to_format == 'pdf':
                st.info("Converting Word DOCX to PDF...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as docx_temp:
                    docx_temp.write(uploaded_file.read())
                    docx_temp.flush()
                    pdf_temp_path = docx_temp.name.replace('.docx','.pdf')
                    try:
                        docx_to_pdf(docx_temp.name, pdf_temp_path)
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
                        os.unlink(docx_temp.name)
                        return
                with open(pdf_temp_path, "rb") as f:
                    pdf_bytes = f.read()
                os.unlink(docx_temp.name)
                os.unlink(pdf_temp_path)
                st.success("Conversion complete!")
                st.download_button("Download PDF file", data=pdf_bytes,
                                   file_name=uploaded_file.name.replace('.docx','.pdf'),
                                   mime='application/pdf')
            else:
                st.error("This conversion is not implemented")
    else:
        st.info("Please upload a CSV, PDF, or DOCX file to start conversion.")
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")

if __name__ == "__main__":
    main()
