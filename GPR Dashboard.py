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

    half = len(base_columns)//2
    left = base_columns[:half]
    right = base_columns[half:]

    def make_rows(cols):
        html=""
        for c in cols:
            html += f"<tr><td><b>{c}</b></td><td>{row[c]}</td></tr>"
        return html

    html=f"""
<html>
<head>
<style>
body {{font-family:Arial;padding:20px;}}
.grid {{display:grid;grid-template-columns:1fr 1fr;gap:10px;}}
table {{width:100%;border-collapse:collapse;}}
td {{border:1px solid black;padding:4px;font-size:11px;}}
.sketch {{height:350px;border:1px solid black;margin-top:10px;}}
</style>
</head>
<body onload="window.print()">
<h3 style="text-align:center;">Electricity Connection Survey Form</h3>
<div class="grid">
<table>{make_rows(left)}</table>
<table>{make_rows(right)}</table>
</div>
<br>
<div class="sketch"></div>
<br>
Signature: __________________
</body>
</html>
"""
    return base64.b64encode(html.encode()).decode()

# =====================================================
# AGGRID DISPLAY FUNCTION (NO COLOR CODING)
# =====================================================

def display_grid(df, print_enable=False):

    if print_enable:
        df["print_data"]=df.apply(create_print_html,axis=1)
        df.insert(1,"Print","")

    cell_renderer = JsCode("""
    class Renderer {
        init(params) {
            this.eGui = document.createElement('span');
            this.eGui.innerHTML = '🖨';
            this.eGui.style.cursor = 'pointer';
            this.eGui.style.fontSize = '18px';
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
        minWidth=130
    )

    if print_enable:
        gb.configure_column("Print", cellRenderer=cell_renderer, width=70, flex=0, pinned="left")
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
