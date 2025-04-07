import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from utils.data_processor import calculate_partnership_effectiveness
from utils.visualizer import plot_partnership_effectiveness
from utils.recommender import recommend_partnerships

def app():
    st.title("Partnership Management")
    
    if 'partnership_data' not in st.session_state or st.session_state.partnership_data is None:
        st.info("No partnership data available. Please upload partnership data from the main page.")
        return
    
    # Process the data to add effectiveness metrics
    partnership_data = calculate_partnership_effectiveness(st.session_state.partnership_data)
    
    # Create tabs for different partnership management views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Partnership Overview", 
        "Effectiveness Analysis", 
        "Partnership Recommendations",
        "Partnership Details"
    ])
    
    with tab1:
        st.header("Partnership Overview")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_partnerships = len(partnership_data)
            st.metric("Total Partnerships", total_partnerships)
            
        with col2:
            # Calculate active partnerships
            if 'status' in partnership_data.columns:
                active_partnerships = partnership_data[partnership_data['status'] == 'Active'].shape[0]
                st.metric("Active Partnerships", active_partnerships)
            else:
                st.metric("Active Partnerships", "N/A")
            
        with col3:
            # Calculate average performance if available
            if 'performance_rating' in partnership_data.columns:
                avg_performance = round(partnership_data['performance_rating'].mean(), 1)
                st.metric("Avg. Performance", f"{avg_performance}/10")
            else:
                st.metric("Avg. Performance", "N/A")
            
        with col4:
            # Calculate total value contribution if available
            if 'value_contribution' in partnership_data.columns:
                total_value = partnership_data['value_contribution'].sum()
                st.metric("Total Value", f"${total_value:,.0f}")
            else:
                st.metric("Total Value", "N/A")
        
        # Partnership type distribution
        if 'partnership_type' in partnership_data.columns:
            st.subheader("Partnership Type Distribution")
            partnership_counts = partnership_data['partnership_type'].value_counts().reset_index()
            partnership_counts.columns = ['partnership_type', 'count']
            
            fig = px.pie(
                partnership_counts, 
                values='count', 
                names='partnership_type',
                title='Partnership Types',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Partnership status distribution
        if 'status' in partnership_data.columns:
            st.subheader("Partnership Status")
            status_counts = partnership_data['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            fig = px.bar(
                status_counts,
                x='status',
                y='count',
                title='Partnership Status Distribution',
                color='status',
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Focus area distribution if available
        if 'focus_area' in partnership_data.columns:
            st.subheader("Focus Area Distribution")
            
            focus_counts = partnership_data['focus_area'].value_counts().reset_index()
            focus_counts.columns = ['focus_area', 'count']
            
            fig = px.bar(
                focus_counts,
                x='focus_area',
                y='count',
                title='Partnership Focus Areas',
                color='focus_area',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Partnership timeline
        if 'start_date' in partnership_data.columns:
            st.subheader("Partnership Timeline")
            
            # Sort partnerships by start date
            timeline_data = partnership_data.sort_values('start_date')
            
            # Create a gantt chart of partnerships
            if 'end_date' in timeline_data.columns:
                # For partnerships without an end date, use today + 1 year as placeholder
                today = datetime.now()
                timeline_data['display_end_date'] = timeline_data['end_date'].fillna(today + timedelta(days=365))
                
                fig = px.timeline(
                    timeline_data,
                    x_start='start_date',
                    x_end='display_end_date',
                    y='name',
                    color='partnership_type' if 'partnership_type' in timeline_data.columns else 'status',
                    hover_name='name',
                    title='Partnership Timeline',
                    color_discrete_sequence=px.colors.qualitative.Safe
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
                
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Partnership Effectiveness Analysis")
        
        # Plot partnership effectiveness
        effectiveness_fig = plot_partnership_effectiveness(partnership_data)
        st.plotly_chart(effectiveness_fig, use_container_width=True)
        
        # Effectiveness category distribution if available
        if 'effectiveness_category' in partnership_data.columns:
            st.subheader("Effectiveness Distribution")
            
            effectiveness_counts = partnership_data['effectiveness_category'].value_counts().reset_index()
            effectiveness_counts.columns = ['effectiveness_category', 'count']
            
            # Define a custom order for effectiveness levels
            level_order = ['High', 'Medium', 'Low', 'Very Low']
            effectiveness_counts['effectiveness_category'] = pd.Categorical(
                effectiveness_counts['effectiveness_category'], 
                categories=level_order, 
                ordered=True
            )
            effectiveness_counts = effectiveness_counts.sort_values('effectiveness_category')
            
            fig = px.bar(
                effectiveness_counts,
                x='effectiveness_category',
                y='count',
                title='Partnership Effectiveness Levels',
                color='effectiveness_category',
                color_discrete_sequence=px.colors.sequential.Greens
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance vs Value Matrix
        if 'performance_rating' in partnership_data.columns and 'value_contribution' in partnership_data.columns:
            st.subheader("Performance vs Value Matrix")
            
            fig = px.scatter(
                partnership_data,
                x='performance_rating',
                y='value_contribution',
                color='partnership_type' if 'partnership_type' in partnership_data.columns else None,
                size='partnership_duration' if 'partnership_duration' in partnership_data.columns else None,
                hover_name='name',
                title='Partnership Performance vs Value Contribution',
                labels={
                    'performance_rating': 'Performance Rating',
                    'value_contribution': 'Value Contribution ($)',
                    'partnership_type': 'Partnership Type',
                    'partnership_duration': 'Duration (days)'
                }
            )
            
            # Add quadrant lines
            mid_performance = (partnership_data['performance_rating'].max() + partnership_data['performance_rating'].min()) / 2
            mid_value = (partnership_data['value_contribution'].max() + partnership_data['value_contribution'].min()) / 2
            
            fig.add_hline(
                y=mid_value,
                line_width=1,
                line_dash="dash",
                line_color="grey"
            )
            
            fig.add_vline(
                x=mid_performance,
                line_width=1,
                line_dash="dash",
                line_color="grey"
            )
            
            # Add quadrant annotations
            fig.add_annotation(
                x=partnership_data['performance_rating'].max() * 0.9,
                y=partnership_data['value_contribution'].max() * 0.9,
                text="High Performance<br>High Value",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=partnership_data['performance_rating'].min() * 1.2,
                y=partnership_data['value_contribution'].max() * 0.9,
                text="Low Performance<br>High Value",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=partnership_data['performance_rating'].max() * 0.9,
                y=partnership_data['value_contribution'].min() * 1.2,
                text="High Performance<br>Low Value",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=partnership_data['performance_rating'].min() * 1.2,
                y=partnership_data['value_contribution'].min() * 1.2,
                text="Low Performance<br>Low Value",
                showarrow=False,
                font=dict(size=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Partnerships requiring attention (low effectiveness, high value potential)
        if 'effectiveness_score' in partnership_data.columns and 'value_contribution' in partnership_data.columns:
            st.subheader("Partnerships Requiring Attention")
            
            # Filter for low effectiveness but high-value partnerships
            attention_needed = partnership_data[
                (partnership_data['effectiveness_score'] < 6) & 
                (partnership_data['value_contribution'] > partnership_data['value_contribution'].median())
            ].sort_values('effectiveness_score')
            
            if not attention_needed.empty:
                # Show in a data table
                st.write(f"Found {len(attention_needed)} high-value partnerships with low effectiveness:")
                
                # Select columns to display
                display_cols = ['name', 'partnership_type', 'effectiveness_score', 'value_contribution', 'status']
                display_cols = [col for col in display_cols if col in attention_needed.columns]
                
                st.dataframe(attention_needed[display_cols])
                
                # Add improvement strategies
                st.subheader("Recommended Improvement Strategies")
                st.write("""
                For partnerships with low effectiveness but high value potential:
                
                1. **Partnership Review**: Schedule a partnership review meeting to identify issues.
                2. **Clear Objectives**: Redefine partnership objectives and success metrics.
                3. **Communication Plan**: Establish a regular communication schedule.
                4. **Resource Allocation**: Ensure adequate resources are allocated to support the partnership.
                5. **Value Enhancement**: Identify new ways to increase mutual value from the partnership.
                """)
            else:
                st.write("No high-value partnerships with low effectiveness found.")
    
    with tab3:
        st.header("Partnership Recommendations")
        
        # Generate potential new partnership recommendations
        st.subheader("Potential New Partnerships")
        
        # Allow user to set number of recommendations
        num_recommendations = st.slider(
            "Number of recommendations", 
            min_value=3, 
            max_value=10, 
            value=5,
            help="Select how many potential partnership recommendations to generate"
        )
        
        if st.button("Generate Partnership Recommendations"):
            with st.spinner("Generating potential partnership recommendations..."):
                membership_data = st.session_state.membership_data if 'membership_data' in st.session_state else None
                potential_partnerships = recommend_partnerships(
                    membership_data,
                    partnership_data, 
                    n_recommendations=num_recommendations
                )
                
                if not potential_partnerships.empty:
                    # Display in an expandable dataframe
                    st.dataframe(
                        potential_partnerships[[
                            'name', 'focus_area', 'recommended_partnership_type', 
                            'alignment_score', 'value_potential'
                        ]], 
                        use_container_width=True
                    )
                    
                    # Show detailed view for each potential partner
                    for i, partner in potential_partnerships.iterrows():
                        with st.expander(f"📋 Details for {partner['name']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Contact:** {partner['contact_person']}")
                                st.write(f"**Email:** {partner['email']}")
                                st.write(f"**Focus Area:** {partner['focus_area']}")
                                st.write(f"**Recommended Partnership Type:** {partner['recommended_partnership_type']}")
                            
                            with col2:
                                st.write(f"**Alignment Score:** {partner['alignment_score']}/10")
                                st.write(f"**Value Potential:** ${partner['value_potential']:,}")
                                
                            st.write("**Why this recommendation:**")
                            for reason in partner['recommendation_reasons'].split(";"):
                                st.write(f"- {reason.strip()}")
                            
                            st.write("**Suggested Outreach:**")
                            st.code(
                                f"Subject: Exploring partnership opportunities with the Centre for Social Innovation\n\n"
                                f"Dear {partner['contact_person']},\n\n"
                                f"I hope this email finds you well. I'm reaching out from the Centre for Social Innovation "
                                f"because we see great potential for collaboration between our organizations.\n\n"
                                f"We believe a {partner['recommended_partnership_type']} partnership could create significant "
                                f"value in the {partner['focus_area']} space, aligning with both our missions.\n\n"
                                f"Would you be available for a conversation to explore potential collaboration opportunities?\n\n"
                                f"Best regards,\n[Your Name]\nCentre for Social Innovation"
                            )
                else:
                    st.error("Unable to generate recommendations. Please check the data.")
        
        # Partnership optimization strategies
        st.subheader("Partnership Optimization Strategies")
        
        # Filter for active partnerships
        active_partnerships = partnership_data[partnership_data['status'] == 'Active'] if 'status' in partnership_data.columns else partnership_data
        
        if not active_partnerships.empty:
            # Group partnerships by type for type-specific strategies
            if 'partnership_type' in active_partnerships.columns:
                partnership_types = active_partnerships['partnership_type'].unique()
                
                selected_partnership_type = st.selectbox(
                    "Select partnership type for specific strategies",
                    options=['All Types'] + list(partnership_types)
                )
                
                # Filter by selected type
                if selected_partnership_type != 'All Types':
                    filtered_partnerships = active_partnerships[active_partnerships['partnership_type'] == selected_partnership_type]
                else:
                    filtered_partnerships = active_partnerships
                
                # Show optimization strategies based on partnership type
                if selected_partnership_type == 'Funding':
                    st.write("""
                    **Funding Partnership Optimization Strategies:**
                    
                    1. **Impact Reporting**: Enhance impact reporting to clearly demonstrate ROI for funders.
                    2. **Recognition Program**: Develop a comprehensive recognition program for funding partners.
                    3. **Milestone Celebrations**: Celebrate key milestones and achievements together.
                    4. **Co-creation Opportunities**: Involve funding partners in program design when appropriate.
                    5. **Long-term Planning**: Develop multi-year partnership plans for funding sustainability.
                    """)
                elif selected_partnership_type == 'Program Collaboration':
                    st.write("""
                    **Program Collaboration Optimization Strategies:**
                    
                    1. **Shared Metrics**: Establish shared success metrics and regular reporting.
                    2. **Joint Marketing**: Increase co-marketing efforts to expand reach.
                    3. **Resource Sharing**: Identify opportunities for resource sharing to maximize efficiency.
                    4. **Innovation Sessions**: Schedule quarterly innovation sessions to explore new ideas.
                    5. **Community Feedback**: Implement joint feedback mechanisms from program participants.
                    """)
                elif selected_partnership_type == 'Strategic Alliance':
                    st.write("""
                    **Strategic Alliance Optimization Strategies:**
                    
                    1. **Leadership Engagement**: Ensure regular engagement between organizational leaders.
                    2. **Joint Strategic Planning**: Include partners in relevant strategic planning sessions.
                    3. **Capability Mapping**: Map complementary capabilities and leverage them effectively.
                    4. **Knowledge Exchange**: Establish formal knowledge exchange protocols.
                    5. **Systems Integration**: Where appropriate, integrate systems for seamless collaboration.
                    """)
                elif selected_partnership_type == 'Resource Sharing':
                    st.write("""
                    **Resource Sharing Optimization Strategies:**
                    
                    1. **Resource Inventory**: Maintain an updated inventory of shareable resources.
                    2. **Efficiency Metrics**: Track and report on efficiency gains from resource sharing.
                    3. **Sharing Protocols**: Develop clear protocols for resource access and use.
                    4. **Expansion Opportunities**: Regularly identify new resource sharing opportunities.
                    5. **Member Benefits**: Create special benefits for members from shared resources.
                    """)
                else:
                    st.write("""
                    **General Partnership Optimization Strategies:**
                    
                    1. **Regular Check-ins**: Establish a cadence of partnership check-in meetings.
                    2. **Success Metrics**: Define clear, measurable success metrics for each partnership.
                    3. **Communication Plan**: Develop a structured communication plan with each partner.
                    4. **Value Assessment**: Conduct bi-annual partnership value assessments.
                    5. **Innovation Focus**: Set aside time specifically to explore new collaboration opportunities.
                    6. **Mutual Promotion**: Increase cross-promotion in respective networks.
                    7. **Feedback Mechanism**: Implement a formal feedback system for continuous improvement.
                    """)
                
                # Show list of partnerships with this type
                st.subheader(f"Active {selected_partnership_type if selected_partnership_type != 'All Types' else ''} Partnerships")
                
                # Select columns to display
                display_cols = ['name', 'focus_area', 'start_date', 'effectiveness_score', 'value_contribution']
                display_cols = [col for col in display_cols if col in filtered_partnerships.columns]
                
                st.dataframe(filtered_partnerships[display_cols], use_container_width=True)
        else:
            st.write("No active partnerships found for optimization recommendations.")
    
    with tab4:
        st.header("Partnership Details")
        
        # Create search/filter options
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            if 'name' in partnership_data.columns:
                search_term = st.text_input("Search by partner name", "")
        
        with col2:
            # Filter by status
            if 'status' in partnership_data.columns:
                status_options = ['All'] + sorted(partnership_data['status'].unique().tolist())
                selected_status = st.selectbox("Filter by status", status_options)
        
        # Apply filters
        filtered_data = partnership_data.copy()
        
        if 'name' in filtered_data.columns and search_term:
            filtered_data = filtered_data[filtered_data['name'].str.contains(search_term, case=False)]
            
        if 'status' in filtered_data.columns and selected_status != 'All':
            filtered_data = filtered_data[filtered_data['status'] == selected_status]
        
        # Display filtered partnerships
        st.subheader(f"Partnerships ({len(filtered_data)})")
        
        if not filtered_data.empty:
            # Select columns to display in the main table
            display_cols = ['partner_id', 'name', 'partnership_type', 'status', 'start_date', 'end_date']
            
            # Add optional columns if they exist
            optional_cols = ['effectiveness_score', 'focus_area', 'value_contribution']
            display_cols.extend([col for col in optional_cols if col in filtered_data.columns])
            
            # Display table with only selected columns
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            st.dataframe(filtered_data[display_cols], use_container_width=True)
            
            # Partnership detail view
            st.subheader("Partnership Detail View")
            
            # Create partnership selector for detailed view
            partner_options = dict(zip(filtered_data['name'], filtered_data.index))
            selected_partner_name = st.selectbox("Select a partnership for detailed view", options=list(partner_options.keys()))
            selected_partner_idx = partner_options[selected_partner_name]
            
            # Get the selected partnership data
            partner = filtered_data.iloc[selected_partner_idx]
            
            # Display partnership details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {partner['name']}")
                st.write(f"**Partner ID:** {partner['partner_id']}")
                st.write(f"**Partnership Type:** {partner.get('partnership_type', 'N/A')}")
                st.write(f"**Status:** {partner.get('status', 'N/A')}")
                st.write(f"**Start Date:** {partner.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {partner.get('end_date', 'N/A')}")
                st.write(f"**Focus Area:** {partner.get('focus_area', 'N/A')}")
            
            with col2:
                if 'effectiveness_score' in partner:
                    st.write(f"**Effectiveness Score:** {partner['effectiveness_score']}/10")
                if 'value_contribution' in partner:
                    st.write(f"**Value Contribution:** ${partner['value_contribution']:,}")
                if 'performance_rating' in partner:
                    st.write(f"**Performance Rating:** {partner['performance_rating']}/10")
                if 'alignment_score' in partner:
                    st.write(f"**Mission Alignment:** {partner['alignment_score']}/10")
                if 'meetings_count' in partner:
                    st.write(f"**Meetings Count:** {partner['meetings_count']}")
                if 'shared_resources' in partner:
                    st.write(f"**Shared Resources:** {partner['shared_resources']}")
            
            # Contact information
            st.subheader("Contact Information")
            if 'contact_person' in partner and 'email' in partner:
                st.write(f"**Contact Person:** {partner['contact_person']}")
                st.write(f"**Email:** {partner['email']}")
            else:
                st.write("No contact information available.")
            
            # Partnership assessment
            st.subheader("Partnership Assessment")
            
            # Create assessment based on available metrics
            assessment_items = []
            
            if 'effectiveness_score' in partner:
                effectiveness = partner['effectiveness_score']
                if effectiveness >= 8:
                    assessment_items.append("✅ **High Effectiveness**: This partnership is performing exceptionally well.")
                elif effectiveness >= 6:
                    assessment_items.append("✓ **Moderate Effectiveness**: This partnership is performing adequately but could be improved.")
                else:
                    assessment_items.append("❗ **Low Effectiveness**: This partnership needs attention to improve performance.")
            
            if 'value_contribution' in partner:
                value = partner['value_contribution']
                avg_value = filtered_data['value_contribution'].mean()
                if value > avg_value * 1.5:
                    assessment_items.append("✅ **High Value**: This partnership provides exceptional value relative to others.")
                elif value > avg_value * 0.8:
                    assessment_items.append("✓ **Moderate Value**: This partnership provides good value.")
                else:
                    assessment_items.append("❗ **Low Value**: The value contribution of this partnership could be improved.")
            
            if 'alignment_score' in partner:
                alignment = partner['alignment_score']
                if alignment >= 8:
                    assessment_items.append("✅ **Strong Alignment**: Excellent mission and goals alignment with CSI.")
                elif alignment >= 6:
                    assessment_items.append("✓ **Moderate Alignment**: Good alignment with some areas for improvement.")
                else:
                    assessment_items.append("❗ **Weak Alignment**: Mission alignment needs to be addressed.")
            
            if 'status' in partner and partner['status'] == 'Active' and 'end_date' in partner:
                try:
                    days_remaining = (partner['end_date'] - datetime.now()).days
                    if days_remaining < 0:
                        assessment_items.append("❗ **Expired**: This partnership has passed its end date and needs renewal.")
                    elif days_remaining < 90:
                        assessment_items.append(f"⚠️ **Expiring Soon**: {days_remaining} days until partnership end date. Consider renewal discussion.")
                except:
                    pass
            
            # Display assessment items
            if assessment_items:
                for item in assessment_items:
                    st.write(item)
            else:
                st.write("Insufficient data for detailed partnership assessment.")
            
            # Recommendations for this partnership
            st.subheader("Recommendations")
            
            # Generate recommendations based on partnership data
            recommendations = []
            
            if 'effectiveness_score' in partner and partner['effectiveness_score'] < 6:
                recommendations.append("**Performance Review**: Schedule a performance review to identify improvement areas.")
            
            if 'end_date' in partner and isinstance(partner['end_date'], datetime) and partner['end_date'] <= datetime.now() + timedelta(days=90):
                recommendations.append("**Renewal Planning**: Begin partnership renewal discussions.")
            
            if 'meetings_count' in partner and partner['meetings_count'] < 4:
                recommendations.append("**Increased Engagement**: Consider increasing meeting frequency to strengthen relationship.")
            
            if 'alignment_score' in partner and partner['alignment_score'] < 7:
                recommendations.append("**Strategic Alignment**: Review strategic alignment to identify shared goals and priorities.")
            
            if 'value_contribution' in partner and partner['value_contribution'] < filtered_data['value_contribution'].median():
                recommendations.append("**Value Enhancement**: Explore opportunities to increase mutual value from this partnership.")
            
            if recommendations:
                for rec in recommendations:
                    st.write(f"- {rec}")
            else:
                st.write("No specific recommendations at this time.")
        else:
            st.write("No partnerships found with the selected filters.")

if __name__ == "__main__":
    app()
