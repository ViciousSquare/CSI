import streamlit as st
import pandas as pd
import os
from utils.data_processor import load_sample_data, process_uploaded_data
from utils.visualizer import create_dashboard_summary

# Set page configuration
st.set_page_config(
    page_title="CSI Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'membership_data' not in st.session_state:
    st.session_state.membership_data = None
if 'partnership_data' not in st.session_state:
    st.session_state.partnership_data = None
if 'program_data' not in st.session_state:
    st.session_state.program_data = None
if 'content_calendar' not in st.session_state:
    st.session_state.content_calendar = None

# Main page header
st.title("Centre for Social Innovation Management System")
st.markdown("""
This system helps you track and optimize CSI's memberships, partnerships, and programs 
by providing data-driven insights and recommendations.
""")

# Sidebar for navigation and data upload
with st.sidebar:
    st.title("Navigation")
    
    # Data Import Section
    st.header("Data Import")
    
    data_type = st.selectbox(
        "Select data type to import",
        ["Membership Data", "Partnership Data", "Program Data", "Content Calendar"]
    )
    
    uploaded_file = st.file_uploader(f"Upload {data_type} (CSV format)", type=["csv"])
    
    if uploaded_file:
        try:
            # Process and store the uploaded data
            if data_type == "Membership Data":
                st.session_state.membership_data = process_uploaded_data(uploaded_file, "membership")
                st.success("Membership data successfully loaded!")
            elif data_type == "Partnership Data":
                st.session_state.partnership_data = process_uploaded_data(uploaded_file, "partnership")
                st.success("Partnership data successfully loaded!")
            elif data_type == "Program Data":
                st.session_state.program_data = process_uploaded_data(uploaded_file, "program")
                st.success("Program data successfully loaded!")
            elif data_type == "Content Calendar":
                st.session_state.content_calendar = process_uploaded_data(uploaded_file, "content")
                st.success("Content calendar successfully loaded!")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    # Option to load sample data for demonstration
    if st.button("Load Sample Data"):
        st.session_state.membership_data = load_sample_data("membership")
        st.session_state.partnership_data = load_sample_data("partnership")
        st.session_state.program_data = load_sample_data("program")
        st.session_state.content_calendar = load_sample_data("content")
        st.success("Sample data loaded successfully!")
    
    # Navigation Links
    st.header("Pages")
    st.markdown("[Home](#)")
    st.markdown("[Membership Management](/membership)")
    st.markdown("[Partnership Management](/partnerships)")
    st.markdown("[Program Management](/programs)")
    st.markdown("[Content Calendar](/content_calendar)")
    st.markdown("[Business Insights](/insights)")

# Main content area - Dashboard Overview
st.header("Dashboard Overview")

# Check if data is available
if (st.session_state.membership_data is None and 
    st.session_state.partnership_data is None and
    st.session_state.program_data is None):
    
    st.info("👆 Please upload or load sample data using the sidebar to get started.")
    
    # Show getting started information
    st.markdown("""
    ## Getting Started
    
    This management system helps CSI track and optimize:
    
    1. **Membership Management**
       - Track current member engagement and satisfaction
       - Identify opportunities for value enhancement
       - Find potential new members
       
    2. **Partnership Management**
       - Monitor current partnerships and performance
       - Discover potential new strategic partners
       - Optimize collaboration effectiveness
       
    3. **Program Management**
       - Evaluate existing program performance
       - Get recommendations for new programs
       - Optimize program deployment with minimal overhead
       
    4. **Content & Business Development**
       - Automated content creation and scheduling
       - Generate business development insights
       - Track key performance metrics
    """)
else:
    # Display dashboard summary with available data
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.membership_data is not None:
            st.subheader("Membership Summary")
            membership_metrics = create_dashboard_summary(st.session_state.membership_data, "membership")
            st.plotly_chart(membership_metrics, use_container_width=True)
        
        if st.session_state.program_data is not None:
            st.subheader("Program Performance")
            program_metrics = create_dashboard_summary(st.session_state.program_data, "program")
            st.plotly_chart(program_metrics, use_container_width=True)
    
    with col2:
        if st.session_state.partnership_data is not None:
            st.subheader("Partnership Overview")
            partnership_metrics = create_dashboard_summary(st.session_state.partnership_data, "partnership")
            st.plotly_chart(partnership_metrics, use_container_width=True)
        
        if st.session_state.content_calendar is not None:
            st.subheader("Content Calendar Status")
            content_metrics = create_dashboard_summary(st.session_state.content_calendar, "content")
            st.plotly_chart(content_metrics, use_container_width=True)
    
    # Show KPI summary if all data is available
    if (st.session_state.membership_data is not None and 
        st.session_state.partnership_data is not None and
        st.session_state.program_data is not None):
        
        st.header("Key Performance Indicators")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric(
                label="Total Members", 
                value=len(st.session_state.membership_data), 
                delta="+5 this month"
            )
            
        with kpi2:
            active_partnerships = st.session_state.partnership_data[
                st.session_state.partnership_data["status"] == "Active"
            ].shape[0]
            st.metric(
                label="Active Partnerships", 
                value=active_partnerships,
                delta="+2 this quarter"
            )
            
        with kpi3:
            avg_satisfaction = st.session_state.membership_data["satisfaction_score"].mean()
            st.metric(
                label="Avg. Member Satisfaction", 
                value=f"{avg_satisfaction:.1f}/10",
                delta="+0.3 since last survey"
            )
            
        with kpi4:
            active_programs = st.session_state.program_data[
                st.session_state.program_data["status"] == "Active"
            ].shape[0]
            st.metric(
                label="Active Programs", 
                value=active_programs,
                delta="+1 this quarter"
            )

# Footer
st.markdown("---")
st.markdown("© 2023 Centre for Social Innovation Management System")
