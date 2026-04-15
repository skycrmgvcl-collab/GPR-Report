import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import base64
import io

# --- Page Configuration ---
st.set_page_config(page_title="Subdivision SR Dashboard", layout="wide")

st.title("⚡ Subdivision SR Monitoring Dashboard")
st.caption("Survey → Estimate → FQ Tracking")

# -----------------------------------------------------------
# SURVEY FORM HTML GENERATOR
# -----------------------------------------------------------
def get_print_html(row):
    # (Same as before, keep your Gujarati HTML layout here)
    html = f"""
    <html>
    <body style="font-family:sans-serif;">
        <h2>મધ્ય ગુજરાત વીજ કંપની લી.</h2>
        <p>SR Number: {row.get('SR Number','')}</p>
        <p>Name: {row.get('Name Of Applicant','')}</p>
        <hr>
        <p>Address: {row.get('Address1','')}, {row.get('Village Or City','')}</p>
        <script>window.print();</script>
    </body>
    </html>
    """
    return html

# -----------------------------------------------------------
# OPTIMIZED GRID DISPLAY FUNCTION
# -----------------------------------------------------------
def display_grid(df, grid_key):
    """Renders AgGrid with optimizations to prevent Marshalling errors."""
    if df.empty:
        st.info("No records to display.")
        return None

    # CRITICAL: Limit the columns sent to the grid to save memory
    # Update this list with the actual column names you want to see
    essential_cols = [
        "SR Number", "Name Of Applicant", "Consumer Category", 
        "SR Type", "Demand Load", "RC Date", "Village Or City", "Aging Days"
    ]
    
    # Only keep columns that actually exist in the dataframe
    cols_to_show = [c for c in essential_cols if c in df.columns]
    display_df = df[cols_to_show].copy()

    gb = GridOptionsBuilder.from_dataframe(display_df)
    gb.configure_selection('single', use_checkbox=True)
    gb.configure_default_column(filter=True, sortable=True, resizable=True, flex=1)
    
    # Pagination helps with large datasets
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    
    grid_response = AgGrid(
        display_df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        key=grid_key,
        height=400,
        theme='alpine'
    )
    return grid_response

# -----------------------------------------------------------
# MAIN APP LOGIC
# -----------------------------------------------------------
file = st.file_uploader("Upload Excel / CSV", type=["xls", "xlsx", "csv"])

if file:
    # 1. Load Data
    df_raw = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)
    df_raw.columns = df_raw.columns.str.strip()
    
    # 2. Filtering & Aging Logic
    df_filtered = df_raw[df_raw["SR Status"].str.upper() == "OPEN"].copy()
    
    for col in ["RC Date", "Date Of Survey", "Date Of Est Appr Launch"]:
        if col in df_filtered.columns:
            df_filtered[col] = pd.to_datetime(df_filtered[col], errors="coerce")

    today = pd.Timestamp.today()

    # Define DataFrames
    df1 = df_filtered[df_filtered["Survey Category"].isna() | (df_filtered["Survey Category"] == "")].copy()
    if not df1.empty: df1["Aging Days"] = (today - df1["RC Date"]).dt.days

    df2 = df_filtered[df_filtered["Survey Category"].isin(["A","B","C","D"]) & df_filtered["Date Of Est Appr Launch"].isna()].copy()
    if not df2.empty: df2["Aging Days"] = (today - df_filtered["Date Of Survey"]).dt.days

    df3 = df_filtered[df_filtered["Date Of Est Appr Launch"].notna() & df_raw["Date Of FQ Issued"].isna()].copy()
    if not df3.empty: df3["Aging Days"] = (today - df_filtered["Date Of Est Appr Launch"]).dt.days

    # 3. Tabs
    tab1, tab2, tab3 = st.tabs(["Survey Pending", "Estimate Pending", "FQ Pending"])

    with tab1:
        res1 = display_grid(df1, "grid_survey")
        if res1 and res1['selected_rows'] is not None:
            # Handle selection (st-aggrid returns list or dataframe depending on version)
            sel = res1['selected_rows']
            row = sel.iloc[0] if isinstance(sel, pd.DataFrame) else sel[0]
            
            st.sidebar.success(f"Selected: {row['SR Number']}")
            html_content = get_print_html(row)
            b64 = base64.b64encode(html_content.encode()).decode()
            st.sidebar.markdown(f'<a href="data:text/html;base64,{b64}" download="Survey_{row["SR Number"]}.html"><button style="width:100%; height:40px; background-color:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">📥 Download & Print Form</button></a>', unsafe_allow_html=True)

    with tab2:
        display_grid(df2, "grid_estimate")

    with tab3:
        display_grid(df3, "grid_fq")

else:
    st.info("Upload file to begin")
