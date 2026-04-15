import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import io

# --- Page Configuration ---
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
<style>
@page {{ size:A4; margin:2mm; }}
body {{ font-family:'Nirmala UI','Shruti',sans-serif; font-size:13px; margin:0; }}
.header {{ text-align:center; font-size:20px; font-weight:bold; }}
.subheader {{ text-align:center; font-size:14px; margin-bottom:5px; }}
.title {{ text-align:center; font-size:16px; font-weight:bold; margin-bottom:6px; text-decoration: underline; }}
table {{ width:100%; border-collapse:collapse; }}
td {{ border:1px solid black; padding:4px; vertical-align:top; }}
.label {{ width:28%; font-weight:bold; }}
.value {{ width:72%; }}
.sketch {{ height:340px; border:1px solid black; margin-top:4px; }}
.signature td {{ text-align:center; height:70px; }}
.srno {{ font-weight:bold; font-size:17px; }}
</style>
</head>
<body onload="window.print()">
<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
<div class="title">Survey Form</div>
<table>
<tr>
<td colspan="2">તારીખ :- _______________________</td>
<td colspan="2" style="text-align:right">GP No. ______ &nbsp;&nbsp; 2026</td>
</tr>
<tr>
<td width="5%">1</td>
<td class="label">અરજદારનું નામ</td>
<td colspan="2" class="value">{row.get("Name Of Applicant","")}</td>
</tr>
<tr>
<td>2</td>
<td class="label">અરજદારનું સરનામું</td>
<td colspan="2" class="value">
{row.get("Address1","")} {row.get("Address2","")} ,
{row.get("Village Or City","")} ,
{row.get("Taluka","")} ,
{row.get("District","")}
</td>
</tr>
<tr>
<td>3</td>
<td class="label">ફોન નંબર</td>
<td>{row.get("Address2","")}</td>
<td class="srno">SR No : {row.get("SR Number","")}</td>
</tr>
<tr>
<td>4</td>
<td class="label">વપરાશનો હેતુ</td>
<td colspan="2">
{row.get("Consumer Category","")} | {row.get("SR Type","")} | {row.get("Demand Load","")} {row.get("Load Uom","")}
</td>
</tr>
<tr>
<td>5</td>
<td class="label">રજીસ્ટ્રેશન ચાર્જ તથા પાવતી નંબર</td>
<td colspan="2">
{row.get("RC Charge","")} | {row.get("RC MR NO","")} | તારીખ : {row.get("RC Date","")}
</td>
</tr>
<tr><td colspan="4"><b>સર્વેની વિગતો</b></td></tr>
<tr><td>6</td><td class="label">બાજુવાળાનો ગ્રાહક નંબર</td><td colspan="2"></td></tr>
<tr><td rowspan="4">7</td><td>1. ફીડરનું નામ</td><td></td><td>ફીડર કેટેગરી</td></tr>
<tr><td>2. ટ્રાન્સફોર્મરનું નામ</td><td></td><td>ટ્રાન્સફોર્મર કેપેસીટી</td></tr>
<tr><td>3. એલ ટી પોલ નંબર</td><td></td><td>જીઓ સર્વે (હા/ના)</td></tr>
<tr><td colspan="3">4. મકાન ઉપરથી કે નજીકથી HT/LT લાઇન પસાર થાય છે ?</td></tr>
<tr><td>8</td><td>મકાન કેટલા માળનું છે</td><td></td><td>કાચું / પાકું</td></tr>
<tr><td>9</td><td colspan="3">મકાનની ઊંચાઈ ૧૫ મીટર કરતાં વધારે છે ?</td></tr>
<tr><td>10</td><td colspan="3">અન્ય વિજ જોડાણ હોય તો વિગત</td></tr>
<tr><td>12</td><td colspan="3">ગામતળ / સિમતળ</td></tr>
<tr><td>13</td><td>સર્વે કેટેગરી (A/B/C/D) </td><td></td><td>પોલ થી અંતર (A કેટેગરી હોય)</td></tr>
<tr><td>14</td><td colspan="3">નકશો તથા અન્ય વિગતો<div class="sketch"></div></td></tr>
<tr><td></td><td colspan="3">Exist. Cons. No. : {row.get("Consumer No","")}</td></tr>
</table>
<br>
<table class="signature">
<tr><td>અરજદાર / પ્રતિનિધિની સહી</td><td>સર્વે કરનારનું નામ / સહી</td><td>જુ.ઇ. ની સહી</td></tr>
</table>
</body>
</html>
"""
    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID DISPLAY FUNCTION
# -----------------------------------------------------------
def display_grid(df, grid_key, print_enable=False):
    df = df.copy().fillna("")

    if print_enable:
        df["print_data"] = df.apply(lambda r: create_print_html(r), axis=1)
        df.insert(1, "Print", "")

    renderer = JsCode("""
    class Renderer{
        init(params){
            this.eGui=document.createElement('span');
            this.eGui.innerHTML='🖨';
            this.eGui.style.cursor='pointer';
            this.eGui.addEventListener('click',()=>{
                const win=window.open("","_blank");
                const b64=params.data.print_data;
                const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));
                const html=new TextDecoder("utf-8").decode(bytes);
                win.document.open();
                win.document.write(html);
                win.document.close();
            });
        }
        getGui(){return this.eGui;}
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True, flex=1, minWidth=120)

    if print_enable:
        gb.configure_column("Print", cellRenderer=renderer, width=70)
        gb.configure_column("print_data", hide=True)

    AgGrid(
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=min(650, 150 + len(df) * 30),
        key=grid_key
    )

# -----------------------------------------------------------
# MAIN APP LOGIC
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel / CSV", type=["xls", "xlsx", "csv"])

if file:
    # 1. Load Data
    if file.name.endswith("csv"):
        df_raw = pd.read_csv(file)
    else:
        df_raw = pd.read_excel(file)

    # 2. Basic Cleaning
    df_raw.columns = df_raw.columns.str.strip()
    df_filtered = df_raw[df_raw["SR Status"].str.upper() != "CLOSED"].copy()

    # 3. Sidebar Filters
    st.sidebar.header("Filters")
    schemes = sorted(df_filtered["Name Of Scheme"].dropna().unique())
    selected_scheme = st.sidebar.multiselect("Select Scheme", schemes, default=schemes)
    df_filtered = df_filtered[df_filtered["Name Of Scheme"].isin(selected_scheme)]

    sr_types = sorted(df_filtered["SR Type"].dropna().unique())
    selected_sr = st.sidebar.multiselect("Select SR Type", sr_types, default=sr_types)
    df_filtered = df_filtered[df_filtered["SR Type"].isin(selected_sr)]

    search = st.text_input("Search SR Number")
    if search:
        df_filtered = df_filtered[df_filtered["SR Number"].astype(str).str.contains(search, case=False)]

    # 4. Date Conversion & Logic
    for col in ["RC Date", "Date Of Survey", "Date Of Est Appr Launch", "Date Of FQ Issued"]:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")

    today = pd.Timestamp.today()

    # Define the three status DataFrames
    df1 = df_filtered[(df_filtered["Survey Category"].isna() | (df_filtered["Survey Category"] == "")) & (df_filtered["SR Status"] == "OPEN")].copy()
    if not df1.empty and "RC Date" in df1.columns:
        df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    df2 = df_filtered[(df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) & (df_filtered["Date Of Est Appr Launch"].isna()) & (df_filtered["SR Status"] == "OPEN")].copy()
    if not df2.empty and "Date Of Survey" in df2.columns:
        df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    df3 = df_filtered[(df_filtered["Survey Category"].isin(["A", "B", "C", "D"])) & (df_filtered["Date Of Est Appr Launch"].notna()) & (df_filtered["Date Of FQ Issued"].isna()) & (df_filtered["SR Status"] == "OPEN")].copy()
    if not df3.empty and "Date Of Est Appr Launch" in df3.columns:
        df3["Aging Days"] = (today - df3["Date Of Est Appr Launch"]).dt.days

    # 5. Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Survey Pending", len(df1))
    col2.metric("Estimate Pending", len(df2))
    col3.metric("FQ Pending", len(df3))
    col4.metric("Total SR", len(df1) + len(df2) + len(df3))

    # 6. Tabs and Grids
    tab1, tab2, tab3 = st.tabs(["Survey Pending", "Estimate Pending", "FQ Pending"])

    with tab1:
        if not df1.empty:
            df1.insert(0, "Sr No", range(1, len(df1) + 1))
            buffer = io.BytesIO()
            df1.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export Survey Pending", buffer.getvalue(), "SurveyPending.xlsx", key="dl_1")
            display_grid(df1, grid_key="grid_survey", print_enable=True)
        else:
            st.info("No records found for Survey Pending.")

    with tab2:
        if not df2.empty:
            df2.insert(0, "Sr No", range(1, len(df2) + 1))
            buffer = io.BytesIO()
            df2.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export Estimate Pending", buffer.getvalue(), "EstimatePending.xlsx", key="dl_2")
            display_grid(df2, grid_key="grid_estimate")
        else:
            st.info("No records found for Estimate Pending.")

    with tab3:
        if not df3.empty:
            df3.insert(0, "Sr No", range(1, len(df3) + 1))
            buffer = io.BytesIO()
            df3.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export FQ Pending", buffer.getvalue(), "FQPending.xlsx", key="dl_3")
            display_grid(df3, grid_key="grid_fq")
        else:
            st.info("No records found for FQ Pending.")

else:
    st.info("Please upload a file to view the dashboard.")
