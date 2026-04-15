import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import base64
import io

# --- Page Configuration ---
st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ Tracking")

# -----------------------------------------------------------
# SURVEY FORM HTML GENERATOR
# -----------------------------------------------------------
def get_print_html(row):
    """Generates the HTML for the survey form based on a single row."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{ size:A4; margin:5mm; }}
    body {{ font-family:'Nirmala UI','Arial',sans-serif; font-size:13px; line-height:1.4; }}
    .header {{ text-align:center; font-size:20px; font-weight:bold; }}
    .title {{ text-align:center; font-size:16px; font-weight:bold; text-decoration: underline; margin-top:10px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    td {{ border:1px solid black; padding:6px; vertical-align:top; }}
    .label {{ width:30%; font-weight:bold; background-color: #f2f2f2; }}
    .sketch {{ height:300px; border:1px solid black; margin-top:5px; }}
</style>
</head>
<body>
    <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
    <div style="text-align:center;">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
    <div class="title">Survey Form</div>
    
    <table>
        <tr><td>SR No: <b>{row.get("SR Number","")}</b></td><td style="text-align:right">Date: ___________</td></tr>
        <tr><td class="label">Applicant Name</td><td>{row.get("Name Of Applicant","")}</td></tr>
        <tr><td class="label">Address</td><td>{row.get("Address1","")}, {row.get("Village Or City","")}, {row.get("Taluka","")}</td></tr>
        <tr><td class="label">Category / Load</td><td>{row.get("Consumer Category","")} | {row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>
        <tr><td class="label">RC Details</td><td>Charge: {row.get("RC Charge","")} | MR No: {row.get("RC MR NO","")}</td></tr>
    </table>

    <div style="margin-top:15px;"><b>Survey Details / Sketch:</b></div>
    <div class="sketch"></div>

    <table style="margin-top:20px; border:none;">
        <tr style="border:none;">
            <td style="border:none; text-align:center;"><br><br>Applicant Signature</td>
            <td style="border:none; text-align:center;"><br><br>Surveyor Name/Sign</td>
            <td style="border:none; text-align:center;"><br><br>Jr. Engineer Sign</td>
        </tr>
    </table>
    <script>window.print();</script>
</body>
</html>
"""
    return html

# -----------------------------------------------------------
# GRID DISPLAY FUNCTION
# -----------------------------------------------------------
def display_grid(df, grid_key):
    """Renders AgGrid with row selection enabled."""
    df = df.copy().fillna("")
    
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection('single', use_checkbox=True) # Enable selection
    gb.configure_default_column(filter=True, sortable=True, resizable=True, flex=1, minWidth=120)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
    
    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        key=grid_key,
        height=400,
        fit_columns_on_grid_load=True
    )
    return grid_response

# -----------------------------------------------------------
# MAIN APP LOGIC
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel / CSV", type=["xls", "xlsx", "csv"])

if file:
    # 1. Load Data
    df_raw = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)
    df_raw.columns = df_raw.columns.str.strip()
    df_filtered = df_raw[df_raw["SR Status"].str.upper() != "CLOSED"].copy()

    # 2. Filtering Logic
    for col in ["RC Date", "Date Of Survey", "Date Of Est Appr Launch", "Date Of FQ Issued"]:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")

    today = pd.Timestamp.today()

    # Split DataFrames
    df1 = df_filtered[(df_filtered["Survey Category"].isna() | (df_filtered["Survey Category"] == ""))].copy()
    df2 = df_filtered[(df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) & (df_filtered["Date Of Est Appr Launch"].isna())].copy()
    df3 = df_filtered[(df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) & (df_filtered["Date Of Est Appr Launch"].notna()) & (df_filtered["Date Of FQ Issued"].isna())].copy()

    # 3. Layout: Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    # Sidebar Print Action
    st.sidebar.header("Actions")
    
    with tab1:
        st.subheader(f"Pending Surveys ({len(df1)})")
        if not df1.empty:
            res1 = display_grid(df1, "grid1")
            selected_row = res1['selected_rows']
            
            if selected_row is not None and len(selected_row) > 0:
                # Use a specific row from the selection
                row_data = selected_row.iloc[0] if isinstance(selected_row, pd.DataFrame) else selected_row[0]
                if st.sidebar.button("🖨️ Print Selected Survey Form"):
                    html_content = get_print_html(row_data)
                    b64 = base64.b64encode(html_content.encode()).decode()
                    href = f'<a href="data:text/html;base64,{b64}" download="Survey_{row_data["SR Number"]}.html" style="text-decoration:none;"><button style="width:100%; cursor:pointer;">Click here to Open/Print Form</button></a>'
                    st.sidebar.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No records found.")

    with tab2:
        st.subheader(f"Pending Estimates ({len(df2)})")
        if not df2.empty:
            display_grid(df2, "grid2")
        else:
            st.info("No records found.")

    with tab3:
        st.subheader(f"Pending FQ ({len(df3)})")
        if not df3.empty:
            display_grid(df3, "grid3")
        else:
            st.info("No records found.")

else:
    st.info("Please upload a file to begin.")
