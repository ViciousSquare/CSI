import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def create_dashboard_summary(data, data_type):
    """
    Create summary visualizations for the dashboard based on data type
    
    Parameters:
    - data: DataFrame with the relevant data
    - data_type: Type of data (membership, partnership, program, content)
    
    Returns:
    - Plotly figure object for the dashboard summary
    """
    if data is None or len(data) == 0:
        # Create an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available. Please upload or load sample data.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(height=300)
        return fig
    
    if data_type == "membership":
        # Create membership summary visualization
        if "membership_type" in data.columns:
            member_type_counts = data["membership_type"].value_counts()
            
            fig = px.pie(
                values=member_type_counts.values,
                names=member_type_counts.index,
                title="Membership Types",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4
            )
            
            fig.update_layout(
                legend_title="Membership Type",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            return fig
        else:
            # Alternative visualization if membership_type is not available
            return px.bar(
                data_frame=data,
                y=data.index,
                x="member_id",
                title="Member Count",
                height=300
            )
            
    elif data_type == "partnership":
        # Create partnership summary visualization
        if "status" in data.columns:
            status_counts = data["status"].value_counts()
            
            fig = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Partnership Status Summary",
                color=status_counts.index,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            
            fig.update_layout(
                xaxis_title="Status",
                yaxis_title="Number of Partnerships",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                showlegend=False
            )
            
            return fig
        else:
            # Alternative visualization
            return px.scatter(
                data_frame=data,
                x="partner_id",
                y="name",
                title="Partnerships Overview",
                height=300
            )
            
    elif data_type == "program":
        # Create program summary visualization
        if "status" in data.columns:
            status_counts = data["status"].value_counts()
            
            fig = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Program Status Summary",
                color=status_counts.index,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                xaxis_title="Status",
                yaxis_title="Number of Programs",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                showlegend=False
            )
            
            return fig
        else:
            # Alternative visualization
            return px.scatter(
                data_frame=data,
                x="program_id",
                y="name",
                title="Programs Overview",
                height=300
            )
            
    elif data_type == "content":
        # Create content calendar summary visualization
        if "status" in data.columns:
            status_counts = data["status"].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Content Status",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            
            fig.update_layout(
                legend_title="Status",
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            return fig
        else:
            # Alternative visualization
            return px.scatter(
                data_frame=data,
                x="content_id",
                y="title",
                title="Content Calendar Overview",
                height=300
            )
    
    # Default visualization if data_type is not recognized
    fig = go.Figure()
    fig.add_annotation(
        text=f"No visualization available for {data_type} data type.",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14)
    )
    fig.update_layout(height=300)
    return fig

def plot_member_engagement(membership_data):
    """
    Create visualization for member engagement analysis
    
    Parameters:
    - membership_data: DataFrame with member engagement data
    
    Returns:
    - Plotly figure object
    """
    if membership_data is None or len(membership_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No membership data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Create a scatter plot of engagement score vs membership duration
    if "engagement_score" in membership_data.columns and "membership_duration_days" in membership_data.columns:
        fig = px.scatter(
            membership_data,
            x="membership_duration_days",
            y="engagement_score",
            color="membership_type" if "membership_type" in membership_data.columns else None,
            hover_name="name",
            hover_data=["satisfaction_score", "attendance_rate"] if "satisfaction_score" in membership_data.columns else None,
            title="Member Engagement Analysis",
            labels={
                "membership_duration_days": "Membership Duration (days)",
                "engagement_score": "Engagement Score"
            },
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            height=500,
            hovermode="closest"
        )
        
        return fig
    else:
        # Alternative visualization if engagement_score is not available
        return px.histogram(
            membership_data,
            x="membership_type" if "membership_type" in membership_data.columns else "member_id",
            title="Membership Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

def plot_partnership_effectiveness(partnership_data):
    """
    Create visualization for partnership effectiveness
    
    Parameters:
    - partnership_data: DataFrame with partnership data
    
    Returns:
    - Plotly figure object
    """
    if partnership_data is None or len(partnership_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No partnership data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # If we have effectiveness metrics, create a bubble chart
    if "effectiveness_score" in partnership_data.columns and "value_contribution" in partnership_data.columns:
        # Create a copy to avoid modifying the original dataframe
        plot_data = partnership_data.copy()
        
        # Ensure partnership_duration is positive for plotting
        if "partnership_duration" in plot_data.columns:
            # Use absolute value to ensure positive values for size
            plot_data["plot_duration"] = plot_data["partnership_duration"].abs()
            size_col = "plot_duration"
        else:
            size_col = None
            
        fig = px.scatter(
            plot_data,
            x="effectiveness_score",
            y="value_contribution",
            size=size_col,
            color="partnership_type" if "partnership_type" in plot_data.columns else "status",
            hover_name="name",
            hover_data=["status", "start_date"],
            title="Partnership Effectiveness vs Value",
            labels={
                "effectiveness_score": "Effectiveness Score",
                "value_contribution": "Value Contribution",
                "plot_duration": "Partnership Duration (days)"
            },
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        
        fig.update_layout(
            height=500,
            hovermode="closest"
        )
        
        return fig
    else:
        # Alternative visualization
        if "partnership_type" in partnership_data.columns and "status" in partnership_data.columns:
            # Create a grouped bar chart of partnership types by status
            partnership_counts = partnership_data.groupby(["partnership_type", "status"]).size().reset_index(name="count")
            
            fig = px.bar(
                partnership_counts,
                x="partnership_type",
                y="count",
                color="status",
                title="Partnership Types by Status",
                labels={
                    "partnership_type": "Partnership Type",
                    "count": "Number of Partnerships",
                    "status": "Status"
                },
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            
            fig.update_layout(
                height=500,
                barmode="group"
            )
            
            return fig
        else:
            # Simple bar chart
            return px.bar(
                partnership_data,
                x="status" if "status" in partnership_data.columns else "partner_id",
                title="Partnership Status",
                color_discrete_sequence=px.colors.qualitative.Safe
            )

def plot_program_performance(program_data):
    """
    Create visualization for program performance
    
    Parameters:
    - program_data: DataFrame with program data
    
    Returns:
    - Plotly figure object
    """
    if program_data is None or len(program_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No program data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Create bar chart of program performance scores
    if "performance_score" in program_data.columns:
        # Sort by performance score descending
        sorted_data = program_data.sort_values("performance_score", ascending=False)
        
        fig = px.bar(
            sorted_data,
            x="name",
            y="performance_score",
            color="status" if "status" in sorted_data.columns else None,
            title="Program Performance Scores",
            labels={
                "name": "Program Name",
                "performance_score": "Performance Score",
                "status": "Status"
            },
            hover_data=["enrollment_rate", "satisfaction_score"] if "enrollment_rate" in sorted_data.columns else None,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    elif "satisfaction_score" in program_data.columns and "enrollment_rate" in program_data.columns:
        # Alternative visualization - scatter plot of satisfaction vs enrollment
        # Create a copy to avoid modifying the original dataframe
        plot_data = program_data.copy()
        
        # Ensure capacity is positive for plotting
        if "capacity" in plot_data.columns:
            # Use absolute value to ensure positive values for size
            plot_data["plot_capacity"] = plot_data["capacity"].abs()
            size_col = "plot_capacity"
        else:
            size_col = None
            
        fig = px.scatter(
            plot_data,
            x="enrollment_rate",
            y="satisfaction_score",
            color="program_type" if "program_type" in plot_data.columns else "status",
            hover_name="name",
            size=size_col,
            title="Program Satisfaction vs Enrollment",
            labels={
                "enrollment_rate": "Enrollment Rate",
                "satisfaction_score": "Satisfaction Score",
                "program_type": "Program Type",
                "plot_capacity": "Capacity"
            },
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            height=500,
            hovermode="closest"
        )
        
        return fig
    else:
        # Simple bar chart of program status
        if "status" in program_data.columns:
            status_counts = program_data["status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            
            fig = px.bar(
                status_counts,
                x="status",
                y="count",
                title="Program Status Distribution",
                color="status",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                height=500,
                xaxis_title="Status",
                yaxis_title="Number of Programs"
            )
            
            return fig
        else:
            # Very basic chart
            return px.bar(
                program_data,
                x="program_id",
                y="name",
                title="Programs Overview",
                color_discrete_sequence=px.colors.qualitative.Bold
            )

def plot_content_calendar(content_data):
    """
    Create visualization for content calendar
    
    Parameters:
    - content_data: DataFrame with content calendar data
    
    Returns:
    - Plotly figure object
    """
    if content_data is None or len(content_data) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No content calendar data available.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        return fig
    
    # Create timeline of content publishing
    if "publish_date" in content_data.columns and "content_type" in content_data.columns:
        # Sort by publish date
        sorted_data = content_data.sort_values("publish_date")
        
        # For better visualization, filter to the most recent and upcoming content
        today = datetime.now()
        recent_date = today - timedelta(days=30)
        future_date = today + timedelta(days=60)
        
        filtered_data = sorted_data[
            (sorted_data["publish_date"] >= recent_date) & 
            (sorted_data["publish_date"] <= future_date)
        ]
        
        # If filtered data is empty, use all data
        if len(filtered_data) == 0:
            filtered_data = sorted_data
        
        fig = px.timeline(
            filtered_data,
            x_start="publish_date",
            x_end="publish_date",
            y="content_type",
            color="status" if "status" in filtered_data.columns else "content_type",
            hover_name="title",
            hover_data=["channel", "author"] if "channel" in filtered_data.columns else None,
            title="Content Calendar Timeline",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        # Add a vertical line for today's date
        # Convert to Plotly's preferred timestamp format
        today_timestamp = today.timestamp() * 1000  # Convert to milliseconds timestamp
        fig.add_vline(
            x=today_timestamp,
            line_width=2,
            line_dash="dash",
            line_color="grey",
            annotation_text="Today"
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Publish Date",
            yaxis_title="Content Type"
        )
        
        return fig
    elif "content_type" in content_data.columns:
        # Alternative - content type distribution
        type_counts = content_data["content_type"].value_counts().reset_index()
        type_counts.columns = ["content_type", "count"]
        
        fig = px.bar(
            type_counts,
            x="content_type",
            y="count",
            title="Content Types Distribution",
            color="content_type",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="Content Type",
            yaxis_title="Count",
            showlegend=False
        )
        
        return fig
    else:
        # Basic chart
        return px.bar(
            content_data,
            x="content_id",
            y="title",
            title="Content Overview",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )

def create_kpi_metrics(data_dict):
    """
    Create KPI metrics figures
    
    Parameters:
    - data_dict: Dictionary containing different dataframes
    
    Returns:
    - Dictionary of Plotly figure objects for KPIs
    """
    kpi_figures = {}
    
    # Membership KPIs
    if 'membership_data' in data_dict and data_dict['membership_data'] is not None:
        membership_data = data_dict['membership_data']
        
        # Total members trend
        if 'join_date' in membership_data.columns:
            # Create monthly join date counts
            membership_data['month_year'] = membership_data['join_date'].dt.strftime('%Y-%m')
            monthly_joins = membership_data.groupby('month_year').size().reset_index(name='new_members')
            monthly_joins['month_year'] = pd.to_datetime(monthly_joins['month_year'] + '-01')
            
            # Sort by date
            monthly_joins = monthly_joins.sort_values('month_year')
            
            # Calculate cumulative sum
            monthly_joins['total_members'] = monthly_joins['new_members'].cumsum()
            
            # Create line chart
            fig = px.line(
                monthly_joins, 
                x='month_year', 
                y='total_members',
                title='Total Membership Growth',
                labels={'month_year': 'Month', 'total_members': 'Total Members'},
                markers=True
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            kpi_figures['membership_growth'] = fig
            
        # Member satisfaction
        if 'satisfaction_score' in membership_data.columns:
            # Calculate average satisfaction by membership type if available
            if 'membership_type' in membership_data.columns:
                satisfaction_by_type = membership_data.groupby('membership_type')['satisfaction_score'].mean().reset_index()
                
                fig = px.bar(
                    satisfaction_by_type,
                    x='membership_type',
                    y='satisfaction_score',
                    title='Average Satisfaction by Membership Type',
                    labels={'membership_type': 'Membership Type', 'satisfaction_score': 'Avg. Satisfaction'},
                    color='membership_type',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                
                fig.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=40, b=10),
                    showlegend=False
                )
                
                kpi_figures['satisfaction_by_type'] = fig
    
    # Partnership KPIs
    if 'partnership_data' in data_dict and data_dict['partnership_data'] is not None:
        partnership_data = data_dict['partnership_data']
        
        # Partnership value contribution
        if 'value_contribution' in partnership_data.columns and 'partnership_type' in partnership_data.columns:
            value_by_type = partnership_data.groupby('partnership_type')['value_contribution'].sum().reset_index()
            
            fig = px.pie(
                value_by_type,
                values='value_contribution',
                names='partnership_type',
                title='Value Contribution by Partnership Type',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            kpi_figures['partnership_value'] = fig
    
    # Program KPIs
    if 'program_data' in data_dict and data_dict['program_data'] is not None:
        program_data = data_dict['program_data']
        
        # Program enrollment rates
        if 'enrollment_rate' in program_data.columns:
            # Get top programs by enrollment rate
            top_programs = program_data.sort_values('enrollment_rate', ascending=False).head(5)
            
            fig = px.bar(
                top_programs,
                x='name',
                y='enrollment_rate',
                title='Top 5 Programs by Enrollment Rate',
                labels={'name': 'Program', 'enrollment_rate': 'Enrollment Rate'},
                color='program_type' if 'program_type' in top_programs.columns else None,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_tickangle=-45
            )
            
            kpi_figures['top_programs'] = fig
    
    return kpi_figures
