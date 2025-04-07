import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from utils.data_processor import calculate_member_engagement
from utils.visualizer import plot_member_engagement
from utils.recommender import recommend_potential_members, find_similar_members

def app():
    st.title("Membership Management")
    
    if 'membership_data' not in st.session_state or st.session_state.membership_data is None:
        st.info("No membership data available. Please upload membership data from the main page.")
        return
    
    # Process the data to add engagement scores
    membership_data = calculate_member_engagement(st.session_state.membership_data)
    
    # Create tabs for different membership management views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Member Overview", 
        "Engagement Analysis", 
        "Member Recommendations",
        "Member Details"
    ])
    
    with tab1:
        st.header("Membership Overview")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_members = len(membership_data)
            st.metric("Total Members", total_members)
            
        with col2:
            # Calculate members about to expire (within next 30 days)
            today = datetime.now()
            if 'renewal_date' in membership_data.columns:
                expiring_soon = membership_data[
                    (membership_data['renewal_date'] > today) & 
                    (membership_data['renewal_date'] <= today + timedelta(days=30))
                ].shape[0]
                st.metric("Expiring Soon", expiring_soon)
            else:
                st.metric("Expiring Soon", "N/A")
            
        with col3:
            # Calculate average satisfaction if available
            if 'satisfaction_score' in membership_data.columns:
                avg_satisfaction = round(membership_data['satisfaction_score'].mean(), 1)
                st.metric("Avg. Satisfaction", f"{avg_satisfaction}/10")
            else:
                st.metric("Avg. Satisfaction", "N/A")
            
        with col4:
            # Calculate average engagement score if available
            if 'engagement_score' in membership_data.columns:
                avg_engagement = round(membership_data['engagement_score'].mean(), 1)
                st.metric("Avg. Engagement", f"{avg_engagement}/100")
            else:
                st.metric("Avg. Engagement", "N/A")
        
        # Membership type distribution
        if 'membership_type' in membership_data.columns:
            st.subheader("Membership Type Distribution")
            membership_counts = membership_data['membership_type'].value_counts().reset_index()
            membership_counts.columns = ['membership_type', 'count']
            
            fig = px.pie(
                membership_counts, 
                values='count', 
                names='membership_type',
                title='Membership Types',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Industry distribution if available
        if 'industry' in membership_data.columns:
            st.subheader("Industry Distribution")
            industry_counts = membership_data['industry'].value_counts().reset_index()
            industry_counts.columns = ['industry', 'count']
            
            fig = px.bar(
                industry_counts,
                x='industry',
                y='count',
                title='Member Industries',
                color='industry',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Membership duration distribution
        if 'membership_duration_days' in membership_data.columns:
            st.subheader("Membership Duration")
            
            # Convert days to years for better visualization
            membership_data['membership_years'] = membership_data['membership_duration_days'] / 365
            
            # Create histogram
            fig = px.histogram(
                membership_data,
                x='membership_years',
                nbins=20,
                title='Membership Duration (Years)',
                color_discrete_sequence=['#2E86C1']
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly joins over time
        if 'join_date' in membership_data.columns:
            st.subheader("Membership Growth Over Time")
            
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
                title='Cumulative Membership Growth',
                labels={'month_year': 'Month', 'total_members': 'Total Members'},
                markers=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Member Engagement Analysis")
        
        # Plot member engagement
        engagement_fig = plot_member_engagement(membership_data)
        st.plotly_chart(engagement_fig, use_container_width=True)
        
        # Engagement level distribution if available
        if 'engagement_level' in membership_data.columns:
            st.subheader("Engagement Level Distribution")
            
            engagement_counts = membership_data['engagement_level'].value_counts().reset_index()
            engagement_counts.columns = ['engagement_level', 'count']
            
            # Define a custom order for engagement levels
            level_order = ['High', 'Medium', 'Low', 'Very Low']
            engagement_counts['engagement_level'] = pd.Categorical(
                engagement_counts['engagement_level'], 
                categories=level_order, 
                ordered=True
            )
            engagement_counts = engagement_counts.sort_values('engagement_level')
            
            fig = px.bar(
                engagement_counts,
                x='engagement_level',
                y='count',
                title='Member Engagement Levels',
                color='engagement_level',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Members requiring attention (low engagement, high value)
        if 'engagement_score' in membership_data.columns and 'membership_type' in membership_data.columns:
            st.subheader("Members Requiring Attention")
            
            # Define high-value membership types
            high_value_types = ['Premium', 'Enterprise']
            
            # Filter for low engagement but high-value members
            attention_needed = membership_data[
                (membership_data['engagement_score'] < 50) & 
                (membership_data['membership_type'].isin(high_value_types))
            ].sort_values('engagement_score')
            
            if not attention_needed.empty:
                # Show in a data table
                st.write(f"Found {len(attention_needed)} high-value members with low engagement:")
                
                # Select columns to display
                display_cols = ['name', 'membership_type', 'engagement_score', 'days_since_interaction', 'satisfaction_score']
                display_cols = [col for col in display_cols if col in attention_needed.columns]
                
                st.dataframe(attention_needed[display_cols])
                
                # Add engagement strategies
                st.subheader("Recommended Engagement Strategies")
                st.write("""
                For members with low engagement:
                
                1. **Personal Outreach**: Schedule one-on-one check-ins with these members.
                2. **Tailored Invitations**: Invite to relevant events and programs that match their interests.
                3. **Membership Review**: Conduct a review of their membership benefits and usage.
                4. **Feedback Session**: Request detailed feedback about their experience and expectations.
                5. **Special Offers**: Provide exclusive access to premium resources or events.
                """)
            else:
                st.write("No high-value members with low engagement found.")
    
    with tab3:
        st.header("Member Recommendations")
        
        # Generate potential new member recommendations
        st.subheader("Potential New Members")
        
        # Allow user to set number of recommendations
        num_recommendations = st.slider(
            "Number of recommendations", 
            min_value=3, 
            max_value=10, 
            value=5,
            help="Select how many potential member recommendations to generate"
        )
        
        if st.button("Generate Recommendations"):
            with st.spinner("Generating potential member recommendations..."):
                potential_members = recommend_potential_members(
                    membership_data, 
                    n_recommendations=num_recommendations
                )
                
                if not potential_members.empty:
                    # Display in an expandable dataframe
                    st.dataframe(
                        potential_members[[
                            'name', 'industry', 'recommended_membership', 
                            'match_score', 'location'
                        ]], 
                        use_container_width=True
                    )
                    
                    # Show detailed view for each potential member
                    for i, member in potential_members.iterrows():
                        with st.expander(f"📋 Details for {member['name']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Contact:** {member['contact_person']}")
                                st.write(f"**Email:** {member['email']}")
                                st.write(f"**Industry:** {member['industry']}")
                                st.write(f"**Location:** {member['location']}")
                            
                            with col2:
                                st.write(f"**Match Score:** {member['match_score']}/100")
                                st.write(f"**Recommended Membership:** {member['recommended_membership']}")
                                
                            st.write("**Why this recommendation:**")
                            for reason in member['recommendation_reasons'].split(";"):
                                st.write(f"- {reason.strip()}")
                            
                            st.write("**Suggested Outreach:**")
                            st.code(
                                f"Subject: Invitation to join the Centre for Social Innovation community\n\n"
                                f"Dear {member['contact_person']},\n\n"
                                f"I hope this email finds you well. I'm reaching out from the Centre for Social Innovation "
                                f"because we believe {member['name']} would be a valuable addition to our community.\n\n"
                                f"Our {member['recommended_membership']} membership might be particularly suited to your organization's needs, "
                                f"providing access to resources, networking, and collaboration opportunities.\n\n"
                                f"Would you be available for a brief conversation to discuss potential membership benefits?\n\n"
                                f"Best regards,\n[Your Name]\nCentre for Social Innovation"
                            )
                else:
                    st.error("Unable to generate recommendations. Please check the data.")
        
        # Similar members finder
        st.subheader("Find Similar Members")
        
        # Create member selector
        if 'name' in membership_data.columns and 'member_id' in membership_data.columns:
            member_options = dict(zip(membership_data['name'], membership_data['member_id']))
            selected_member_name = st.selectbox(
                "Select a member", 
                options=list(member_options.keys()),
                help="Find members with similar characteristics to this one"
            )
            selected_member_id = member_options[selected_member_name]
            
            if st.button("Find Similar Members"):
                with st.spinner("Finding similar members..."):
                    similar_members = find_similar_members(
                        membership_data, 
                        selected_member_id, 
                        n_similar=5
                    )
                    
                    if not similar_members.empty:
                        st.write(f"Members similar to **{selected_member_name}**:")
                        
                        # Format similarity score as percentage
                        similar_members['similarity'] = (similar_members['similarity_score'] * 100).round(1).astype(str) + '%'
                        
                        # Display similar members
                        st.dataframe(
                            similar_members[['name', 'similarity']],
                            use_container_width=True
                        )
                        
                        # Suggest collaborative opportunities
                        st.subheader("Collaboration Opportunities")
                        st.write("""
                        Consider these collaborative opportunities for similar members:
                        
                        1. **Joint Events**: Facilitate introductions for potential event collaborations.
                        2. **Resource Sharing**: Identify complementary resources these members could share.
                        3. **Interest Groups**: Create a focused interest group for these members.
                        4. **Peer Mentoring**: Establish a peer mentoring relationship between similar members.
                        5. **Collaborative Projects**: Suggest specific collaborative project opportunities.
                        """)
                    else:
                        st.error("Unable to find similar members. Please check the data.")
    
    with tab4:
        st.header("Member Details")
        
        # Create search/filter options
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            if 'name' in membership_data.columns:
                search_term = st.text_input("Search by name", "")
        
        with col2:
            # Filter by membership type
            if 'membership_type' in membership_data.columns:
                membership_types = ['All'] + sorted(membership_data['membership_type'].unique().tolist())
                selected_type = st.selectbox("Filter by membership type", membership_types)
        
        # Apply filters
        filtered_data = membership_data.copy()
        
        if 'name' in filtered_data.columns and search_term:
            filtered_data = filtered_data[filtered_data['name'].str.contains(search_term, case=False)]
            
        if 'membership_type' in filtered_data.columns and selected_type != 'All':
            filtered_data = filtered_data[filtered_data['membership_type'] == selected_type]
        
        # Display filtered members
        st.subheader(f"Members ({len(filtered_data)})")
        
        if not filtered_data.empty:
            # Select columns to display in the main table
            display_cols = ['member_id', 'name', 'membership_type', 'join_date', 'renewal_date']
            
            # Add optional columns if they exist
            optional_cols = ['engagement_score', 'industry', 'satisfaction_score']
            display_cols.extend([col for col in optional_cols if col in filtered_data.columns])
            
            # Display table with only selected columns
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            st.dataframe(filtered_data[display_cols], use_container_width=True)
            
            # Member detail view
            st.subheader("Member Detail View")
            
            # Create member selector for detailed view
            member_options = dict(zip(filtered_data['name'], filtered_data.index))
            selected_member_name = st.selectbox("Select a member for detailed view", options=list(member_options.keys()))
            selected_member_idx = member_options[selected_member_name]
            
            # Get the selected member data
            member = filtered_data.iloc[selected_member_idx]
            
            # Display member details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {member['name']}")
                st.write(f"**Member ID:** {member['member_id']}")
                st.write(f"**Membership Type:** {member.get('membership_type', 'N/A')}")
                st.write(f"**Join Date:** {member.get('join_date', 'N/A')}")
                st.write(f"**Renewal Date:** {member.get('renewal_date', 'N/A')}")
                st.write(f"**Industry:** {member.get('industry', 'N/A')}")
            
            with col2:
                if 'engagement_score' in member:
                    st.write(f"**Engagement Score:** {member['engagement_score']}/100")
                if 'satisfaction_score' in member:
                    st.write(f"**Satisfaction Score:** {member['satisfaction_score']}/10")
                if 'attendance_rate' in member:
                    st.write(f"**Event Attendance Rate:** {member['attendance_rate']*100:.1f}%")
                if 'last_interaction' in member:
                    st.write(f"**Last Interaction:** {member['last_interaction'].date()}")
                if 'location' in member:
                    st.write(f"**Location:** {member['location']}")
            
            # Contact information
            st.subheader("Contact Information")
            if 'contact_person' in member and 'email' in member:
                st.write(f"**Contact Person:** {member['contact_person']}")
                st.write(f"**Email:** {member['email']}")
            else:
                st.write("No contact information available.")
            
            # Membership timeline
            st.subheader("Membership Timeline")
            
            # Create timeline events
            timeline_events = []
            
            # Add join date
            if 'join_date' in member:
                timeline_events.append({
                    'date': member['join_date'],
                    'event': 'Joined CSI',
                    'description': f"Became a {member.get('membership_type', 'member')}"
                })
            
            # Add renewal date if it's in the future
            if 'renewal_date' in member and member['renewal_date'] > datetime.now():
                timeline_events.append({
                    'date': member['renewal_date'],
                    'event': 'Membership Renewal',
                    'description': f"Renewal of {member.get('membership_type', 'membership')}"
                })
            elif 'renewal_date' in member:
                timeline_events.append({
                    'date': member['renewal_date'],
                    'event': 'Membership Expired',
                    'description': f"Renewal of {member.get('membership_type', 'membership')} needed"
                })
            
            # Add last interaction if available
            if 'last_interaction' in member:
                timeline_events.append({
                    'date': member['last_interaction'],
                    'event': 'Last Interaction',
                    'description': "Most recent engagement with CSI"
                })
            
            # Convert to DataFrame and sort by date
            if timeline_events:
                timeline_df = pd.DataFrame(timeline_events)
                timeline_df = timeline_df.sort_values('date')
                
                # Display timeline
                for _, event in timeline_df.iterrows():
                    st.write(f"**{event['date'].date()}**: {event['event']} - {event['description']}")
            else:
                st.write("No timeline events available.")
            
            # Recommendations for this member
            st.subheader("Recommendations")
            
            # Generate simple recommendations based on member data
            recommendations = []
            
            if 'renewal_date' in member and member['renewal_date'] <= datetime.now() + timedelta(days=30):
                recommendations.append("**Renewal Outreach**: This membership is expiring soon. Schedule a renewal conversation.")
            
            if 'engagement_score' in member and member['engagement_score'] < 50:
                recommendations.append("**Engagement Boost**: Member has low engagement. Consider a personalized outreach strategy.")
            
            if 'satisfaction_score' in member and member['satisfaction_score'] < 7:
                recommendations.append("**Satisfaction Check**: Member has below-average satisfaction. Schedule a feedback session.")
            
            if 'last_interaction' in member and (datetime.now() - member['last_interaction']).days > 60:
                recommendations.append("**Re-engagement**: No recent interactions. Send a personalized check-in message.")
            
            if recommendations:
                for rec in recommendations:
                    st.write(f"- {rec}")
            else:
                st.write("No specific recommendations at this time.")
        else:
            st.write("No members found with the selected filters.")

if __name__ == "__main__":
    app()
