import pandas as pd
import re
import uuid

def extract_data_from_pdf(path):
    text = open(path, 'r', encoding='utf-8', errors='ignore').read()
    lines = text.splitlines()
    data = []
    for i, line in enumerate(lines):
        if re.match(r'\d+\.\d+ .*', line):
            spec = lines[i+1] if i+1 < len(lines) else ''
            data.append((line.split()[1], spec))
    return dict(data)

def compare_spec_coa(spec_path, coa_path):
    spec_data = extract_data_from_pdf(spec_path)
    coa_data = extract_data_from_pdf(coa_path)

    result_rows = []
    for test, spec in spec_data.items():
        coa_result = coa_data.get(test, "Not Found")
        status = "Match"
        if coa_result == "Not Found":
            status = "Missing"
        elif spec not in coa_result:
            status = "Deviation or OOS"
        result_rows.append({
            "Test Name": test,
            "Spec Limit": spec,
            "Result": coa_result,
            "Status": status
        })

    df = pd.DataFrame(result_rows)
    file_id = str(uuid.uuid4())
    excel_path = f"uploads/{file_id}.xlsx"
    df.to_excel(excel_path, index=False)
    return result_rows, excel_path
