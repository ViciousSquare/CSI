import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

from utils.data_processor import (
    calculate_member_engagement, 
    calculate_partnership_effectiveness,
    analyze_program_performance
)
from utils.visualizer import create_kpi_metrics

def app():
    st.title("Business Development Insights")
    
    # Check if data is available
    if ('membership_data' not in st.session_state or st.session_state.membership_data is None) and \
       ('partnership_data' not in st.session_state or st.session_state.partnership_data is None) and \
       ('program_data' not in st.session_state or st.session_state.program_data is None):
        st.info("No data available for analysis. Please upload or load sample data from the main page.")
        return
    
    # Process data if available
    data_dict = {}
    
    if 'membership_data' in st.session_state and st.session_state.membership_data is not None:
        data_dict['membership_data'] = calculate_member_engagement(st.session_state.membership_data)
    
    if 'partnership_data' in st.session_state and st.session_state.partnership_data is not None:
        data_dict['partnership_data'] = calculate_partnership_effectiveness(st.session_state.partnership_data)
    
    if 'program_data' in st.session_state and st.session_state.program_data is not None:
        data_dict['program_data'] = analyze_program_performance(st.session_state.program_data)
    
    # Create tabs for different insights views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview Insights", 
        "Membership Insights", 
        "Partnership Insights",
        "Program Insights"
    ])
    
    with tab1:
        st.header("Key Business Insights")
        
        # Display high-level KPIs
        st.subheader("Performance Overview")
        
        # Create overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'membership_data' in data_dict:
                total_members = len(data_dict['membership_data'])
                st.metric("Total Members", total_members)
            else:
                st.metric("Total Members", "N/A")
                
        with col2:
            if 'partnership_data' in data_dict:
                total_partners = len(data_dict['partnership_data'])
                active_partners = data_dict['partnership_data'][data_dict['partnership_data']['status'] == 'Active'].shape[0] if 'status' in data_dict['partnership_data'].columns else 0
                st.metric("Active Partnerships", active_partners)
            else:
                st.metric("Active Partnerships", "N/A")
                
        with col3:
            if 'program_data' in data_dict:
                total_programs = len(data_dict['program_data'])
                active_programs = data_dict['program_data'][data_dict['program_data']['status'] == 'Active'].shape[0] if 'status' in data_dict['program_data'].columns else 0
                st.metric("Active Programs", active_programs)
            else:
                st.metric("Active Programs", "N/A")
                
        with col4:
            # Calculate overall health score based on available data
            health_score = 0
            health_components = 0
            
            if 'membership_data' in data_dict and 'engagement_score' in data_dict['membership_data'].columns:
                avg_engagement = data_dict['membership_data']['engagement_score'].mean()
                health_score += avg_engagement
                health_components += 1
                
            if 'partnership_data' in data_dict and 'effectiveness_score' in data_dict['partnership_data'].columns:
                avg_effectiveness = data_dict['partnership_data']['effectiveness_score'].mean() * 10  # Scale to 0-100
                health_score += avg_effectiveness
                health_components += 1
                
            if 'program_data' in data_dict and 'performance_score' in data_dict['program_data'].columns:
                avg_performance = data_dict['program_data']['performance_score'].mean()
                health_score += avg_performance
                health_components += 1
                
            if health_components > 0:
                overall_health = health_score / health_components
                st.metric("Overall Health", f"{overall_health:.1f}/100")
            else:
                st.metric("Overall Health", "N/A")
        
        # Display KPI charts if data is available
        kpi_figs = create_kpi_metrics(data_dict)
        
        if kpi_figs:
            st.subheader("Key Performance Indicators")
            
            # Display KPI charts in a 2x2 grid
            chart_keys = list(kpi_figs.keys())
            
            # Create rows of 2 charts each
            for i in range(0, len(chart_keys), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    if i < len(chart_keys):
                        st.plotly_chart(kpi_figs[chart_keys[i]], use_container_width=True)
                        
                with col2:
                    if i + 1 < len(chart_keys):
                        st.plotly_chart(kpi_figs[chart_keys[i + 1]], use_container_width=True)
        
        # Insights and recommendations summary
        st.subheader("Strategic Insights & Recommendations")
        
        # Generate insights based on available data
        insights = []
        
        # Membership insights
        if 'membership_data' in data_dict:
            membership_data = data_dict['membership_data']
            
            if 'engagement_level' in membership_data.columns:
                # Calculate engagement distribution
                engagement_counts = membership_data['engagement_level'].value_counts()
                high_engagement_pct = (engagement_counts.get('High', 0) / len(membership_data) * 100) if len(membership_data) > 0 else 0
                low_engagement_pct = (engagement_counts.get('Low', 0) + engagement_counts.get('Very Low', 0)) / len(membership_data) * 100 if len(membership_data) > 0 else 0
                
                if high_engagement_pct >= 50:
                    insights.append("**Strong Member Engagement**: Over 50% of members show high engagement. Continue with current engagement strategies while focusing on at-risk members.")
                elif low_engagement_pct >= 40:
                    insights.append("**Member Engagement Needs Attention**: A significant portion of members show low engagement. Consider implementing a targeted re-engagement strategy.")
            
            if 'industry' in membership_data.columns:
                # Identify top industries
                top_industries = membership_data['industry'].value_counts().head(2).index.tolist()
                insights.append(f"**Industry Focus**: {', '.join(top_industries)} are your most represented industries. Consider developing specialized resources for these sectors.")
                
            # Check for expiring memberships
            if 'renewal_date' in membership_data.columns:
                today = datetime.now()
                expiring_soon = membership_data[
                    (membership_data['renewal_date'] > today) & 
                    (membership_data['renewal_date'] <= today + timedelta(days=30))
                ]
                if len(expiring_soon) > 0:
                    insights.append(f"**Renewal Opportunity**: {len(expiring_soon)} memberships are expiring within 30 days. Prioritize renewal outreach.")
        
        # Partnership insights
        if 'partnership_data' in data_dict:
            partnership_data = data_dict['partnership_data']
            
            if 'effectiveness_score' in partnership_data.columns:
                # Check for high-value low-effectiveness partnerships
                if 'value_contribution' in partnership_data.columns:
                    high_value_low_effectiveness = partnership_data[
                        (partnership_data['effectiveness_score'] < 6) & 
                        (partnership_data['value_contribution'] > partnership_data['value_contribution'].median())
                    ]
                    if len(high_value_low_effectiveness) > 0:
                        insights.append(f"**Partnership Optimization**: {len(high_value_low_effectiveness)} high-value partnerships show low effectiveness. Review and strengthen these strategic relationships.")
            
            if 'partnership_type' in partnership_data.columns and 'status' in partnership_data.columns:
                # Check partnership type distribution for active partnerships
                active_partnerships = partnership_data[partnership_data['status'] == 'Active']
                if len(active_partnerships) > 0:
                    type_counts = active_partnerships['partnership_type'].value_counts()
                    top_type = type_counts.index[0] if len(type_counts) > 0 else None
                    if top_type and type_counts[top_type] > len(active_partnerships) * 0.5:
                        insights.append(f"**Partnership Diversity**: Over 50% of active partnerships are '{top_type}'. Consider diversifying partnership types for resilience.")
        
        # Program insights
        if 'program_data' in data_dict:
            program_data = data_dict['program_data']
            
            if 'performance_score' in program_data.columns and 'status' in program_data.columns:
                # Check for underperforming active programs
                active_programs = program_data[program_data['status'] == 'Active']
                if len(active_programs) > 0:
                    underperforming = active_programs[active_programs['performance_score'] < 60]
                    if len(underperforming) > 0:
                        insights.append(f"**Program Performance Gap**: {len(underperforming)} active programs are underperforming. Conduct reviews to identify improvement opportunities.")
            
            if 'enrollment_rate' in program_data.columns and 'status' in program_data.columns:
                # Check enrollment rates of active programs
                active_programs = program_data[program_data['status'] == 'Active']
                if len(active_programs) > 0:
                    low_enrollment = active_programs[active_programs['enrollment_rate'] < 0.5]
                    if len(low_enrollment) > len(active_programs) * 0.3:
                        insights.append("**Enrollment Challenge**: Multiple programs have less than 50% enrollment. Review marketing and targeting strategies.")
        
        # Display insights
        if insights:
            for insight in insights:
                st.write(f"- {insight}")
        else:
            st.write("Upload more data to generate strategic insights.")
        
        # Overall business development recommendations
        st.subheader("Business Development Action Plan")
        
        st.markdown("""
        Based on the available data, consider the following strategic actions:
        
        1. **Segment-Specific Engagement**: Develop targeted engagement strategies for different member segments, especially focusing on those showing signs of reduced engagement.
        
        2. **Partnership Portfolio Optimization**: Regularly review partnership effectiveness and ensure a balanced portfolio across different partnership types.
        
        3. **Program Innovation Pipeline**: Establish a structured process for program development, testing, and evaluation to ensure offerings remain relevant.
        
        4. **Data-Driven Decision Making**: Continue to improve data collection and analysis to measure impact and inform strategic decisions.
        
        5. **Community-Centered Growth**: Ensure all growth initiatives strengthen the core community and maintain alignment with CSI's mission.
        """)
        
        # Show impact projection if sufficient data is available
        if len(data_dict) >= 2:
            st.subheader("Growth Projection")
            
            # Create simple projection chart
            months = 12
            today = datetime.now()
            projection_dates = [today + timedelta(days=30*i) for i in range(months)]
            
            # Create different projection scenarios
            base_growth = np.linspace(1, 1.1, months)  # 10% growth over year
            accelerated_growth = np.linspace(1, 1.2, months)  # 20% growth over year
            optimized_growth = np.linspace(1, 1.3, months)  # 30% growth over year
            
            projection_df = pd.DataFrame({
                'Date': projection_dates,
                'Current Strategy': base_growth,
                'Enhanced Engagement': accelerated_growth,
                'Optimized Strategy': optimized_growth
            })
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=projection_df['Date'], 
                y=projection_df['Current Strategy'],
                mode='lines',
                name='Current Strategy',
                line=dict(color='blue')
            ))
            
            fig.add_trace(go.Scatter(
                x=projection_df['Date'], 
                y=projection_df['Enhanced Engagement'],
                mode='lines',
                name='Enhanced Engagement',
                line=dict(color='green')
            ))
            
            fig.add_trace(go.Scatter(
                x=projection_df['Date'], 
                y=projection_df['Optimized Strategy'],
                mode='lines',
                name='Optimized Strategy',
                line=dict(color='red')
            ))
            
            fig.update_layout(
                title='Projected Growth (Relative Scale)',
                xaxis_title='Timeline',
                yaxis_title='Growth Factor',
                legend_title='Scenarios',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Projection Scenarios:**
            
            - **Current Strategy**: Continuing existing approaches (est. 10% annual growth)
            - **Enhanced Engagement**: Implementing targeted engagement strategies (est. 20% annual growth)
            - **Optimized Strategy**: Full implementation of data-driven recommendations (est. 30% annual growth)
            
            *Note: These projections are estimates based on available data patterns and industry benchmarks.*
            """)
    
    with tab2:
        st.header("Membership Insights")
        
        if 'membership_data' not in data_dict:
            st.info("No membership data available. Please upload membership data from the main page.")
        else:
            membership_data = data_dict['membership_data']
            
            # Membership retention analysis
            st.subheader("Membership Retention Analysis")
            
            if 'join_date' in membership_data.columns:
                # Calculate membership duration in months
                today = datetime.now()
                membership_data['months_as_member'] = ((today - membership_data['join_date']).dt.days / 30).astype(int)
                
                # Create cohort retention visualization
                cohort_bins = [0, 3, 6, 12, 24, 36, float('inf')]
                cohort_labels = ['0-3 months', '3-6 months', '6-12 months', '1-2 years', '2-3 years', '3+ years']
                
                membership_data['tenure_cohort'] = pd.cut(
                    membership_data['months_as_member'], 
                    bins=cohort_bins, 
                    labels=cohort_labels
                )
                
                cohort_counts = membership_data['tenure_cohort'].value_counts().sort_index()
                
                fig = px.bar(
                    x=cohort_counts.index,
                    y=cohort_counts.values,
                    labels={'x': 'Membership Tenure', 'y': 'Number of Members'},
                    title='Membership Retention by Tenure',
                    color=cohort_counts.values,
                    color_continuous_scale='Blues'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate retention metrics
                if 'renewal_date' in membership_data.columns:
                    expired = membership_data[membership_data['renewal_date'] < today]
                    active = membership_data[membership_data['renewal_date'] >= today]
                    
                    retention_rate = len(active) / (len(active) + len(expired)) * 100 if (len(active) + len(expired)) > 0 else 0
                    
                    st.metric("Overall Retention Rate", f"{retention_rate:.1f}%")
                    
                    # Show retention by membership type if available
                    if 'membership_type' in membership_data.columns:
                        st.subheader("Retention by Membership Type")
                        
                        membership_types = membership_data['membership_type'].unique()
                        retention_by_type = {}
                        
                        for membership_type in membership_types:
                            type_members = membership_data[membership_data['membership_type'] == membership_type]
                            type_active = type_members[type_members['renewal_date'] >= today]
                            type_retention = len(type_active) / len(type_members) * 100 if len(type_members) > 0 else 0
                            retention_by_type[membership_type] = type_retention
                        
                        retention_df = pd.DataFrame({
                            'Membership Type': list(retention_by_type.keys()),
                            'Retention Rate (%)': list(retention_by_type.values())
                        })
                        
                        fig = px.bar(
                            retention_df,
                            x='Membership Type',
                            y='Retention Rate (%)',
                            color='Retention Rate (%)',
                            color_continuous_scale='Blues',
                            title='Retention Rate by Membership Type'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            
            # Engagement analysis
            st.subheader("Engagement Analysis")
            
            if 'engagement_score' in membership_data.columns:
                # Create histogram of engagement scores
                fig = px.histogram(
                    membership_data,
                    x='engagement_score',
                    nbins=20,
                    title='Distribution of Member Engagement Scores',
                    color_discrete_sequence=['#3366CC']
                )
                
                fig.update_layout(
                    xaxis_title='Engagement Score',
                    yaxis_title='Number of Members'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show engagement by membership type if available
                if 'membership_type' in membership_data.columns:
                    engagement_by_type = membership_data.groupby('membership_type')['engagement_score'].mean().sort_values(ascending=False)
                    
                    fig = px.bar(
                        x=engagement_by_type.index,
                        y=engagement_by_type.values,
                        labels={'x': 'Membership Type', 'y': 'Average Engagement Score'},
                        title='Average Engagement by Membership Type',
                        color=engagement_by_type.values,
                        color_continuous_scale='Blues'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Value enhancement opportunities
            st.subheader("Value Enhancement Opportunities")
            
            # Generate value enhancement recommendations based on data
            value_enhancements = []
            
            if 'engagement_level' in membership_data.columns and 'membership_type' in membership_data.columns:
                # Find membership types with lower engagement
                engagement_by_type = membership_data.groupby('membership_type')['engagement_score'].mean().sort_values()
                lower_engaged_types = engagement_by_type.head(2).index.tolist()
                
                for membership_type in lower_engaged_types:
                    value_enhancements.append(f"**{membership_type} Membership Enhancement**: Members with this plan show lower engagement. Consider adding specialized resources or networking opportunities specific to this segment.")
            
            if 'industry' in membership_data.columns:
                # Identify top industries for targeted value-adds
                industry_counts = membership_data['industry'].value_counts().head(3)
                for industry, count in industry_counts.items():
                    value_enhancements.append(f"**{industry} Industry Resources**: With {count} members in this industry, consider developing specialized resources, events, or partnerships for this sector.")
            
            # General value enhancement ideas
            general_enhancements = [
                "**Enhanced Networking**: Implement facilitated networking sessions to connect members with similar interests or complementary capabilities.",
                "**Resource Library**: Develop a curated resource library with tools, templates, and guides relevant to social innovation.",
                "**Mentorship Program**: Create a structured mentorship program matching experienced members with those seeking guidance.",
                "**Learning Opportunities**: Offer exclusive workshops or webinars on topics relevant to member needs and interests.",
                "**Success Showcasing**: Develop a systematic approach to showcasing member successes and amplifying their impact stories."
            ]
            
            # Combine specific and general recommendations
            all_enhancements = value_enhancements + general_enhancements
            
            # Display recommendations
            for i, enhancement in enumerate(all_enhancements[:6]):  # Limit to reasonable number
                st.write(f"{i+1}. {enhancement}")
            
            # Member acquisition strategy
            st.subheader("Member Acquisition Strategy")
            
            # Map of potential source channels
            acquisition_channels = [
                {"channel": "Partner Referrals", "potential": 8, "cost": 3, "effort": 4},
                {"channel": "Events & Workshops", "potential": 7, "cost": 6, "effort": 7},
                {"channel": "Digital Marketing", "potential": 6, "cost": 7, "effort": 6},
                {"channel": "Member Referrals", "potential": 9, "cost": 2, "effort": 5},
                {"channel": "Community Outreach", "potential": 7, "cost": 5, "effort": 8},
                {"channel": "Content Marketing", "potential": 6, "cost": 4, "effort": 7}
            ]
            
            # Convert to DataFrame
            channels_df = pd.DataFrame(acquisition_channels)
            
            # Create bubble chart for acquisition strategies
            fig = px.scatter(
                channels_df,
                x="effort",
                y="cost",
                size="potential",
                color="potential",
                hover_name="channel",
                size_max=60,
                color_continuous_scale="Blues",
                title="Member Acquisition Channel Analysis"
            )
            
            fig.update_layout(
                xaxis_title="Effort Required (1-10)",
                yaxis_title="Cost Level (1-10)",
                coloraxis_colorbar_title="Potential (1-10)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Provide specific acquisition strategies
            st.markdown("""
            **Recommended Acquisition Priorities:**
            
            1. **Member Referral Program**: Develop a structured referral program with incentives for existing members who bring in new organizations.
            
            2. **Partner Network Activation**: Leverage existing partnerships to identify and introduce potential new members.
            
            3. **Targeted Content Strategy**: Create valuable content addressing specific pain points of target member segments.
            
            4. **Strategic Event Programming**: Design events that showcase the value of membership to potential members.
            
            5. **Community Engagement**: Participate in relevant community initiatives to build relationships with potential members.
            """)
    
    with tab3:
        st.header("Partnership Insights")
        
        if 'partnership_data' not in data_dict:
            st.info("No partnership data available. Please upload partnership data from the main page.")
        else:
            partnership_data = data_dict['partnership_data']
            
            # Partnership value analysis
            st.subheader("Partnership Value Analysis")
            
            if 'value_contribution' in partnership_data.columns and 'partnership_type' in partnership_data.columns:
                # Calculate average value by partnership type
                value_by_type = partnership_data.groupby('partnership_type')['value_contribution'].mean().sort_values(ascending=False)
                
                fig = px.bar(
                    x=value_by_type.index,
                    y=value_by_type.values,
                    labels={'x': 'Partnership Type', 'y': 'Average Value Contribution'},
                    title='Average Value Contribution by Partnership Type',
                    color=value_by_type.values,
                    color_continuous_scale='Greens'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Partnership performance matrix
            st.subheader("Partnership Performance Matrix")
            
            if 'effectiveness_score' in partnership_data.columns and 'value_contribution' in partnership_data.columns:
                # Create a scatter plot of effectiveness vs value
                # Create a copy for safe manipulation
                plot_data = partnership_data.copy()
                
                # Ensure partnership_duration is positive for plotting
                if 'partnership_duration' in plot_data.columns:
                    # Use absolute value to ensure positive values for size
                    plot_data['plot_duration'] = plot_data['partnership_duration'].abs()
                    size_col = 'plot_duration'
                else:
                    size_col = None
                
                fig = px.scatter(
                    plot_data,
                    x='effectiveness_score',
                    y='value_contribution',
                    color='partnership_type' if 'partnership_type' in plot_data.columns else None,
                    size=size_col,
                    hover_name='name',
                    title='Partnership Effectiveness vs Value',
                    labels={
                        'effectiveness_score': 'Effectiveness Score',
                        'value_contribution': 'Value Contribution',
                        'plot_duration': 'Partnership Duration (days)',
                        'partnership_type': 'Partnership Type',
                        'partnership_duration': 'Duration (days)'
                    }
                )
                
                # Add quadrant lines and labels
                mid_effectiveness = partnership_data['effectiveness_score'].median()
                mid_value = partnership_data['value_contribution'].median()
                
                fig.add_hline(
                    y=mid_value,
                    line_width=1,
                    line_dash="dash",
                    line_color="grey"
                )
                
                fig.add_vline(
                    x=mid_effectiveness,
                    line_width=1,
                    line_dash="dash",
                    line_color="grey"
                )
                
                # Add annotations for quadrants
                fig.add_annotation(
                    x=partnership_data['effectiveness_score'].max() * 0.9,
                    y=partnership_data['value_contribution'].max() * 0.9,
                    text="STAR<br>High Value, High Effectiveness",
                    showarrow=False,
                    font=dict(size=10, color="green")
                )
                
                fig.add_annotation(
                    x=partnership_data['effectiveness_score'].min() * 1.1,
                    y=partnership_data['value_contribution'].max() * 0.9,
                    text="POTENTIAL<br>High Value, Low Effectiveness",
                    showarrow=False,
                    font=dict(size=10, color="orange")
                )
                
                fig.add_annotation(
                    x=partnership_data['effectiveness_score'].max() * 0.9,
                    y=partnership_data['value_contribution'].min() * 1.1,
                    text="EFFICIENT<br>Low Value, High Effectiveness",
                    showarrow=False,
                    font=dict(size=10, color="blue")
                )
                
                fig.add_annotation(
                    x=partnership_data['effectiveness_score'].min() * 1.1,
                    y=partnership_data['value_contribution'].min() * 1.1,
                    text="REVIEW<br>Low Value, Low Effectiveness",
                    showarrow=False,
                    font=dict(size=10, color="red")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display partnership strategies for each quadrant
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **STAR Partnerships (High Value, High Effectiveness)**
                    - Invest in deepening these relationships
                    - Explore expansion opportunities
                    - Document success factors for replication
                    """)
                    
                    st.markdown("""
                    **POTENTIAL Partnerships (High Value, Low Effectiveness)**
                    - Conduct partnership reviews to identify issues
                    - Realign expectations and objectives
                    - Implement structured communication plan
                    """)
                
                with col2:
                    st.markdown("""
                    **EFFICIENT Partnerships (Low Value, High Effectiveness)**
                    - Identify value enhancement opportunities
                    - Consider strategic expansion
                    - Apply successful elements to other partnerships
                    """)
                    
                    st.markdown("""
                    **REVIEW Partnerships (Low Value, Low Effectiveness)**
                    - Evaluate strategic alignment
                    - Consider restructuring or sunsetting
                    - Capture lessons learned
                    """)
            
            # Partnership gap analysis
            st.subheader("Partnership Gap Analysis")
            
            # Define important partnership categories and current coverage
            partnership_categories = [
                {"category": "Funding & Financial Support", "importance": 9, "current_coverage": 7},
                {"category": "Program Delivery & Implementation", "importance": 8, "current_coverage": 6},
                {"category": "Knowledge & Expertise", "importance": 7, "current_coverage": 8},
                {"category": "Network Access", "importance": 8, "current_coverage": 5},
                {"category": "Technology & Innovation", "importance": 6, "current_coverage": 4},
                {"category": "Space & Physical Resources", "importance": 7, "current_coverage": 7},
                {"category": "Marketing & Promotion", "importance": 6, "current_coverage": 5},
                {"category": "Research & Development", "importance": 5, "current_coverage": 3}
            ]
            
            # Calculate gap
            for category in partnership_categories:
                category["gap"] = category["importance"] - category["current_coverage"]
            
            # Sort by gap size (descending)
            partnership_categories.sort(key=lambda x: x["gap"], reverse=True)
            
            # Convert to DataFrame
            gap_df = pd.DataFrame(partnership_categories)
            
            # Create gap analysis chart
            fig = px.bar(
                gap_df,
                x="category",
                y=["current_coverage", "gap"],
                title="Partnership Coverage Gap Analysis",
                labels={"value": "Score (1-10)", "category": "Partnership Category", "variable": "Metric"},
                color_discrete_map={"current_coverage": "green", "gap": "red"},
                barmode="stack"
            )
            
            fig.update_layout(legend_title="")
            fig.for_each_trace(lambda t: t.update(name="Current Coverage" if t.name == "current_coverage" else "Gap"))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Partnership development recommendations
            st.subheader("Partnership Development Priorities")
            
            # Get top 3 gap areas for targeted recommendations
            top_gaps = gap_df.sort_values("gap", ascending=False).head(3)["category"].tolist()
            
            st.markdown(f"""
            **Based on gap analysis, prioritize developing partnerships in:**
            
            1. **{top_gaps[0]}**: Target organizations with strong capabilities in this area to address critical needs.
            
            2. **{top_gaps[1]}**: Strengthen existing partnerships or develop new relationships to enhance capabilities.
            
            3. **{top_gaps[2]}**: Explore innovative partnership models to address this gap while minimizing resource requirements.
            """)
            
            # Partnership opportunity mapping
            st.subheader("Partnership Opportunity Map")
            
            # Create an opportunity matrix based on focus areas and partnership types
            opportunity_data = {
                "focus_area": ["Education", "Social Justice", "Environment", "Technology", "Healthcare"],
                "funding": [7, 8, 9, 6, 7],
                "program_collaboration": [9, 7, 8, 8, 6],
                "resource_sharing": [8, 7, 6, 9, 7],
                "strategic_alliance": [7, 9, 8, 7, 8]
            }
            
            opportunity_df = pd.DataFrame(opportunity_data)
            opportunity_df = opportunity_df.set_index("focus_area")
            
            # Create heatmap
            fig = px.imshow(
                opportunity_df.values,
                x=opportunity_df.columns,
                y=opportunity_df.index,
                color_continuous_scale="Greens",
                title="Partnership Opportunity Heat Map",
                labels=dict(x="Partnership Type", y="Focus Area", color="Opportunity Score")
            )
            
            fig.update_layout(
                xaxis_title="Partnership Type",
                yaxis_title="Focus Area"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Opportunity Scoring Factors:**
            - Alignment with CSI strategic objectives
            - Market need and demand
            - Potential impact and value creation
            - Resource availability and requirements
            - Existing network and connections
            
            *Note: Higher scores (darker green) indicate areas with greater partnership potential.*
            """)
    
    with tab4:
        st.header("Program Insights")
        
        if 'program_data' not in data_dict:
            st.info("No program data available. Please upload program data from the main page.")
        else:
            program_data = data_dict['program_data']
            
            # Program performance analysis
            st.subheader("Program Performance Analysis")
            
            if 'performance_score' in program_data.columns:
                # Create histogram of performance scores
                fig = px.histogram(
                    program_data,
                    x='performance_score',
                    nbins=20,
                    title='Distribution of Program Performance Scores',
                    color_discrete_sequence=['#3366CC']
                )
                
                fig.update_layout(
                    xaxis_title='Performance Score',
                    yaxis_title='Number of Programs'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show performance by program type if available
                if 'program_type' in program_data.columns:
                    performance_by_type = program_data.groupby('program_type')['performance_score'].mean().sort_values(ascending=False)
                    
                    fig = px.bar(
                        x=performance_by_type.index,
                        y=performance_by_type.values,
                        labels={'x': 'Program Type', 'y': 'Average Performance Score'},
                        title='Average Performance by Program Type',
                        color=performance_by_type.values,
                        color_continuous_scale='Blues'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Program ROI analysis
            st.subheader("Program ROI Analysis")
            
            if 'budget' in program_data.columns and 'expenses' in program_data.columns:
                # Calculate ROI metrics
                if 'enrollment_rate' in program_data.columns and 'capacity' in program_data.columns:
                    # Calculate cost per participant
                    program_data['participants'] = program_data['capacity'] * program_data['enrollment_rate']
                    program_data['cost_per_participant'] = program_data['expenses'] / program_data['participants']
                    
                    # For programs with zero participants, set cost_per_participant to expenses
                    program_data.loc[program_data['participants'] == 0, 'cost_per_participant'] = program_data['expenses']
                    
                    # Remove infinite or unreasonably high values
                    program_data = program_data[program_data['cost_per_participant'] < 10000]
                    
                    # Sort by cost per participant
                    roi_data = program_data.sort_values('cost_per_participant').head(10)
                    
                    # Create bar chart of cost per participant
                    fig = px.bar(
                        roi_data,
                        x='name',
                        y='cost_per_participant',
                        color='program_type' if 'program_type' in roi_data.columns else None,
                        title='Cost per Participant by Program (Top 10 Most Efficient)',
                        labels={
                            'name': 'Program Name',
                            'cost_per_participant': 'Cost per Participant ($)',
                            'program_type': 'Program Type'
                        }
                    )
                    
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Budget utilization
                program_data['budget_utilization'] = (program_data['expenses'] / program_data['budget'] * 100).round(1)
                
                # Create histogram of budget utilization
                fig = px.histogram(
                    program_data,
                    x='budget_utilization',
                    nbins=20,
                    range_x=[0, 200],  # Limit range to 0-200%
                    title='Distribution of Budget Utilization (%)',
                    color_discrete_sequence=['#3366CC']
                )
                
                fig.add_vline(
                    x=100,
                    line_width=2,
                    line_dash="dash",
                    line_color="red"
                )
                
                fig.update_layout(
                    xaxis_title='Budget Utilization (%)',
                    yaxis_title='Number of Programs'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Program portfolio analysis
            st.subheader("Program Portfolio Analysis")
            
            if 'program_type' in program_data.columns and 'target_audience' in program_data.columns:
                # Create a cross-tabulation of program types and target audiences
                portfolio_matrix = pd.crosstab(
                    program_data['program_type'], 
                    program_data['target_audience']
                )
                
                # Convert to probabilities for better visualization
                portfolio_norm = portfolio_matrix.div(portfolio_matrix.sum().sum())
                
                # Create heatmap
                fig = px.imshow(
                    portfolio_norm.values,
                    x=portfolio_norm.columns,
                    y=portfolio_norm.index,
                    color_continuous_scale="Blues",
                    title="Program Portfolio Coverage",
                    labels=dict(x="Target Audience", y="Program Type", color="Relative Coverage")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Identify portfolio gaps
                st.markdown("**Program Portfolio Gaps:**")
                
                # Find cells with zero or low values
                gaps = []
                for i, program_type in enumerate(portfolio_norm.index):
                    for j, audience in enumerate(portfolio_norm.columns):
                        if portfolio_norm.iloc[i, j] == 0:
                            gaps.append(f"- No {program_type} programs for {audience}")
                        elif portfolio_norm.iloc[i, j] < 0.05:  # Very low coverage
                            gaps.append(f"- Limited {program_type} programming for {audience}")
                
                # Display top gaps (limit to avoid overwhelming)
                for gap in gaps[:5]:
                    st.write(gap)
            
            # Program innovation opportunities
            st.subheader("Program Innovation Opportunities")
            
            # Create a framework for program innovation assessment
            innovation_areas = [
                {"area": "Digital Transformation", "market_demand": 9, "capability_fit": 7, "resource_req": 6},
                {"area": "Climate Action", "market_demand": 8, "capability_fit": 8, "resource_req": 7},
                {"area": "Social Enterprise Acceleration", "market_demand": 8, "capability_fit": 9, "resource_req": 5},
                {"area": "Inclusive Leadership", "market_demand": 7, "capability_fit": 8, "resource_req": 4},
                {"area": "Cross-sector Collaboration", "market_demand": 8, "capability_fit": 9, "resource_req": 5},
                {"area": "Impact Measurement", "market_demand": 7, "capability_fit": 6, "resource_req": 7},
                {"area": "Community Resilience", "market_demand": 7, "capability_fit": 7, "resource_req": 6}
            ]
            
            # Calculate an opportunity score (higher is better)
            # Formula: (market_demand + capability_fit) - resource_req
            for area in innovation_areas:
                area["opportunity_score"] = (area["market_demand"] + area["capability_fit"]) - area["resource_req"]
            
            # Sort by opportunity score (descending)
            innovation_areas.sort(key=lambda x: x["opportunity_score"], reverse=True)
            
            # Convert to DataFrame
            innovation_df = pd.DataFrame(innovation_areas)
            
            # Create opportunity score chart
            fig = px.bar(
                innovation_df,
                x="area",
                y="opportunity_score",
                title="Program Innovation Opportunity Scores",
                labels={"area": "Innovation Area", "opportunity_score": "Opportunity Score"},
                color="opportunity_score",
                color_continuous_scale="Blues"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed metrics for top opportunities
            st.markdown("**Top Program Innovation Opportunities:**")
            
            for i, area in enumerate(innovation_areas[:3]):
                st.markdown(f"""
                **{i+1}. {area['area']}**
                - Market Demand: {area['market_demand']}/10
                - Capability Fit: {area['capability_fit']}/10
                - Resource Requirements: {area['resource_req']}/10 (lower is better)
                - Opportunity Score: {area['opportunity_score']}
                """)
            
            # Program development recommendations
            st.subheader("Program Development Recommendations")
            
            st.markdown("""
            **Based on the analysis, consider these program development strategies:**
            
            1. **Low-Resource Impact Programs**: Prioritize development of high-impact programs that require minimal resource investment, such as:
               - Peer learning circles
               - Digital resource libraries
               - Community-led workshops
               - Mentorship matching platforms
            
            2. **Portfolio Optimization**: For each program in the portfolio, identify one of these strategic actions:
               - Scale (high-performing programs with growth potential)
               - Improve (promising programs with performance gaps)
               - Maintain (stable programs serving specific needs)
               - Sunset (underperforming programs with limited strategic value)
            
            3. **Modular Program Design**: Create program "building blocks" that can be combined and customized for different audiences, reducing development overhead while maintaining relevance.
            
            4. **Partner-Powered Programming**: Develop a framework for co-creating and delivering programs with strategic partners, leveraging external resources while providing unique value.
            
            5. **Impact Measurement Standardization**: Implement consistent impact measurement across all programs to better evaluate ROI and inform resource allocation.
            """)

if __name__ == "__main__":
    app()
