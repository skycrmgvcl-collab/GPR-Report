import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import base64
import io

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ Tracking")

# -----------------------------------------------------------
# SURVEY FORM (Gujarati + A4)
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

body {{
font-family: 'Noto Sans Gujarati','Nirmala UI','Shruti',sans-serif;
font-size:13px;
margin:0;
}}

.header {{ text-align:center; font-size:20px; font-weight:bold; }}
.subheader {{ text-align:center; font-size:14px; margin-bottom:5px; }}
.title {{ text-align:center; font-size:16px; font-weight:bold; margin-bottom:6px; text-decoration: underline; }}

table {{ width:100%; border-collapse:collapse; }}

td {{
border:1px solid black;
padding:4px;
vertical-align:top;
}}

.sketch {{
height:340px;
border:1px solid black;
margin-top:4px;
}}

.signature td {{
text-align:center;
height:70px;
}}

.srno {{
font-weight:bold;
font-size:17px;
}}
</style>
</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
<div class="title">Survey Form</div>

<table>

<tr>
<td colspan="2">તારીખ :- _______________________</td>
<td colspan="2" style="text-align:right">GP No. ______ 2026</td>
</tr>

<tr>
<td width="5%">1</td>
<td>અરજદારનું નામ</td>
<td colspan="2">{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td>2</td>
<td>અરજદારનું સરનામું</td>
<td colspan="2">
{row.get("Address1","")} {row.get("Address2","")},
{row.get("Village Or City","")},
{row.get("Taluka","")},
{row.get("District","")}
</td>
</tr>

<tr>
<td>3</td>
<td>ફોન નંબર</td>
<td>{row.get("Address2","")}</td>
<td class="srno">SR No : {row.get("SR Number","")}</td>
</tr>

<tr>
<td>4</td>
<td>વપરાશનો હેતુ</td>
<td colspan="2">
{row.get("Consumer Category","")} |
{row.get("SR Type","")} |
{row.get("Demand Load","")} {row.get("Load Uom","")}
</td>
</tr>

<tr>
<td>5</td>
<td>રજીસ્ટ્રેશન ચાર્જ</td>
<td colspan="2">
{row.get("RC Charge","")} |
{row.get("RC MR NO","")} |
તારીખ : {row.get("RC Date","")}
</td>
</tr>

<tr><td colspan="4"><b>સર્વેની વિગતો</b></td></tr>

<tr><td>6</td><td>બાજુવાળાનો ગ્રાહક નંબર</td><td colspan="2"></td></tr>

<tr><td rowspan="4">7</td><td>ફીડર</td><td></td><td>કેટેગરી</td></tr>
<tr><td>ટ્રાન્સફોર્મર</td><td></td><td>કેપેસીટી</td></tr>
<tr><td>એલ ટી પોલ</td><td></td><td>જીઓ સર્વે</td></tr>
<tr><td colspan="3">HT/LT લાઇન પસાર થાય છે ?</td></tr>

<tr><td>8</td><td>મકાન માળ</td><td></td><td>કાચું/પાકું</td></tr>
<tr><td>9</td><td colspan="3">ઊંચાઈ 15 મીટરથી વધુ?</td></tr>
<tr><td>10</td><td colspan="3">અન્ય જોડાણ વિગત</td></tr>
<tr><td>12</td><td colspan="3">ગામતળ/સિમતળ</td></tr>

<tr><td>13</td><td>સર્વે કેટેગરી</td><td></td><td>પોલ અંતર</td></tr>

<tr>
<td>14</td>
<td colspan="3">
નકશો
<div class="sketch"></div>
</td>
</tr>

<tr>
<td></td>
<td colspan="3">Exist. Cons. No : {row.get("Consumer No","")}</td>
</tr>

</table>

<br>

<table class="signature">
<tr>
<td>અરજદાર સહી</td>
<td>સર્વે કરનાર</td>
<td>જુ.ઇ.</td>
</tr>
</table>

</body>
</html>
"""
    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID FUNCTION (SAFE)
# -----------------------------------------------------------

def display_grid(df, print_enable=False, grid_key="grid"):

    df = df.copy().fillna("").reset_index(drop=True)

    # Convert all columns to string
    for col in df.columns:
        df[col] = df[col].astype(str)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True)

    AgGrid(
        df,
        gridOptions=gb.build(),
        height=500,
        fit_columns_on_grid_load=True,
        key=grid_key
    )

    # Print Section
    if print_enable:

        st.markdown("### 🖨 Print Survey Form")

        if len(df) == 0:
            st.warning("No records available to print")
            return

        idx = st.number_input(
            "Enter Sr No",
            min_value=1,
            max_value=len(df),
            value=1,
            step=1,
            key=f"num_{grid_key}"
        )

        if st.button("Print Selected", key=f"btn_{grid_key}"):

            row = df.iloc[idx-1]
            html = create_print_html(row)

            js = f"""
            <script>
            var win = window.open("", "_blank");
            var html = atob("{html}");
            win.document.write(html);
            win.document.close();
            </script>
            """

            st.components.v1.html(js, height=0)

# -----------------------------------------------------------
# FILE UPLOAD
# -----------------------------------------------------------

file = st.file_uploader("Upload Excel / CSV", type=["xls","xlsx","csv"])

if file:

    if file.name.endswith("csv"):
        df = pd.read_csv(file, encoding="utf-8-sig")
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()
    df = df.fillna("")

    df = df[df["SR Status"].str.upper() != "CLOSED"]

    st.sidebar.header("Filters")

    schemes = sorted(df["Name Of Scheme"].dropna().unique())
    selected_scheme = st.sidebar.multiselect("Scheme", schemes, default=schemes)
    df = df[df["Name Of Scheme"].isin(selected_scheme)]

    sr_types = sorted(df["SR Type"].dropna().unique())
    selected_sr = st.sidebar.multiselect("SR Type", sr_types, default=sr_types)
    df = df[df["SR Type"].isin(selected_sr)]

    search = st.text_input("Search SR Number")

    if search:
        df = df[df["SR Number"].astype(str).str.contains(search, case=False)]

    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    today = pd.Timestamp.today()

    df1 = df[(df["Survey Category"].isna()) & (df["SR Status"]=="OPEN")].copy()
    df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    df2 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].isna()) &
             (df["SR Status"]=="OPEN")].copy()
    df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    df3 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].notna()) &
             (df["Date Of FQ Issued"].isna()) &
             (df["SR Status"]=="OPEN")].copy()
    df3["Aging Days"] = (today - df3["Date Of Est Appr Launch"]).dt.days

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Survey Pending", len(df1))
    col2.metric("Estimate Pending", len(df2))
    col3.metric("FQ Pending", len(df3))
    col4.metric("Total SR", len(df1)+len(df2)+len(df3))

    tab1, tab2, tab3 = st.tabs(["Survey","Estimate","FQ"])

    with tab1:
        df1.insert(0,"Sr No",range(1,len(df1)+1))
        display_grid(df1, True, "grid1")

    with tab2:
        df2.insert(0,"Sr No",range(1,len(df2)+1))
        display_grid(df2, False, "grid2")

    with tab3:
        df3.insert(0,"Sr No",range(1,len(df3)+1))
        display_grid(df3, False, "grid3")

else:
    st.info("Upload file to begin")
