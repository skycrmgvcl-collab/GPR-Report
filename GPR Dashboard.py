import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import os

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ → Release Stage Tracking")

# --------------------------------------------------
# Survey Form HTML
# --------------------------------------------------

def create_print_html(row):

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>

@page {{
size:A4;
margin:8mm;
}}

body {{
font-family:'Nirmala UI','Shruti',sans-serif;
font-size:13px;
margin:0;
}}

.header {{
text-align:center;
font-size:18px;
font-weight:bold;
}}

.subheader {{
text-align:center;
margin-bottom:5px;
}}

.title {{
text-align:center;
font-size:16px;
font-weight:bold;
margin-bottom:6px;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
padding:4px;
vertical-align:top;
}}

.line {{
border-bottom:1px solid black;
display:inline-block;
width:100%;
}}

.sketch {{
height:200px;
border:1px solid black;
}}

.signature td {{
text-align:center;
padding-top:30px;
}}

</style>

</head>

<body onload="window.print()">

<div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
<div class="subheader">(ઓ. એન્ડ. એમ.) સબ ડિવિઝન, વિરપુર</div>

<div class="title">Survey Form</div>

<table>

<tr>
<td>તારીખ:- ________________________</td>
<td style="text-align:right">GP No. ______ &nbsp;&nbsp; 2026</td>
</tr>

</table>

<br>

<table>

<tr>
<td width="4%">1</td>
<td width="28%">અરજદારનું નામ :-</td>
<td class="line">{row.get("Name Of Applicant","")}</td>
</tr>

<tr>
<td>2</td>
<td>અરજદારનું સરનામું :-</td>
<td class="line">
{row.get("Address1","")} {row.get("Address2","")},
{row.get("Village Or City","")},
{row.get("Taluka","")},
{row.get("District","")}
</td>
</tr>

<tr>
<td>3</td>
<td>ફોન નંબર :-</td>
<td>
{row.get("Address2","")} &nbsp;&nbsp;&nbsp; SR No. {row.get("SR Number","")}
</td>
</tr>

<tr>
<td>4</td>
<td>વપરાશનો હેતુ :-</td>
<td class="line">
{row.get("Consumer Category","")} |
{row.get("SR Type","")} |
{row.get("Demand Load","")} {row.get("Load Uom","")}
</td>
</tr>

<tr>
<td>5</td>
<td>રજીસ્ટ્રેશન ચાર્જ તથા પાવતી નંબર :-</td>
<td>
{row.get("RC Charge","")} |
{row.get("RC MR NO","")} &nbsp;&nbsp; તારીખ:- {row.get("RC Date","")}
</td>
</tr>

</table>

<br>

<b>સર્વેની વિગતો :-</b>

<table>

<tr>
<td width="4%">6</td>
<td>બાજુવાળાનો ગ્રાહક નંબર :</td>
<td class="line"></td>
</tr>

<tr>
<td>7</td>
<td>
1. ફીડરનું નામ :- <span class="line" style="width:200px"></span>
</td>
<td>
ફીડરનું કેટેગરી :- ______
</td>
</tr>

<tr>
<td></td>
<td>
2. ટ્રાન્સફરનું નામ :- <span class="line" style="width:200px"></span>
</td>
<td>
DTR કપકીટી :- ______
</td>
</tr>

<tr>
<td></td>
<td>
3. એલ ટી પોલ નંબર :- <span class="line" style="width:200px"></span>
</td>
<td>
જીઓ સર્વે (હા/ના)? ______
</td>
</tr>

<tr>
<td></td>
<td colspan="2">
4. મકાન ઉપરથી કે નજીકથી એચ.ટી/એલ.ટી લાઇન પસાર થાય છે કે કેમ ? :-
<span class="line"></span>
</td>
</tr>

<tr>
<td>8</td>
<td>
સદર મકાન કેટલા માળનું છે. :-
<span class="line"></span>
</td>

<td>
વીજ જોડાણ મંગેલ મકાન કાચું છે પાકું? :- ______
</td>
</tr>

<tr>
<td>9</td>
<td colspan="2">
સદર મકાનની ઊંચાઈ ૧૫ મીટર કરતાં વધારે છે કે કેમ ? :-
<span class="line"></span>
</td>
</tr>

<tr>
<td>10</td>
<td colspan="2">
વીજ જોડાણ મંગેલ મકાનમાં અન્ય વિજ જોડાણ હોય તો તેની વિગત (હેતુ સાથે) :-
<span class="line"></span>
</td>
</tr>

<tr>
<td>12</td>
<td colspan="2">
વીજ જોડાણ મંગેલ સ્થળ ગામતળ માં છે કે સિમતલ માં છે? :-
<span class="line"></span>
</td>
</tr>

<tr>
<td>13</td>
<td>
સર્વે કેટેગરી (A/B/C/D) :- <span class="line" style="width:120px"></span>
</td>
<td>
પોલ થી મકાન નું અંતર :- ______
</td>
</tr>

<tr>
<td>14</td>
<td colspan="2">
નકશો તથા અન્ય વિગતો નીચે બતાવી :- <br>
<div class="sketch"></div>
</td>
</tr>

<tr>
<td></td>
<td colspan="2">
Exist. Cons. No. (For LE) :- {row.get("Consumer No","")}
</td>
</tr>

</table>

<br><br>

<table class="signature">

<tr>
<td>અરજદાર / પ્રતિનિધિની સહી.</td>
<td>સર્વે કરનારનું / સહી<br>નામ<br>હોદ્દો</td>
<td>જુ.ઇ. ની સહી</td>
</tr>

</table>

</body>
</html>
"""

    return base64.b64encode(html.encode("utf-8")).decode()
# --------------------------------------------------
# AgGrid Display
# --------------------------------------------------

def display_grid(df, print_enable=False):

    df = df.copy()

    if print_enable:
        df["print_data"] = df.apply(create_print_html, axis=1)
        df.insert(1,"Print","")

    renderer = JsCode("""
class Renderer{
init(params){
this.eGui=document.createElement('span');
this.eGui.innerHTML='🖨';
this.eGui.style.cursor='pointer';

this.eGui.addEventListener('click',()=>{

const win=window.open("","_blank");

// decode base64 to UTF8
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

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=120
    )

    if print_enable:
        gb.configure_column("Print", cellRenderer=renderer, width=70)
        gb.configure_column("print_data", hide=True)

    # Aging highlight
    gb.configure_column(
        "Aging Days",
        cellStyle=JsCode("""
        function(params){
        if(params.value>30){
        return {'color':'white','backgroundColor':'red'}
        }
        }
        """)
    )

    AgGrid(
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=500,
        theme="streamlit"
    )

# --------------------------------------------------
# File Upload
# --------------------------------------------------

file = st.file_uploader("Upload Excel / CSV", type=["xlsx","csv"])

if file:

    if file.name.endswith("csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    # Scheme Filter
    scheme_list = sorted(df["Name Of Scheme"].dropna().unique())
    scheme_filter = st.sidebar.selectbox("Scheme Filter", ["All"] + scheme_list)

    if scheme_filter != "All":
        df = df[df["Name Of Scheme"] == scheme_filter]

    # Date conversion
    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    today = pd.Timestamp.today()

    # Stage 1
    df1 = df[(df["Survey Category"].isna()) & (df["SR Status"]=="OPEN")].copy()
    df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    # Stage 2
    df2 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].isna()) &
             (df["SR Status"]=="OPEN")].copy()
    df2["Aging Days"] = (today - df2["Date Of Survey"]).dt.days

    # Stage 3
    df3 = df[(df["Survey Category"].isin(["A","B","C","D"])) &
             (df["Date Of Est Appr Launch"].notna()) &
             (df["Date Of FQ Issued"].isna()) &
             (df["SR Status"]=="OPEN")].copy()
    df3["Aging Days"] = (today - df3["Date Of Est Appr Launch"]).dt.days

    tab1,tab2,tab3 = st.tabs(["Unsurvey Applications","Estimate Pending","FQ Issue Pending"])

    with tab1:

        st.download_button(
            "⬇ Download Excel",
            df1.to_csv(index=False),
            file_name="survey_pending.csv"
        )

        df1.insert(0,"Sr No",range(1,len(df1)+1))
        display_grid(df1,print_enable=True)

    with tab2:

        st.download_button(
            "⬇ Download Excel",
            df2.to_csv(index=False),
            file_name="estimate_pending.csv"
        )

        df2.insert(0,"Sr No",range(1,len(df2)+1))
        display_grid(df2)

    with tab3:

        st.download_button(
            "⬇ Download Excel",
            df3.to_csv(index=False),
            file_name="fq_pending.csv"
        )

        df3.insert(0,"Sr No",range(1,len(df3)+1))
        display_grid(df3)

else:
    st.info("Upload file to begin")
