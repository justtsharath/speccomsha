import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd
from difflib import get_close_matches

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_tests(text):
    # Adjust pattern if needed based on your PDFs
    pattern = re.compile(r"(\d{1,2}\.\d{1,2}|\d{1,2}\.0)?\s*([\w\s\-/()]+?)\s{2,}(.*)")
    tests = []
    for match in pattern.finditer(text):
        # Ignore empty or invalid rows
        test_name = match.group(2).strip()
        spec = match.group(3).strip()
        if test_name and spec:
            tests.append({"Test Name": test_name, "Spec": spec})
    return tests

def extract_results(text):
    # Similar pattern for results
    pattern = re.compile(r"(\d{1,2}\.\d{1,2}|\d{1,2}\.0)?\s*([\w\s\-/()]+?)\s{2,}(.*)")
    results = []
    for match in pattern.finditer(text):
        test_name = match.group(2).strip()
        result = match.group(3).strip()
        if test_name and result:
            results.append({"Test Name": test_name, "Result": result})
    return results

def compare_spec_coa(spec_tests, coa_results):
    df = pd.DataFrame(spec_tests)
    df["Result"] = ""
    df["Status"] = ""

    for i, row in df.iterrows():
        match = get_close_matches(row["Test Name"], [r["Test Name"] for r in coa_results], n=1, cutoff=0.8)
        if match:
            result = next((r for r in coa_results if r["Test Name"] == match[0]), None)
            df.at[i, "Result"] = result["Result"]
            # Basic string containment check, can improve with numeric comparison
            if row["Spec"] in result["Result"] or result["Result"] in row["Spec"]:
                df.at[i, "Status"] = "✅ Match"
            else:
                df.at[i, "Status"] = "❌ Deviation"
        else:
            df.at[i, "Result"] = "Not Found"
            df.at[i, "Status"] = "❌ Missing"

    return df

# Streamlit UI
st.title("Spec vs CoA PDF Comparison Tool")

spec_pdf = st.file_uploader("Upload Finished Product Specification PDF", type="pdf")
coa_pdf = st.file_uploader("Upload Certificate of Analysis (CoA) PDF", type="pdf")

if spec_pdf and coa_pdf:
    with st.spinner("Extracting and comparing..."):
        spec_text = extract_text_from_pdf(spec_pdf)
        coa_text = extract_text_from_pdf(coa_pdf)

        spec_data = extract_tests(spec_text)
        coa_data = extract_results(coa_text)

        if not spec_data or not coa_data:
            st.error("Couldn't extract test data properly. Try with different PDFs or formatting.")
        else:
            comparison_df = compare_spec_coa(spec_data, coa_data)

            st.dataframe(comparison_df)

            # Download button for Excel file
            towrite = pd.ExcelWriter("comparison_result.xlsx", engine='openpyxl')
            comparison_df.to_excel(towrite, index=False, sheet_name='Comparison')
            towrite.save()

            with open("comparison_result.xlsx", "rb") as f:
                st.download_button("Download Comparison Excel", data=f, file_name="comparison_result.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")



