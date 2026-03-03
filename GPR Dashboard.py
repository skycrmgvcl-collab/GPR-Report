import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.markdown("## ⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ → Release Stage Tracking")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Filters")

show_shift = st.sidebar.checkbox("Connection Shifting (Non Cons)")
show_pmsy = st.sidebar.checkbox("PMSY RTS")
show_rooftop = st.sidebar.checkbox("LT Rooftop")

# =====================================================
# BASE COLUMNS
# =====================================================

base_columns = [
    "Name Of Subdivision","SR Number","SR Type","Name Of Applicant",
    "Address1","Address2","District","Taluka","Village Or City",
    "Consumer Category","Sub Category","Name Of Scheme",
    "Demand Load","Load Uom","Tariff","RC Date","RC MR NO",
    "RC Charge","SR Status","Rev Land Syrvey No"
]

extra_columns = [
    "Survey Category",
    "Date Of Survey",
    "Date Of Est Appr Launch",
    "Date Of Est Appr Recv",
    "Ts Amount",
    "Ts No",
    "Date Of FQ Issued"
]

# =====================================================
# PRINT FUNCTION (TAB 1)
# =====================================================

def create_print_html(row):

    import base64

    # ===== Convert logo to base64 =====
    with open("mgvcl_logo.png", "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode()

    html = f"""
<html>
<head>
<meta charset="UTF-8">
<style>

@page {{
    size: A4;
    margin: 20mm;
}}

body {{
    font-family: 'Noto Sans Gujarati','Shruti',sans-serif;
    font-size: 13px;
}}

.header {{
    text-align:center;
    font-weight:bold;
    font-size:18px;
}}

.subheader {{
    text-align:center;
    font-size:15px;
}}

.title {{
    text-align:center;
    font-size:20px;
    font-weight:bold;
    margin-top:10px;
    margin-bottom:10px;
    text-decoration: underline;
}}

table {{
    width:100%;
    border-collapse:collapse;
}}

td {{
    border:1px solid black;
    padding:6px;
}}

.logo {{
    position:absolute;
    top:20px;
    left:20px;
    width:80px;
}}

.sketch {{
    height:150px;
}}

</style>
</head>

<body onload="window.print()">

<img src="data:image/png;base64,{logo_base64}" class="logo">

<div class="header">
મધ્ય ગુજરાત વીજ કંપની લી.
</div>

<div class="subheader">
(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર
</div>

<div class="title">Survey Form</div>

<table>
<tr>
<td>તારીખ :- __________________</td>
<td style="text-align:right;">ND SCHEMES &nbsp;&nbsp; 2026</td>
</tr>
</table>

<br>

<table>
<tr>
<td width="5%">૧</td>
<td width="30%">અરજદારનું નામ</td>
<td>{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td>૨</td>
<td>અરજદારનું સરનામું</td>
<td>
{row.get("Address1","")} {row.get("Address2","")} ,
{row.get("District","")} ,
{row.get("Taluka","")} ,
{row.get("Village Or City","")}
</td>
</tr>

<tr>
<td>૩</td>
<td>ફોન નંબર</td>
<td>{row.get("Address2","")} &nbsp;&nbsp;&nbsp;
<b>SR No:</b> {row.get("SR Number","")}
</td>
</tr>

<tr>
<td>૪</td>
<td>વપરાશનો હેતુ</td>
<td>
{row.get("Consumer Category","")} |
{row.get("SR Type","")} |
{row.get("Demand Load","")} {row.get("Load Uom","")}
</td>
</tr>

<tr>
<td>૫</td>
<td>રજીસ્ટ્રેશન ચાર્જ તથા પાવતી નંબર</td>
<td>
{row.get("RC Charge","")} |
{row.get("RC MR NO","")} |
તારીખ : {row.get("RC Date","")}
</td>
</tr>
</table>

<br>

<b>સર્વેની વિગતો :</b>

<table>
<tr>
<td>૬</td>
<td>બાજુવાળાનો ગ્રાહક નંબર</td>
<td colspan="2"></td>
</tr>

<tr>
<td>૭-૧</td>
<td>ફીડરનું નામ</td>
<td></td>
<td>ફીડર કેટેગરી</td>
</tr>

<tr>
<td>૭-૨</td>
<td>ટ્રાન્સફરનું નામ</td>
<td></td>
<td>DTR કપેસિટી</td>
</tr>

<tr>
<td>૭-૩</td>
<td>એલ ટી પોલ નંબર</td>
<td></td>
<td>જીઓ સર્વે (હા/ના)</td>
</tr>

<tr>
<td>૭-૪</td>
<td colspan="3">મકાન ઉપરથી કે નજીકથી એચ.ટી/એલ.ટી લાઇન પસાર થાય છે કે કેમ?</td>
</tr>

<tr>
<td>૮</td>
<td>મકાન કેટલા માળનું છે?</td>
<td></td>
<td>કાચું / પાકું</td>
</tr>

<tr>
<td>૯</td>
<td colspan="3">મકાનની ઊંચાઈ ૧૫ મીટર કરતાં વધારે છે કે કેમ?</td>
</tr>

<tr>
<td>૧૦</td>
<td colspan="3">અન્ય વિજ જોડાણ હોય તો વિગત</td>
</tr>

<tr>
<td>૧૨</td>
<td colspan="3">ગામતળ માં છે કે સિમતલ માં?</td>
</tr>

<tr>
<td>૧૩</td>
<td>સર્વે કેટેગરી (A/B/C/D)</td>
<td></td>
<td>પોલ થી અંતર</td>
</tr>

<tr>
<td>૧૪</td>
<td colspan="3" class="sketch"></td>
</tr>
</table>

<br>

<b>Exist. Cons. No. (For LE):</b>
{row.get("Consumer No","")}

<br><br><br>

Signature : _______________________

</body>
</html>
"""

    return base64.b64encode(html.encode("utf-8")).decode()
# =====================================================
# FILE UPLOAD
# =====================================================

file = st.file_uploader("Upload Excel/CSV", type=["xlsx","xls","csv"])

if file:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file, engine="openpyxl")
    else:
        df = pd.read_excel(file, engine="xlrd")

    # Clean columns
    df["SR Type"]=df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"]=df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"]=df["Survey Category"].astype(str).str.strip()
    df["SR Status"]=df["SR Status"].astype(str).str.strip()

    # Date conversion
    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col]=pd.to_datetime(df[col],errors="coerce")

    # Scheme filter
    scheme_list = sorted(df["Name Of Scheme"].dropna().unique())
    scheme_filter = st.sidebar.selectbox("Name Of Scheme", ["All"] + list(scheme_list))

    # Remove excluded types
    df=df[df["SR Type"].str.lower()!="change of name"]
    df=df[df["Name Of Scheme"].str.lower()!="spa schemes"]

    selected_types=[]
    if show_shift: selected_types.append("Connection Shifting(Non Cons)")
    if show_pmsy: selected_types.append("PMSY RTS")
    if show_rooftop: selected_types.append("LT Rooftop")

    if selected_types:
        df=df[df["SR Type"].isin(selected_types)]
    else:
        df=df[~df["SR Type"].isin(["Connection Shifting(Non Cons)","PMSY RTS","LT Rooftop"])]

    if scheme_filter!="All":
        df=df[df["Name Of Scheme"]==scheme_filter]

    today = pd.Timestamp.today()

    # =====================================================
    # STAGE FILTERS
    # =====================================================

    df1=df[
        (
            df["Survey Category"].isna()
            |(df["Survey Category"]=="")
            |(df["Survey Category"].str.lower()=="nan")
        )
        &(df["SR Status"].str.upper()=="OPEN")
    ].copy()
    df1["Aging Days"]=(today - df1["RC Date"]).dt.days

    df2=df[
        (df["Survey Category"].isin(["A","B","C","D"]))
        &(df["Date Of Est Appr Launch"].isna())
        &(df["SR Status"].str.upper()=="OPEN")
    ].copy()
    df2["Aging Days"]=(today - df2["Date Of Survey"]).dt.days

    df3=df[
        (df["Survey Category"].isin(["A","B","C","D"]))
        &(df["Date Of Est Appr Launch"].notna())
        &(df["Date Of FQ Issued"].isna())
        &(df["SR Status"].str.upper()=="OPEN")
    ].copy()
    df3["Aging Days"]=(today - df3["Date Of Est Appr Launch"]).dt.days

    # =====================================================
    # SUMMARY METRICS
    # =====================================================

    col1,col2,col3 = st.columns(3)
    col1.metric("📝 Survey Pending",len(df1))
    col2.metric("📐 Estimate Pending",len(df2))
    col3.metric("💰 FQ Issue Pending",len(df3))

    total_open = len(df1)+len(df2)+len(df3)
    all_df = pd.concat([df1,df2,df3])
    over30 = len(all_df[all_df["Aging Days"]>30])
    oldest = all_df["Aging Days"].max() if not all_df.empty else 0

    col4,col5,col6 = st.columns(3)
    col4.metric("Total OPEN SR", total_open)
    col5.metric(">30 Days Cases", over30)
    col6.metric("Oldest Case (Days)", int(oldest) if pd.notna(oldest) else 0)

    # =====================================================
    # TABS
    # =====================================================

    tab1,tab2,tab3 = st.tabs(["Unsurvey Applications","Estimate Pending","FQ Issue Pending"])

    with tab1:
        df1=df1[base_columns + ["Aging Days"]]
        df1.insert(0,"Sr. No.",range(1,len(df1)+1))
        display_grid(df1, print_enable=True)

    with tab2:
        df2=df2[base_columns + extra_columns + ["Aging Days"]]
        df2.insert(0,"Sr. No.",range(1,len(df2)+1))
        display_grid(df2)

    with tab3:
        df3=df3[base_columns + extra_columns + ["Workflow Type","Aging Days"]]
        df3.insert(0,"Sr. No.",range(1,len(df3)+1))
        display_grid(df3)

else:
    st.info("Upload file to begin")
