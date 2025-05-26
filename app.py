import fitz  # PyMuPDF
import re
import pandas as pd
from difflib import get_close_matches

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_tests(text):
    pattern = re.compile(r"(\d{1,2}\.\d{1,2}|\d{1,2}\.0)\s+(.*?)\s{2,}(.*)")
    tests = []
    for match in pattern.finditer(text):
        test_number, test_name, spec = match.groups()
        tests.append({"Test Name": test_name.strip(), "Spec": spec.strip()})
    return tests

def extract_results(text):
    pattern = re.compile(r"(\d{1,2}\.\d{1,2}|\d{1,2}\.0)\s+(.*?)\s{2,}(.*)")
    results = []
    for match in pattern.finditer(text):
        test_number, test_name, result = match.groups()
        results.append({"Test Name": test_name.strip(), "Result": result.strip()})
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
            df.at[i, "Status"] = "✅ Match" if row["Spec"] in result["Result"] or result["Result"] in row["Spec"] else "❌ Deviation"
        else:
            df.at[i, "Result"] = "Not Found"
            df.at[i, "Status"] = "❌ Missing"

    return df

def main():
    spec_pdf = "fp_spec.pdf"  # Replace with your actual filename
    coa_pdf = "coa.pdf"       # Replace with your actual filename

    spec_text = extract_text_from_pdf(spec_pdf)
    coa_text = extract_text_from_pdf(coa_pdf)

    spec_data = extract_tests(spec_text)
    coa_data = extract_results(coa_text)

    result_df = compare_spec_coa(spec_data, coa_data)

    print("\n📋 Comparison Table:\n")
    print(result_df.to_string(index=False))

    result_df.to_excel("comparison_result.xlsx", index=False)
    print("\n✅ Saved as 'comparison_result.xlsx'")

if __name__ == "__main__":
    main()

