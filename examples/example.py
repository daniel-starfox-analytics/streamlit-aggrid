import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# Set page config to wide mode
st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    # Replace with your actual CSV file path
    data = pd.read_csv("/workspaces/streamlit-aggrid/examples/bquxjob_6c59d1a9_1946f6e52da.csv")
    return data

st.title("Event Parameters Analysis")

# Use the full width of the page
st.markdown("""
    <style>
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .stDataFrame {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

data = load_data()
shouldDisplayPivoted = st.checkbox("Show Pivoted View")

gb = GridOptionsBuilder.from_dataframe(data)

# Configure common column properties
gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
    flex=1  # Make columns flex to fill space
)

# Configure the event_name column as the main grouping column
gb.configure_column(
    field="event_name",
    header_name="Event Name",
    minWidth=200,
    rowGroup=True,
    pivot=True,
    hide=shouldDisplayPivoted
)

# Configure param_type as a secondary grouping column
gb.configure_column(
    field="param_type",
    header_name="Parameter Type",
    minWidth=150,
    rowGroup=True,
    hide=shouldDisplayPivoted
)

# Configure param_key as the pivot column
gb.configure_column(
    field="param_key",
    header_name="Parameter Key",
    rowGroup=True,
    pivot=True,
    hide=True
)

# Configure value columns
value_columns = [
    "event_total_count",
    "total_occurrences",
    "valid_occurrences",
    "coverage_percentage",
    "is_always_present"
]

for col in value_columns:
    gb.configure_column(
        field=col,
        header_name=col.replace("_", " ").title(),
        type=["numericColumn"],
        aggFunc="first",
        valueFormatter="value.toLocaleString()" if "occurrences" in col else None,
        minWidth=120  # Ensure minimum width for readability
    )

# Configure grid options for pivoting
gb.configure_grid_options(
    pivotMode=shouldDisplayPivoted,
    suppressAggFuncInHeader=True,
    autoGroupColumnDef=dict(
        minWidth=250,
        pinned="left",
        cellRendererParams=dict(
            suppressCount=True,
            innerRenderer="agGroupCellRenderer"
        )
    ),
    domLayout='normal',  # Use normal layout for better width control
    width='100%'  # Set grid width to 100%
)

# Build and display the grid
go = gb.build()

# Create a container for the grid that uses the full width
with st.container():
    AgGrid(
        data,
        gridOptions=go,
        height=600,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,  # Make columns fit the available space
        update_mode='value_changed',
        theme='streamlit',  # Use streamlit theme for better integration
        key='grid1'
    )

# Add summary statistics in a full-width container
if not shouldDisplayPivoted:
    st.subheader("Summary Statistics")
    cols = st.columns(4)  # Create 4 columns for better spacing
    with cols[0]:
        st.metric("Total Events", len(data['event_name'].unique()))
    with cols[1]:
        st.metric("Total Parameters", data['param_key'].nunique())
    with cols[2]:
        st.metric("Average Coverage", f"{data['coverage_percentage'].mean():.2f}%")
    with cols[3]:
        st.metric("Always Present Parameters", data['is_always_present'].sum())