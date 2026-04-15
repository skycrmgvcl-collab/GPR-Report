import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")

# -----------------------------------------------------------
# IMPROVED PRINT HTML (Better Font Support)
# -----------------------------------------------------------

def create_print_html(row_dict):
    # Convert row to dictionary to handle data safely
    r = row_dict
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;700&display=swap" rel="stylesheet">
    <style>
        @page {{ size:A4; margin:5mm; }}
        body {{ 
            font-family: 'Noto Sans Gujarati', sans-serif; 
            font-size: 14px; 
            margin: 0; padding: 20px;
            line-height: 1.6;
        }}
        .header {{ text-align:center; font-size:22px; font-weight:bold; color: #000; }}
        .subheader {{ text-align:center; font-size:16px; margin-bottom: 5px; }}
        .title {{ text-align:center; font-size:18px; font-weight:bold; text-decoration: underline; margin-bottom: 20px; }}
        
        table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
        td {{ border:1px solid black; padding:8px; vertical-align: top; }}
        .label {{ width: 30%; font-weight: bold; }}
        .sketch {{ height:300px; border:1px solid black; margin-top: 10px; position: relative; }}
        .sketch::after {{ content: 'S K E T C H / N A K S H O'; position: absolute; top: 45%; left: 35%; color: #ddd; font-size: 20px; }}
        .srno {{ font-weight:bold; font-size:18px; color: red; }}
        
        /* Ensure font renders before print */
        @media print {{
            body {{ visibility: visible; }}
        }}
    </style>
</head>
<body>
    <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
    <div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
    <div class="title">સર્વે ફોર્મ (Survey Form)</div>

    <table>
        <tr>
            <td colspan="2">તારીખ :- __________</td>
            <td colspan="2" style="text-align:right">વર્ષ: 2026</td>
        </tr>
        <tr>
            <td class="label">૧. અરજદારનું નામ</td>
            <td colspan="3">{r.get("Name Of Applicant","")}</td>
        </tr>
        <tr>
            <td class="label">૨. અરજદારનું સરનામું</td>
            <td colspan="3">
                {r.get("Address1","")} {r.get("Address2","")}, 
                {r.get("Village Or City","")}, {r.get("Taluka","")}, {r.get("District","")}
            </td>
        </tr>
        <tr>
            <td class="label">૩. ફોન નંબર / SR No</td>
            <td>{r.get("Mobile Number","")}</td>
            <td colspan="2" class="srno">SR No : {r.get("SR Number","")}</td>
        </tr>
        <tr>
            <td class="label">૪. વિગત</td>
            <td colspan="3">
                હેતુ: {r.get("Consumer Category","")} | 
                Type: {r.get("SR Type","")} | 
                Load: {r.get("Demand Load","")} {r.get("Load Uom","")}
            </td>
        </tr>
        <tr>
            <td class="label">૫. રજીસ્ટ્રેશન વિગત</td>
            <td colspan="3">ચાર્જ: {r.get("RC Charge","")} | MR NO: {r.get("RC MR NO","")}</td>
        </tr>
        <tr><td colspan="4" style="background-color:#f2f2f2; font-weight:bold; text-align:center;">સર્વે વિગતો (Office Use)</td></tr>
        <tr><td>૬. બાજુવાળો ગ્રાહક નં.</td><td colspan="3"></td></tr>
        <tr><td>૭. ફીડર / ટ્રાન્સફોર્મર</td><td colspan="3"></td></tr>
        <tr><td>૮. નકશો (Sketch)</td><td colspan="3"><div class="sketch"></div></td></tr>
    </table>

    <script>
        // Critical: Wait for fonts to load then print
        document.fonts.ready.then(function () {{
            window.print();
        }});
    </script>
</body>
</html>
"""
    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID COMPONENT WITH ROW-LEVEL PRINT
# -----------------------------------------------------------

def display_grid_with_print(df, key):
    if df.empty:
        st.info("No records found.")
        return

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)
    
    # Enable row selection
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    
    grid_options = gb.build()
    
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        height=400,
        width='100%',
        key=key,
        theme="streamlit",
        update_mode="selection_changed"
    )

    # Print logic based on selection
    selected_rows = grid_response['selected_rows']
    
    if selected_rows:
        # Compatibility check for different AgGrid versions
        selected_data = selected_rows[0] if isinstance(selected_rows, list) else selected_rows
        
        st.success(f"Selected SR: {selected_data.get('SR Number')}")
        
        if st.button(f"🖨️ Print Form for {selected_data.get('SR Number')}", key=f"btn_{key}"):
            html_b64 = create_print_html(selected_data)
            components_html = f"""
                <script>
                var w = window.open();
                w.document.write(atob("{html_b64}"));
                w.document.close();
                </script>
            """
            st.components.v1.html(components_html, height=0)

# -----------------------------------------------------------
# DATA PROCESSING
# -----------------------------------------------------------

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    if file.name.endswith("csv"):
        df = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df = pd.read_excel(file)

    # Standard Cleaning
    df.columns = df.columns.str.strip()
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip().replace(['NULL', 'null', 'nan', 'NaN', 'None'], "")

    df["SR Status"] = df["SR Status"].str.upper()
    df = df[df["SR Status"] != "CLOSED"]

    # Tabs
    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    # Filtering Logic (as per your rules)
    df_survey = df[(df["Survey Category"] == "") & (df["SR Status"] == "OPEN")].copy()
    df_est = df[(df["Survey Category"].isin(["A","B","C","D"])) & (df["Date Of Est Appr Launch"] == "")].copy()
    
    with t1:
        st.subheader("Select a row and click the Print button below")
        display_grid_with_print(df_survey, "g1")
        
    with t2:
        display_grid_with_print(df_est, "g2")
    
    with t3:
        st.write("FQ Logic goes here...")

else:
    st.info("Please upload a file to begin.")
