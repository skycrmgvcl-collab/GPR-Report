import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import io

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.markdown("""
<style>
.block-container {padding-top:1rem;}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ → Release Stage Tracking")

# -----------------------------------------------------------
# SURVEY FORM  (UNCHANGED FROM YOUR PROGRAM)
# -----------------------------------------------------------

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
2. ટ્રાન્સફોર્મરનું નામ :- <span class="line" style="width:200px"></span>
</td>
<td>
ટ્રાન્સફોર્મર કેપેસીટી :- ______
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
4. મકાન ઉપરથી કે નજીકથી HT/LT લાઇન પસાર થાય છે કે કેમ ?
<span class="line"></span>
</td>
</tr>

<tr>
<td>8</td>
<td>
સદર મકાન કેટલા માળનું છે :-
<span class="line"></span>
</td>

<td>
કાચું કે પાકું :- ______
</td>
</tr>

<tr>
<td>9</td>
<td colspan="2">
સદર મકાનની ઊંચાઈ ૧૫ મીટર કરતાં વધારે છે ?
<span class="line"></span>
</td>
</tr>

<tr>
<td>10</td>
<td colspan="2">
અન્ય વિજ જોડાણ હોય તો વિગત
<span class="line"></span>
</td>
</tr>

<tr>
<td>12</td>
<td colspan="2">
ગામતળ / સિમતળ
<span class="line"></span>
</td>
</tr>

<tr>
<td>13</td>
<td>સર્વે કેટેગરી :- ______</td>
<td>પોલ થી અંતર :- ______</td>
</tr>

<tr>
<td>14</td>
<td colspan="2">
નકશો તથા અન્ય વિગતો
<div class="sketch"></div>
</td>
</tr>

<tr>
<td></td>
<td colspan="2">
Exist. Cons. No. :- {row.get("Consumer No","")}
</td>
</tr>

</table>

<br><br>

<table class="signature">
<tr>
<td>અરજદાર / પ્રતિનિધિની સહી</td>
<td>સર્વે કરનાર</td>
<td>જુ.ઇ. ની સહી</td>
</tr>
</table>

</body>
</html>
"""

    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID FUNCTION
# -----------------------------------------------------------

def display_grid(df,print_enable=False):

    df=df.copy()

    if print_enable:
        df["print_data"]=df.apply(create_print_html,axis=1)
        df.insert(1,"Print","")

    renderer=JsCode("""
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

    gb=GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        filter=True,
        sortable=True,
        resizable=True,
        flex=1,
        minWidth=120
    )

    if print_enable:
        gb.configure_column("Print",cellRenderer=renderer,width=70)
        gb.configure_column("print_data",hide=True)

    AgGrid(
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=min(650,120+len(df)*30)
    )

# -----------------------------------------------------------
# FILE UPLOAD
# -----------------------------------------------------------

file=st.file_uploader("Upload Excel / CSV",type=["xlsx","csv"])

if file:

    if file.name.endswith("csv"):
        df=pd.read_csv(file)
    else:
        df=pd.read_excel(file)

    # remove closed SR
    df=df[df["SR Status"].str.upper()!="CLOSED"]

    st.sidebar.title("Filters")

    scheme_list=sorted(df["Name Of Scheme"].dropna().unique())
    scheme_filter=st.sidebar.selectbox("Select Scheme",["All"]+scheme_list)

    if scheme_filter!="All":
        df=df[df["Name Of Scheme"]==scheme_filter]

    # Better SR Type UI
    with st.sidebar.expander("SR Type Selection",expanded=True):

        sr_types=sorted(df["SR Type"].dropna().unique())
        selected_sr=st.multiselect("Choose SR Type",sr_types,default=sr_types)

    df=df[df["SR Type"].isin(selected_sr)]

    # Search
    search=st.text_input("🔎 Search SR Number")

    if search:
        df=df[df["SR Number"].astype(str).str.contains(search,case=False,na=False)]

    # Date conversion
    for col in ["RC Date","Date Of Survey","Date Of Est Appr Launch","Date Of FQ Issued"]:
        if col in df.columns:
            df[col]=pd.to_datetime(df[col],errors="coerce")

    today=pd.Timestamp.today()

    # Stage Logic
    df1=df[(df["Survey Category"].isna())&(df["SR Status"]=="OPEN")].copy()
    df1["Aging Days"]=(today-df1["RC Date"]).dt.days

    df2=df[(df["Survey Category"].isin(["A","B","C","D"]))&(df["Date Of Est Appr Launch"].isna())&(df["SR Status"]=="OPEN")].copy()
    df2["Aging Days"]=(today-df2["Date Of Survey"]).dt.days

    df3=df[(df["Survey Category"].isin(["A","B","C","D"]))&(df["Date Of Est Appr Launch"].notna())&(df["Date Of FQ Issued"].isna())&(df["SR Status"]=="OPEN")].copy()
    df3["Aging Days"]=(today-df3["Date Of Est Appr Launch"]).dt.days

    # Metrics
    col1,col2,col3,col4=st.columns(4)

    col1.metric("📝 Survey Pending",len(df1))
    col2.metric("📐 Estimate Pending",len(df2))
    col3.metric("💰 FQ Pending",len(df3))
    col4.metric("📊 Total SR",len(df1)+len(df2)+len(df3))

    # Tabs
    tab1,tab2,tab3=st.tabs(["📋 Survey Pending","📐 Estimate Pending","💰 FQ Pending"])

    tab1_cols=[
    "SR Number","SR Type","Name Of Applicant","Address1","Address2","District",
    "Taluka","Village Or City","Consumer Category","Sub Category","Name Of Scheme",
    "Demand Load","Load Uom","Tariff","RC Date","RC MR NO","RC Charge",
    "Survey Category","SR Status","Rev Land Syrvey No"
    ]

    with tab1:
        df1=df1[tab1_cols]
        df1.insert(0,"Sr No",range(1,len(df1)+1))
        display_grid(df1,print_enable=True)

    with tab2:
        df2.insert(0,"Sr No",range(1,len(df2)+1))
        display_grid(df2)

    with tab3:
        df3.insert(0,"Sr No",range(1,len(df3)+1))
        display_grid(df3)

else:
    st.info("Upload file to begin")
