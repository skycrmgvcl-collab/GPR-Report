import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
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
# PRINT LINK GENERATOR
# =====================================================

def create_print_html(row):

    half = len(unsurvey_columns)//2
    left = unsurvey_columns[:half]
    right = unsurvey_columns[half:]

    def rows(cols):
        html=""
        for c in cols:
            html+=f"<tr><td><b>{c}</b></td><td>{row[c]}</td></tr>"
        return html

    html=f"""
<html>
<head>
<style>
body{{font-family:Arial;padding:20px;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;}}
table{{width:100%;border-collapse:collapse;}}
td{{border:1px solid black;padding:4px;font-size:11px;}}
.sketch{{height:350px;border:1px solid black;margin-top:10px;}}
</style>
</head>

<body onload="window.print()">

<h3 style="text-align:center;">Electricity Connection Survey Form</h3>

<div class="grid">
<table>{rows(left)}</table>
<table>{rows(right)}</table>
</div>

<br>

<table>
<tr><td><b>Survey Category</b></td><td></td></tr>
<tr><td><b>Feeder Name</b></td><td></td></tr>
<tr><td><b>Date of Survey</b></td><td></td></tr>
</table>

<div class="sketch"></div>

<br>
Signature: __________________

</body>
</html>
"""

    return base64.b64encode(html.encode()).decode()

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

    df["SR Type"] = df["SR Type"].astype(str).str.strip()
    df["Name Of Scheme"] = df["Name Of Scheme"].astype(str).str.strip()
    df["Survey Category"] = df["Survey Category"].astype(str).str.strip()
    df["SR Status"] = df["SR Status"].astype(str).str.strip()

    df = df[df["SR Type"].str.lower() != "change of name"]
    df = df[df["Name Of Scheme"].str.lower() != "spa schemes"]

    if not show_shift:
        df = df[df["SR Type"] != "Connection Shifting(Non Cons)"]

    if not show_pmsy:
        df = df[df["SR Type"] != "PMSY RTS"]

    if not show_rooftop:
        df = df[df["SR Type"] != "LT Rooftop"]

    df = df[
        (
            df["Survey Category"].isna()
            | (df["Survey Category"] == "")
            | (df["Survey Category"].str.lower() == "nan")
        )
        &
        (df["SR Status"].str.upper() == "OPEN")
    ]

    df = df[unsurvey_columns]

    df.insert(0, "Sr. No.", range(1, len(df)+1))

    # create base64 print data
    df["print_data"] = df.apply(create_print_html, axis=1)

    # visible icon column
    df.insert(1, "Print", "🖨")

    st.metric("Total Unsurvey OPEN", len(df))

    # =====================================================
    # AGGRID ICON RENDERER
    # =====================================================

    cell_renderer = JsCode("""
    class PrintIconRenderer {
        init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerHTML = '🖨';
            this.eGui.style.cursor = 'pointer';
            this.eGui.style.fontSize = '18px';

            const data = params.data.print_data;

            this.eGui.addEventListener('click', () => {
                const win = window.open("");
                win.document.write(atob(data));
                win.document.close();
            });
        }

        getGui() {
            return this.eGui;
        }
    }
    """)

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_column(
        "Print",
        cellRenderer=cell_renderer,
        width=70
    )

    gb.configure_column("print_data", hide=True)

    gb.configure_default_column(filter=True, sortable=True, flex=1)

    gridOptions = gb.build()

    AgGrid(
        df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=500
    )

    st.write("Click 🖨 icon to print")

else:
    st.info("Upload file to begin")
