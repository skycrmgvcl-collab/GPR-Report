import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import os

# =====================================================
# PAGE CONFIG
# =====================================================

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
# PRINT FUNCTION (AS PER ATTACHED FORMAT)
# =====================================================

def create_print_html(row):

    exist_cons = row.get("Exist. Cons. No. (For LE)", row.get("Consumer No", ""))

    html = f"""
<div style="font-family:'Nirmala UI','Shruti',sans-serif;font-size:14px;">

<div style="text-align:center;font-weight:bold;font-size:18px;">
મધ્ય ગુજરાત વીજ કંપની લી.
</div>

<div style="text-align:center;">
(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર
</div>

<div style="text-align:center;font-size:18px;font-weight:bold;margin:10px 0;text-decoration:underline;">
Survey Form
</div>

<table border="1" style="width:100%;border-collapse:collapse;">
<tr>
<td>તારીખ :</td>
<td></td>
<td style="text-align:right;">{row.get("Name Of Scheme","")}</td>
</tr>
</table>

<br>

<table border="1" style="width:100%;border-collapse:collapse;">

<tr>
<td width="5%">૧</td>
<td width="30%">અરજદારનું નામ</td>
<td>{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td>૨</td>
<td>અરજદારનું સરનામું</td>
<td>
{row.get("Address1","")} {row.get("Address2","")},
{row.get("Village Or City","")},
{row.get("Taluka","")},
{row.get("District","")}
</td>
</tr>

<tr>
<td>૩</td>
<td>ફોન નંબર</td>
<td>{row.get("Address2","")} &nbsp;&nbsp; SR No: {row.get("SR Number","")}</td>
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
{row.get("RC Date","")}
</td>
</tr>

<tr>
<td>૬</td>
<td>બાજુવાળાનો ગ્રાહક નંબર</td>
<td></td>
</tr>

<tr>
<td>૭</td>
<td>સર્વે કેટેગરી</td>
<td>{row.get("Survey Category","")}</td>
</tr>

<tr>
<td>૮</td>
<td>ફીડર / ટ્રાન્સફર / પોલ વિગત</td>
<td></td>
</tr>

<tr>
<td>૯</td>
<td>મકાન વિગત</td>
<td></td>
</tr>

<tr>
<td>૧૦</td>
<td>અન્ય વિજ જોડાણ વિગત</td>
<td></td>
</tr>

<tr>
<td>૧૧</td>
<td>ગામતળ / સિમતલ</td>
<td></td>
</tr>

<tr>
<td>૧૨</td>
<td>Exist. Cons. No. (For LE)</td>
<td>{exist_cons}</td>
</tr>

<tr>
<td>૧૩</td>
<td colspan="2" style="height:150px;"></td>
</tr>

</table>

<br><br>
Signature : _______________________

</div>
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
            this.eGui.style.fontSize = '18px';

            this.eGui.addEventListener('click', () => {

                const win = window.open("", "_blank");
                win.document.open("text/html","replace");
                win.document.write("<!DOCTYPE html><html><head><meta charset='UTF-8'></head><body>" + atob(params.data.print_data) + "</body></html>");
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
# SIDEBAR FILTERS (RESTORED)
# =====================================================

st.sidebar.header("Filters")

file = st.file_uploader("Upload Excel/CSV", type=["xlsx","xls","csv"])

if file:

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    # Scheme Filter Restored
    scheme_list = sorted(df["Name Of Scheme"].dropna().unique())
    scheme_filter = st.sidebar.selectbox("Name Of Scheme", ["All"] + scheme_list)

    if scheme_filter != "All":
        df = df[df["Name Of Scheme"] == scheme_filter]

    # Date conversion
    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["SR Status"] = df["SR Status"].astype(str)

    today = pd.Timestamp.today()

    # Stage 1
    df1 = df[(df["Survey Category"].isna()) &
             (df["SR Status"].str.upper()=="OPEN")].copy()
    df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    # Stage 2
    df2 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].isna()) &
             (df["SR Status"].str.upper()=="OPEN")].copy()
    df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    # Stage 3
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
