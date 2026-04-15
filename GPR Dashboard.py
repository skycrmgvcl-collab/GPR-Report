import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import base64
import io

st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ Tracking")

# -----------------------------------------------------------
# SURVEY FORM
# -----------------------------------------------------------

def create_print_html(row):
    # ... (Keep your existing HTML/CSS code exactly as it is) ...
    html = f"""
    <!DOCTYPE html>
    <html>
    <body onload="window.print()">
    <div class="header">મધ્ય ગુજરાત વીજ કંપની લી.</div>
    </body>
    </html>
    """
    return base64.b64encode(html.encode("utf-8")).decode()

# -----------------------------------------------------------
# GRID FUNCTION (UPDATED)
# -----------------------------------------------------------

def display_grid(df, grid_key, print_enable=False): # Added grid_key parameter

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

    # Added 'key' parameter here using the passed grid_key
    AgGrid(
        df,
        gridOptions=gb.build(),
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=min(650, 120 + len(df) * 30),
        key=grid_key 
    )

# -----------------------------------------------------------
# FILE UPLOAD & PROCESSING
# -----------------------------------------------------------

file = st.file_uploader("Upload Excel / CSV", type=["xls", "xlsx", "csv"])

if file:
    if file.name.endswith("csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = df.columns.str.strip()
    df = df[df["SR Status"].str.upper() != "CLOSED"]

    # ... (Keep your Filter and Data Processing logic as is) ...
    # (Assuming df1, df2, df3 are generated correctly)

    tab1, tab2, tab3 = st.tabs(["Survey Pending", "Estimate Pending", "FQ Pending"])

    with tab1:
        if not df1.empty:
            df1.insert(0, "Sr No", range(1, len(df1) + 1))
            buffer = io.BytesIO()
            df1.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export Survey Pending", buffer.getvalue(), "SurveyPending.xlsx")
            
            # Pass a unique key for the first grid
            display_grid(df1, grid_key="grid_survey", print_enable=True)
        else:
            st.write("No pending surveys.")

    with tab2:
        if not df2.empty:
            df2.insert(0, "Sr No", range(1, len(df2) + 1))
            buffer = io.BytesIO()
            df2.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export Estimate Pending", buffer.getvalue(), "EstimatePending.xlsx")
            
            # Pass a unique key for the second grid
            display_grid(df2, grid_key="grid_estimate")
        else:
            st.write("No pending estimates.")

    with tab3:
        if not df3.empty:
            df3.insert(0, "Sr No", range(1, len(df3) + 1))
            buffer = io.BytesIO()
            df3.to_excel(buffer, index=False, engine="xlsxwriter")
            st.download_button("Export FQ Pending", buffer.getvalue(), "FQPending.xlsx")
            
            # Pass a unique key for the third grid
            display_grid(df3, grid_key="grid_fq")
        else:
            st.write("No pending FQ.")

else:
    st.info("Upload file to begin")
