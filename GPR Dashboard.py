import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import base64

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ Tracking")

# -----------------------------------------------------------
# SURVEY FORM HTML GENERATOR
# -----------------------------------------------------------

def create_print_html(row):
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati&display=swap" rel="stylesheet">
    <style>
        @page {{ size:A4; margin:2mm; }}
        body {{ font-family:'Noto Sans Gujarati','Nirmala UI','Shruti',sans-serif; font-size:13px; margin:0; }}
        .header {{ text-align:center; font-size:20px; font-weight:bold; }}
        .subheader {{ text-align:center; font-size:14px; }}
        .title {{ text-align:center; font-size:16px; font-weight:bold; text-decoration: underline; }}
        table {{ width:100%; border-collapse:collapse; }}
        td {{ border:1px solid black; padding:4px; }}
        .sketch {{ height:340px; border:1px solid black; }}
        .srno {{ font-weight:bold; font-size:17px; }}
    </style>
</head>
<body onload="window.print()">
    <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
    <div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
    <div class="title">Survey Form</div>
    <table>
        <tr>
            <td colspan="2">તારીખ :- __________</td>
            <td colspan="2" style="text-align:right">2026</td>
        </tr>
        <tr>
            <td>1</td><td>અરજદારનું નામ</td>
            <td colspan="2">{row.get("Name Of Applicant","")}</td>
        </tr>
        <tr>
            <td>2</td><td>અરજદારનું સરનામું</td>
            <td colspan="2">
                {row.get("Address1","")} {row.get("Address2","")},
                {row.get("Village Or City","")}, {row.get("Taluka","")}, {row.get("District","")}
            </td>
        </tr>
        <tr>
            <td>3</td><td>ફોન નંબર</td>
            <td>{row.get("Address2","")}</td>
            <td class="srno">SR No : {row.get("SR Number","")}</td>
        </tr>
        <tr>
            <td>4</td><td>વપરાશનો હેતુ</td>
            <td colspan="2">
                {row.get("Consumer Category","")} | {row.get("SR Type","")} | 
                {row.get("Demand Load","")} {row.get("Load Uom","")}
            </td>
        </tr>
        <tr>
            <td>5</td><td>રજીસ્ટ્રેશન ચાર્જ</td>
            <td colspan="2">{row.get("RC Charge","")} | {row.get("RC MR NO","")}</td>
        </tr>
        <tr><td colspan="4"><b>સર્વે વિગતો</b></td></tr>
        <tr><td>6</td><td>બાજુવાળો ગ્રાહક નંબર</td><td colspan="2"></td></tr>
        <tr><td>7</td><td colspan="3">ફીડર / ટ્રાન્સફોર્મર / પોલ વિગત</td></tr>
        <tr><td>8</td><td colspan="3">મકાન વિગત</td></tr>
        <tr><td>9</td><td colspan="3">ઊંચાઈ 15 મીટરથી વધુ?</td></tr>
        <tr><td>14</td><td colspan="3">નકશો<div class="sketch"></div></td></tr>
        <tr><td></td><td colspan="3">Exist. Cons. No : {row.get("Consumer No","")}</td></tr>
    </table>
</body>
</html>
"""
    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID DISPLAY FUNCTION
# -----------------------------------------------------------

def display_grid(df, print_enable=False, key="grid"):
    if df.empty:
        st.warning("No records found for this stage.")
        return

    # Clean display: Ensure no 'nan' strings appear in the UI
    display_df = df.copy()
    
    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    
    AgGrid(display_df, gridOptions=gb.build(), height=400, key=key, theme="streamlit")

    if print_enable:
        st.write("---")
        idx = st.number_input("Enter row number (Sr No) to print", 1, len(display_df), 1, key=f"num_{key}")
        if st.button("🖨️ Generate Survey Form", key=f"btn_{key}"):
            html_data = create_print_html(display_df.iloc[idx-1])
            st.components.v1.html(f"""
                <script>
                var w=window.open();
                w.document.write(atob("{html_data}"));
                w.document.close();
                </script>
            """, height=0)

# -----------------------------------------------------------
# MAIN APPLICATION LOGIC
# -----------------------------------------------------------

file = st.file_uploader("Upload Excel/CSV", type=["xls","xlsx","csv"])

if file:
    # Load data
    if file.name.endswith("csv"):
        df = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df = pd.read_excel(file)

    # 1. Clean Column Names
    df.columns = df.columns.str.strip()

    # 2. GLOBAL CLEANING: Handle "NULL", "nan", and Whitespace
    for col in df.columns:
        # Convert everything to string for cleaning
        df[col] = df[col].astype(str).str.strip()
        # Replace common 'null' indicators with actual empty strings
        df[col] = df[col].replace(['NULL', 'null', 'nan', 'NaN', 'None', 'NAT'], "")

    # 3. Status Normalization
    df["SR Status"] = df["SR Status"].str.upper()
    df = df[df["SR Status"] != "CLOSED"] # Exclude Closed

    # 4. Sidebar Filters
    st.sidebar.header("Filters")
    
    schemes = sorted([x for x in df["Name Of Scheme"].unique() if x != ""])
    selected_scheme = st.sidebar.multiselect("Scheme", schemes, default=schemes)
    
    sr_types = sorted([x for x in df["SR Type"].unique() if x != ""])
    selected_sr = st.sidebar.multiselect("SR Type", sr_types, default=sr_types)

    # Apply filters
    df_filtered = df[df["Name Of Scheme"].isin(selected_scheme) & df["SR Type"].isin(selected_sr)]

    search = st.sidebar.text_input("Search SR Number")
    if search:
        df_filtered = df_filtered[df_filtered["SR Number"].str.contains(search, case=False)]

    # 5. Date Conversion (for Aging)
    for col in ["RC Date", "Date Of Survey", "Date Of Est Appr Launch", "Date Of FQ Issued"]:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")

    today = pd.Timestamp.today()

    # -----------------------------------------------------------
    # STAGE LOGIC
    # -----------------------------------------------------------

    # STAGE 1: Survey Pending (Category is empty OR NULL)
    df1 = df_filtered[
        (df_filtered["Survey Category"] == "") & 
        (df_filtered["SR Status"] == "OPEN")
    ].copy()
    if not df1.empty:
        df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    # STAGE 2: Estimate Pending (Survey done, but Est Appr Launch is empty)
    df2 = df_filtered[
        (df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) &
        (df_filtered["Date Of Est Appr Launch"].isna()) &
        (df_filtered["SR Status"] == "OPEN")
    ].copy()
    if not df2.empty:
        df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    # STAGE 3: FQ Pending (Est Appr Launch done, but FQ Issued is empty)
    df3 = df_filtered[
        (df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) &
        (df_filtered["Date Of Est Appr Launch"].notna()) &
        (df_filtered["Date Of FQ Issued"].isna()) &
        (df_filtered["SR Status"] == "OPEN")
    ].copy()
    if not df3.empty:
        df3["Aging Days"] = (today - df3["Date Of Est Appr Launch"]).dt.days

    # -----------------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Survey Pending", len(df1))
    col2.metric("Estimate Pending", len(df2))
    col3.metric("FQ Pending", len(df3))
    col4.metric("Total Active SR", len(df_filtered))

    t1, t2, t3 = st.tabs(["📋 Survey Pending", "📐 Estimate Pending", "💰 FQ Pending"])

    with t1:
        if not df1.empty:
            df1.insert(0, "Sr No", range(1, len(df1) + 1))
            display_grid(df1, print_enable=True, key="g1")
        else:
            st.info("No records pending survey.")

    with t2:
        if not df2.empty:
            df2.insert(0, "Sr No", range(1, len(df2) + 1))
            display_grid(df2, print_enable=False, key="g2")
        else:
            st.info("No records pending estimate.")

    with t3:
        if not df3.empty:
            df3.insert(0, "Sr No", range(1, len(df3) + 1))
            display_grid(df3, print_enable=False, key="g3")
        else:
            st.info("No records pending FQ.")

else:
    st.info("Please upload the SR Status Excel or CSV file to start.")
