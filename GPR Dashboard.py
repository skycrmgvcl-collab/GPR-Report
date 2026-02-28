import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from st_aggrid import AgGrid, GridOptionsBuilder
import base64

st.set_page_config(page_title="SR Stage Dashboard", layout="wide")

st.title("⚡ SR Stage Monitoring Dashboard")

# =====================================================
# SIDEBAR FILTERS
# =====================================================

st.sidebar.header("Include SR Types")

show_shift = st.sidebar.checkbox("Connection Shifting (Non Cons)", value=False)
show_pmsy = st.sidebar.checkbox("PMSY RTS", value=False)
show_rooftop = st.sidebar.checkbox("LT Rooftop", value=False)

# =====================================================
# REQUIRED COLUMNS
# =====================================================

unsurvey_columns = [
    "Name Of Subdivision",
    "SR Number",
    "SR Type",
    "Name Of Applicant",
    "Address1",
    "Address2",
    "District",
    "Taluka",
    "Village Or City",
    "Consumer Category",
    "Sub Category",
    "Name Of Scheme",
    "Demand Load",
    "Load Uom",
    "Tariff",
    "RC Date",
    "RC MR NO",
    "RC Charge",
    "SR Status",
    "Rev Land Syrvey No"
]

# =====================================================
# WORD FORM
# =====================================================

def generate_word_form(row):

    doc = Document()

    title = doc.add_heading("Electricity Connection Survey Form", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"

    for col in unsurvey_columns:
        r = table.add_row().cells
        r[0].text = col
        r[1].text = str(row[col])

    doc.add_paragraph("\nSurvey Category: __________________")
    doc.add_paragraph("Feeder Name: __________________")
    doc.add_paragraph("Date of Survey: __________________")

    doc.add_paragraph("\nSite Sketch:")
    doc.add_paragraph("\n" * 4)

    doc.add_paragraph("\nSignature: __________________")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer

# =====================================================
# PRINT HTML GENERATOR
# =====================================================

def create_print_link(row):

    half = len(unsurvey_columns)//2

    left = unsurvey_columns[:half]
    right = unsurvey_columns[half:]

    def rows(cols):
        html=""
        for c in cols:
            html+=f"<tr><td class='l'>{c}</td><td class='v'>{row[c]}</td></tr>"
        return html

    html=f"""
<html>
<head>
<style>

body {{
font-family: Arial;
padding:20px;
}}

.grid {{
display:grid;
grid-template-columns:1fr 1fr;
gap:10px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
border:1px solid black;
padding:4px;
font-size:11px;
}}

.l {{
font-weight:bold;
width:40%;
}}

.sketch {{
height:350px;
border:1px solid black;
margin-top:10px;
}}

</style>
</head>

<body onload="window.print()">

<h3 style="text-align:center;">Electricity Connection Survey Form</h3>

<div class="grid">

<table>
{rows(left)}
</table>

<table>
{rows(right)}
</table>

</div>

<br>

<table>
<tr><td class="l">Survey Category</td><td></td></tr>
<tr><td class="l">Feeder Name</td><td></td></tr>
<tr><td class="l">Date of Survey</td><td></td></tr>
</table>

<div class="sketch"></div>

<br>
Signature: __________________

</body>
</html>
"""

    b64=base64.b64encode(html.encode()).decode()

    return f'<a href="data:text/html;base64,{b64}" target="_blank">🖨</a>'

# =====================================================
# FILE UPLOAD
# =====================================================

file=st.file_uploader("Upload Excel/CSV",type=["xlsx","xls","csv"])

if file:

    if file.name.endswith(".csv"):
        df=pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df=pd.read_excel(file,engine="openpyxl")
    else:
        df=pd.read_excel(file,engine="xlrd")

    df["SR Type"]=df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"]=df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"]=df["Survey Category"].astype(str).str.strip()
    df["SR Status"]=df["SR Status"].astype(str).str.strip()

    # always remove
    df=df[df["SR Type"].str.lower()!="change of name"]
    df=df[df["Name Of Scheme"].str.lower()!="spa schemes"]

    # sidebar filters
    if not show_shift:
        df=df[df["SR Type"]!="Connection Shifting(Non Cons)"]

    if not show_pmsy:
        df=df[df["SR Type"]!="PMSY RTS"]

    if not show_rooftop:
        df=df[df["SR Type"]!="LT Rooftop"]

    df=df[
        (
        df["Survey Category"].isna()
        |(df["Survey Category"]=="")
        |(df["Survey Category"].str.lower()=="nan")
        )
        &
        (df["SR Status"].str.upper()=="OPEN")
    ]

    df=df[unsurvey_columns]

    df.insert(0,"Sr. No.",range(1,len(df)+1))

    # print icon column
    df.insert(1,"Print","")

    df["Print"]=df.apply(lambda x:create_print_link(x),axis=1)

    st.metric("Total Unsurvey OPEN",len(df))

    gb=GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        flex=1
    )

    gb.configure_column("Print",width=70)

    gridOptions=gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=500
    )

    st.write("Click 🖨 icon in row to print")

else:
    st.info("Upload file to begin")
