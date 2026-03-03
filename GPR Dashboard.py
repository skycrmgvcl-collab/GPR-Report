import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import os

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.markdown("## ⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ → Release Stage Tracking")

# =====================================================
# SAFE LOGO LOAD
# =====================================================

LOGO_BASE64 = ""
if os.path.exists("mgvcl_logo.png"):
    with open("mgvcl_logo.png", "rb") as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

show_shift = st.sidebar.checkbox("Connection Shifting (Non Cons)")
show_pmsy = st.sidebar.checkbox("PMSY RTS")
show_rooftop = st.sidebar.checkbox("LT Rooftop")

# =====================================================
# PRINT FUNCTION (Official Format)
# =====================================================

def create_print_html(row):

    exist_cons = row.get("Exist. Cons. No. (For LE)", row.get("Consumer No", ""))

    html = f"""
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600&display=swap" rel="stylesheet">

<style>
@page {{ size: A4; margin: 20mm; }}
body {{ font-family: 'Noto Sans Gujarati', sans-serif; font-size: 13px; }}
.header {{ text-align:center; font-weight:bold; font-size:18px; }}
.subheader {{ text-align:center; }}
.title {{ text-align:center; font-size:20px; font-weight:bold; text-decoration: underline; margin:10px 0; }}
table {{ width:100%; border-collapse:collapse; }}
td {{ border:1px solid black; padding:6px; vertical-align:top; }}
.logo {{ position:absolute; top:20px; left:20px; width:80px; }}
.sketch {{ height:150px; }}
</style>
</head>

<body onload="window.print()">

{"<img src='data:image/png;base64," + LOGO_BASE64 + "' class='logo'>" if LOGO_BASE64 else ""}

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>
<div class="title">Survey Form</div>

<table>
<tr>
<td>તારીખ :- __________________</td>
<td style="text-align:right;">ND SCHEMES &nbsp;&nbsp; 2026</td>
</tr>
</table>

<br>

<table>
<tr><td width="5%">૧</td><td width="30%">અરજદારનું નામ</td><td>{row.get("Name Of Applicant","")}</td></tr>
<tr><td>૨</td><td>અરજદારનું સરનામું</td>
<td>{row.get("Address1","")} {row.get("Address2","")} ,
{row.get("Village Or City","")} ,
{row.get("Taluka","")} ,
{row.get("District","")}</td></tr>

<tr><td>૩</td><td>ફોન નંબર</td>
<td>{row.get("Address2","")} &nbsp;&nbsp; SR No: {row.get("SR Number","")}</td></tr>

<tr><td>૪</td><td>વપરાશનો હેતુ</td>
<td>{row.get("Consumer Category","")} |
{row.get("SR Type","")} |
{row.get("Demand Load","")} {row.get("Load Uom","")}</td></tr>

<tr><td>૫</td><td>રજીસ્ટ્રેશન ચાર્જ તથા પાવતી નંબર</td>
<td>{row.get("RC Charge","")} |
{row.get("RC MR NO","")} |
તારીખ : {row.get("RC Date","")}</td></tr>
</table>

<br><b>સર્વેની વિગતો :</b>

<table>
<tr><td>૬</td><td colspan="2">બાજુવાળાનો ગ્રાહક નંબર</td></tr>
<tr><td>૭-૧</td><td>ફીડરનું નામ</td><td>ફીડર કેટેગરી</td></tr>
<tr><td>૭-૨</td><td>ટ્રાન્સફરનું નામ</td><td>DTR કપેસિટી</td></tr>
<tr><td>૭-૩</td><td>એલ ટી પોલ નંબર</td><td>જીઓ સર્વે (હા/ના)</td></tr>
<tr><td>૭-૪</td><td colspan="2">મકાન ઉપરથી કે નજીકથી એચ.ટી/એલ.ટી લાઇન પસાર થાય છે?</td></tr>
<tr><td>૮</td><td>મકાન કેટલા માળનું છે?</td><td>કાચું / પાકું</td></tr>
<tr><td>૯</td><td colspan="2">મકાનની ઊંચાઈ ૧૫ મીટર કરતાં વધારે છે?</td></tr>
<tr><td>૧૦</td><td colspan="2">અન્ય વિજ જોડાણ વિગત</td></tr>
<tr><td>૧૨</td><td colspan="2">ગામતળ / સિમતલ</td></tr>
<tr><td>૧૩</td><td>સર્વે કેટેગરી (A/B/C/D)</td><td>પોલ થી અંતર</td></tr>
<tr><td>૧૪</td><td colspan="2" class="sketch"></td></tr>
</table>

<br>
<b>Exist. Cons. No. (For LE):</b> {exist_cons}

<br><br><br>
Signature : _______________________

</body>
</html>
"""
    return base64.b64encode(html.encode("utf-8")).decode()

# =====================================================
# GRID FUNCTION
# =====================================================

def display_grid(df, print_enable=False):

    df = df.copy()

    if print_enable:
        df["print_data"] = df.apply(create_print_html, axis=1)
        df.insert(1, "Print", "")

    cell_renderer = JsCode("""
    class Renderer {
        init(params) {
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = '🖨';
            this.eGui.style.cursor = 'pointer';
            this.eGui.addEventListener('click', () => {
                const win = window.open("");
                win.document.write(atob(params.data.print_data));
                win.document.close();
            });
        }
        getGui() { return this.eGui; }
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=120
    )

    if print_enable:
        gb.configure_column("Print", cellRenderer=cell_renderer, width=70, flex=0)
        gb.configure_column("print_data", hide=True)

    AgGrid(
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=500,
        theme="streamlit"
    )

# =====================================================
# FILE UPLOAD + STAGE LOGIC
# =====================================================

file = st.file_uploader("Upload Excel/CSV", type=["xlsx","xls","csv"])

if file:

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["SR Status"] = df["SR Status"].astype(str)

    today = pd.Timestamp.today()

    df1 = df[(df["Survey Category"].isna()) & (df["SR Status"].str.upper()=="OPEN")].copy()
    df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    df2 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].isna()) &
             (df["SR Status"].str.upper()=="OPEN")].copy()
    df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    df3 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].notna()) &
             (df["Date Of FQ Issued"].isna()) &
             (df["SR Status"].str.upper()=="OPEN")].copy()
    df3["Aging Days"] = (today - df3["Date Of Est Appr Launch"]).dt.days

    tab1, tab2, tab3 = st.tabs(["Unsurvey Applications","Estimate Pending","FQ Issue Pending"])

    with tab1:
        df1.insert(0,"Sr No", range(1,len(df1)+1))
        display_grid(df1, print_enable=True)

    with tab2:
        df2.insert(0,"Sr No", range(1,len(df2)+1))
        display_grid(df2)

    with tab3:
        df3.insert(0,"Sr No", range(1,len(df3)+1))
        display_grid(df3)

else:
    st.info("Upload file to begin")
