import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from utils.visualizer import plot_content_calendar
from utils.content_generator import (
    generate_content_ideas, 
    generate_content_calendar, 
    generate_social_media_post, 
    generate_email_newsletter
)

def app():
    st.title("Content Calendar Management")
    
    # Initialize or load content calendar data
    if 'content_calendar' not in st.session_state:
        st.session_state.content_calendar = None
    
    # Create tabs for different content management views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Calendar Overview", 
        "Content Generation", 
        "Social Media Posts",
        "Email Newsletters"
    ])
    
    with tab1:
        st.header("Content Calendar Overview")
        
        if st.session_state.content_calendar is None:
            st.info("No content calendar data available. You can generate content ideas in the 'Content Generation' tab or upload content data from the main page.")
        else:
            content_data = st.session_state.content_calendar
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_content = len(content_data)
                st.metric("Total Content Items", total_content)
                
            with col2:
                # Calculate content by status
                if 'status' in content_data.columns:
                    published_count = content_data[content_data['status'] == 'Published'].shape[0]
                    st.metric("Published Items", published_count)
                else:
                    st.metric("Published Items", "N/A")
                
            with col3:
                # Calculate upcoming content (next 30 days)
                today = datetime.now()
                if 'publish_date' in content_data.columns:
                    upcoming = content_data[
                        (content_data['publish_date'] > today) & 
                        (content_data['publish_date'] <= today + timedelta(days=30))
                    ].shape[0]
                    st.metric("Upcoming (30 Days)", upcoming)
                else:
                    st.metric("Upcoming (30 Days)", "N/A")
                
            with col4:
                # Calculate average engagement if available
                if 'engagement_score' in content_data.columns:
                    avg_engagement = round(content_data['engagement_score'].mean(), 1)
                    st.metric("Avg. Engagement", avg_engagement)
                elif 'estimated_engagement' in content_data.columns:
                    avg_engagement = round(content_data['estimated_engagement'].mean(), 1)
                    st.metric("Est. Engagement", avg_engagement)
                else:
                    st.metric("Avg. Engagement", "N/A")
            
            # Content calendar timeline visualization
            calendar_fig = plot_content_calendar(content_data)
            st.plotly_chart(calendar_fig, use_container_width=True)
            
            # Content type distribution
            if 'content_type' in content_data.columns:
                st.subheader("Content Type Distribution")
                type_counts = content_data['content_type'].value_counts().reset_index()
                type_counts.columns = ['content_type', 'count']
                
                fig = px.pie(
                    type_counts, 
                    values='count', 
                    names='content_type',
                    title='Content Types',
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Content status distribution
            if 'status' in content_data.columns:
                st.subheader("Content Status")
                status_counts = content_data['status'].value_counts().reset_index()
                status_counts.columns = ['status', 'count']
                
                fig = px.bar(
                    status_counts,
                    x='status',
                    y='count',
                    title='Content Status Distribution',
                    color='status',
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            # Channel distribution if available
            if 'channel' in content_data.columns:
                st.subheader("Channel Distribution")
                
                # Split multiple channels and count
                all_channels = []
                for channels in content_data['channel']:
                    if isinstance(channels, str):
                        channel_list = [c.strip() for c in channels.split(',')]
                        all_channels.extend(channel_list)
                
                if all_channels:
                    channel_counts = pd.Series(all_channels).value_counts().reset_index()
                    channel_counts.columns = ['channel', 'count']
                    
                    fig = px.bar(
                        channel_counts,
                        x='channel',
                        y='count',
                        title='Content Distribution by Channel',
                        color='channel',
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Content calendar table view with filters
            st.subheader("Content Calendar Table View")
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start date", 
                    value=today - timedelta(days=30),
                    help="Filter content from this date"
                )
            with col2:
                end_date = st.date_input(
                    "End date", 
                    value=today + timedelta(days=90),
                    help="Filter content until this date"
                )
            
            # Status filter
            if 'status' in content_data.columns:
                status_options = ['All'] + sorted(content_data['status'].unique().tolist())
                selected_status = st.selectbox("Filter by status", status_options)
            
            # Apply filters
            filtered_data = content_data.copy()
            
            if 'publish_date' in filtered_data.columns:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                filtered_data = filtered_data[
                    (filtered_data['publish_date'] >= start_datetime) & 
                    (filtered_data['publish_date'] <= end_datetime)
                ]
                
            if 'status' in filtered_data.columns and selected_status != 'All':
                filtered_data = filtered_data[filtered_data['status'] == selected_status]
            
            # Display filtered content calendar
            if not filtered_data.empty:
                # Select columns to display
                display_cols = ['title', 'content_type', 'publish_date', 'status', 'channel']
                
                # Add optional columns if they exist
                optional_cols = ['theme', 'target_audience', 'assigned_to', 'estimated_engagement']
                display_cols.extend([col for col in optional_cols if col in filtered_data.columns])
                
                # Ensure selected columns exist in the dataframe
                display_cols = [col for col in display_cols if col in filtered_data.columns]
                
                # Sort by publish date
                if 'publish_date' in filtered_data.columns:
                    filtered_data = filtered_data.sort_values('publish_date')
                
                st.dataframe(filtered_data[display_cols], use_container_width=True)
            else:
                st.write("No content found within the selected filters.")
            
            # Content item details viewer
            st.subheader("Content Item Details")
            
            if not filtered_data.empty and 'title' in filtered_data.columns:
                selected_content = st.selectbox(
                    "Select content item to view details",
                    options=filtered_data['title'].tolist()
                )
                
                # Get selected content details
                content_item = filtered_data[filtered_data['title'] == selected_content].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {content_item['title']}")
                    st.write(f"**Content Type:** {content_item.get('content_type', 'N/A')}")
                    st.write(f"**Theme:** {content_item.get('theme', 'N/A')}")
                    st.write(f"**Publish Date:** {content_item.get('publish_date', 'N/A')}")
                    st.write(f"**Status:** {content_item.get('status', 'N/A')}")
                    
                with col2:
                    st.write(f"**Channel:** {content_item.get('channel', 'N/A')}")
                    st.write(f"**Target Audience:** {content_item.get('target_audience', 'N/A')}")
                    st.write(f"**Assigned To:** {content_item.get('assigned_to', 'N/A')}")
                    st.write(f"**Est. Engagement:** {content_item.get('estimated_engagement', 'N/A')}")
                
                if 'description' in content_item:
                    st.write(f"**Description:**")
                    st.write(content_item['description'])
                
                if 'keywords' in content_item:
                    st.write(f"**Keywords:** {content_item['keywords']}")
                
                # Production timeline if available
                if 'content_creation_date' in content_item and 'review_date' in content_item and 'final_approval_date' in content_item:
                    st.subheader("Production Timeline")
                    
                    timeline_data = {
                        'Stage': ['Content Creation', 'Review', 'Final Approval', 'Publish'],
                        'Date': [
                            content_item['content_creation_date'],
                            content_item['review_date'],
                            content_item['final_approval_date'],
                            content_item['publish_date']
                        ]
                    }
                    
                    timeline_df = pd.DataFrame(timeline_data)
                    st.dataframe(timeline_df, use_container_width=True)
    
    with tab2:
        st.header("Content Generation")
        
        # Content idea generator
        st.subheader("Generate Content Ideas")
        
        # Number of ideas to generate
        num_ideas = st.slider(
            "Number of content ideas to generate", 
            min_value=3, 
            max_value=20, 
            value=5
        )
        
        if st.button("Generate Content Ideas"):
            with st.spinner("Generating content ideas..."):
                # Get data from session state if available
                membership_data = st.session_state.membership_data if 'membership_data' in st.session_state else None
                partnership_data = st.session_state.partnership_data if 'partnership_data' in st.session_state else None
                program_data = st.session_state.program_data if 'program_data' in st.session_state else None
                
                # Generate content ideas
                content_ideas = generate_content_ideas(
                    membership_data, 
                    partnership_data, 
                    program_data, 
                    n_ideas=num_ideas
                )
                
                if not content_ideas.empty:
                    # Store in session state for use in other tabs
                    st.session_state.content_ideas = content_ideas
                    
                    # Display generated ideas
                    st.success(f"Generated {len(content_ideas)} content ideas!")
                    
                    # Display in a dataframe
                    display_cols = ['title', 'content_type', 'theme', 'publish_date', 'channel', 'target_audience', 'status']
                    display_cols = [col for col in display_cols if col in content_ideas.columns]
                    
                    st.dataframe(content_ideas[display_cols], use_container_width=True)
                    
                    # Option to create a full content calendar
                    if st.button("Generate Full Content Calendar from Ideas"):
                        with st.spinner("Creating content calendar..."):
                            # Get date range for calendar
                            today = datetime.now()
                            calendar = generate_content_calendar(
                                content_ideas,
                                start_date=today,
                                end_date=today + timedelta(days=90)
                            )
                            
                            # Store in session state
                            st.session_state.content_calendar = calendar
                            
                            st.success("Content calendar created! View it in the Calendar Overview tab.")
                else:
                    st.error("Unable to generate content ideas. Please check the data.")
        
        # Content calendar preview (if ideas have been generated)
        if 'content_ideas' in st.session_state and st.session_state.content_ideas is not None:
            st.subheader("Content Ideas Preview")
            
            # Show detailed view for each content idea
            for i, content in st.session_state.content_ideas.iterrows():
                with st.expander(f"📝 {content['title']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Content Type:** {content['content_type']}")
                        st.write(f"**Theme:** {content['theme']}")
                        st.write(f"**Target Audience:** {content['target_audience']}")
                        st.write(f"**Channel:** {content['channel']}")
                    
                    with col2:
                        st.write(f"**Publish Date:** {content['publish_date'].strftime('%Y-%m-%d')}")
                        st.write(f"**Status:** {content['status']}")
                        st.write(f"**Est. Engagement:** {content['estimated_engagement']}/100")
                        st.write(f"**Keywords:** {content['keywords']}")
                    
                    st.write(f"**Description:**")
                    st.write(content['description'])
        
        # Manual content creation form
        st.subheader("Create Content Item Manually")
        
        with st.form("content_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Content Title")
                content_type = st.selectbox(
                    "Content Type",
                    options=[
                        "Blog Post", "Newsletter", "Social Media", 
                        "Case Study", "Member Spotlight", "Partner Spotlight",
                        "Program Announcement", "Event Announcement", "Success Story"
                    ]
                )
                theme = st.selectbox(
                    "Theme",
                    options=[
                        "Community Impact", "Innovation", "Sustainability", 
                        "Collaboration", "Member Success", "Social Enterprise", 
                        "Future of Work", "SDGs", "Diversity & Inclusion"
                    ]
                )
                description = st.text_area("Description")
            
            with col2:
                publish_date = st.date_input("Publish Date")
                channel = st.multiselect(
                    "Channel",
                    options=["Website", "Email", "LinkedIn", "Twitter", "Instagram", "Facebook", "All Channels"]
                )
                target_audience = st.selectbox(
                    "Target Audience",
                    options=[
                        "All Members", "All Partners", "General Public", 
                        "Potential Members", "Specific Member Segments", "All Audiences"
                    ]
                )
                keywords = st.text_input("Keywords (comma separated)")
            
            submit_button = st.form_submit_button("Add Content Item")
            
            if submit_button:
                # Create new content item
                new_content = {
                    'content_id': f"CNT{np.random.randint(1000, 9999)}",
                    'title': title,
                    'content_type': content_type,
                    'theme': theme,
                    'description': description,
                    'publish_date': datetime.combine(publish_date, datetime.min.time()),
                    'channel': ", ".join(channel),
                    'target_audience': target_audience,
                    'status': 'Idea',
                    'estimated_engagement': np.random.randint(50, 91),
                    'keywords': keywords
                }
                
                # Add to existing calendar or create new one
                if st.session_state.content_calendar is not None:
                    # Append to existing calendar
                    st.session_state.content_calendar = pd.concat([
                        st.session_state.content_calendar, 
                        pd.DataFrame([new_content])
                    ], ignore_index=True)
                else:
                    # Create new calendar with this item
                    st.session_state.content_calendar = pd.DataFrame([new_content])
                
                st.success("Content item added to calendar!")
    
    with tab3:
        st.header("Social Media Posts Generator")
        
        # Check if we have content ideas or calendar
        content_source = None
        
        if 'content_calendar' in st.session_state and st.session_state.content_calendar is not None:
            content_source = st.session_state.content_calendar
        elif 'content_ideas' in st.session_state and st.session_state.content_ideas is not None:
            content_source = st.session_state.content_ideas
        
        if content_source is not None:
            # Content selector
            st.subheader("Generate Social Media Posts")
            
            selected_content = st.selectbox(
                "Select content to generate social media posts for",
                options=content_source['title'].tolist()
            )
            
            # Get selected content
            content_item = content_source[content_source['title'] == selected_content].iloc[0]
            
            if st.button("Generate Social Media Posts"):
                with st.spinner("Generating posts..."):
                    # Generate social media posts
                    posts = generate_social_media_post(content_item)
                    
                    if posts:
                        st.success("Social media posts generated!")
                        
                        # Display posts by platform
                        for platform, post in posts.items():
                            with st.expander(f"{platform.capitalize()} Post"):
                                st.text_area(
                                    f"{platform.capitalize()} Content", 
                                    value=post,
                                    height=200,
                                    key=f"post_{platform}"
                                )
                                
                                if platform == "linkedin":
                                    st.markdown("""
                                    **Best posting time:** Tuesday, Wednesday, Thursday between 8-10 AM or 1-2 PM
                                    
                                    **Recommended hashtags:** Keep professional, industry-specific hashtags (3-5 max)
                                    """)
                                elif platform == "twitter":
                                    st.markdown("""
                                    **Best posting time:** Weekdays between 9 AM-12 PM
                                    
                                    **Additional tips:** Include relevant @mentions, limit to 3-4 hashtags
                                    """)
                                elif platform == "instagram":
                                    st.markdown("""
                                    **Best posting time:** Monday, Wednesday, Thursday at 11 AM-1 PM or 7-9 PM
                                    
                                    **Additional tips:** Use up to 10-15 relevant hashtags in a comment, not caption
                                    """)
                                elif platform == "facebook":
                                    st.markdown("""
                                    **Best posting time:** Weekdays at 1-4 PM
                                    
                                    **Additional tips:** Keep hashtags minimal (1-2), focus on engaging copy
                                    """)
                    else:
                        st.error("Unable to generate social media posts. Please try another content item.")
            
            # Social media content planner
            st.subheader("Social Media Content Planner")
            
            # Allow user to select platforms and view posting schedule
            platforms = st.multiselect(
                "Select platforms for content planning",
                options=["LinkedIn", "Twitter", "Instagram", "Facebook"],
                default=["LinkedIn", "Twitter"]
            )
            
            if platforms and content_source is not None:
                # Filter to content suitable for social media
                social_content = content_source[
                    (content_source['content_type'].isin([
                        'Social Media', 'Blog Post', 'Member Spotlight', 
                        'Partner Spotlight', 'Program Announcement', 'Event Announcement'
                    ])) |
                    (content_source['channel'].str.contains('|'.join(platforms), case=False, regex=True, na=False))
                ]
                
                if not social_content.empty:
                    # Create a posting calendar view
                    st.write(f"**Posting Calendar for Selected Platforms:**")
                    
                    # Group by week for viewing
                    if 'publish_date' in social_content.columns:
                        # Add week number for grouping
                        social_content['week'] = social_content['publish_date'].dt.strftime('%Y-W%W')
                        
                        # Sort by date
                        social_content = social_content.sort_values('publish_date')
                        
                        # Group by week
                        weeks = social_content['week'].unique()
                        
                        for week in weeks:
                            week_content = social_content[social_content['week'] == week]
                            with st.expander(f"Week of {week_content['publish_date'].min().strftime('%b %d, %Y')}"):
                                for idx, content in week_content.iterrows():
                                    st.write(f"**{content['publish_date'].strftime('%A, %b %d')}** - {content['title']} ({content['content_type']})")
                                    st.write(f"Channels: {content['channel']}")
                                    st.write(f"Target: {content['target_audience']}")
                                    st.write("---")
                else:
                    st.write("No suitable content found for social media planning.")
        else:
            st.info("No content data available. Please generate content ideas or create a content calendar first.")
        
        # Social media best practices guide
        with st.expander("Social Media Best Practices"):
            st.markdown("""
            ### Social Media Best Practices for CSI
            
            #### General Guidelines
            - **Voice & Tone**: Professional but approachable, mission-driven, community-focused
            - **Visual Identity**: Consistent colors, fonts, and design elements that align with CSI brand
            - **Hashtag Strategy**: Use consistent branded hashtags like #CSIcommunity #SocialInnovation
            
            #### Platform-Specific Guidelines
            
            **LinkedIn**
            - **Content Focus**: Professional updates, thought leadership, partner/member spotlights
            - **Posting Frequency**: 2-3 times per week
            - **Best Times**: Tuesday, Wednesday, Thursday (8-10 AM, 1-2 PM)
            - **Format**: Longer-form content, professional tone, industry insights
            
            **Twitter**
            - **Content Focus**: News, updates, event announcements, community engagement
            - **Posting Frequency**: 3-5 times per week
            - **Best Times**: Weekdays (9 AM-12 PM)
            - **Format**: Concise, engaging, frequent use of relevant hashtags
            
            **Instagram**
            - **Content Focus**: Visual storytelling, behind-the-scenes, community highlights
            - **Posting Frequency**: 2-3 times per week
            - **Best Times**: Monday, Wednesday, Thursday (11 AM-1 PM, 7-9 PM)
            - **Format**: High-quality visuals, stories for day-to-day updates, IGTV for longer content
            
            **Facebook**
            - **Content Focus**: Community updates, events, longer stories
            - **Posting Frequency**: 2-3 times per week
            - **Best Times**: Weekdays (1-4 PM)
            - **Format**: Mix of text, images, videos, longer-form content than other platforms
            
            #### Content Themes
            1. **Member Spotlights**: Highlighting member organizations and their impact
            2. **Partner Showcases**: Featuring partnerships and collaborative initiatives
            3. **Program Highlights**: Sharing program successes and opportunities
            4. **Community Impact**: Demonstrating CSI's community impact through stories
            5. **Educational Content**: Sharing insights on social innovation trends
            6. **Events & Announcements**: Promoting upcoming events and opportunities
            """)
    
    with tab4:
        st.header("Email Newsletter Generator")
        
        # Check if we have content ideas or calendar
        content_source = None
        
        if 'content_calendar' in st.session_state and st.session_state.content_calendar is not None:
            content_source = st.session_state.content_calendar
        elif 'content_ideas' in st.session_state and st.session_state.content_ideas is not None:
            content_source = st.session_state.content_ideas
        
        if content_source is not None:
            # Generate newsletter
            st.subheader("Generate Email Newsletter")
            
            if st.button("Generate Newsletter"):
                with st.spinner("Generating newsletter..."):
                    # Generate email newsletter from content
                    newsletter = generate_email_newsletter(content_source)
                    
                    if newsletter:
                        st.success("Newsletter generated!")
                        
                        # Display the newsletter
                        with st.expander("Newsletter Preview", expanded=True):
                            st.subheader(f"Subject: {newsletter['subject']}")
                            
                            st.markdown(f"**{newsletter['greeting']}**")
                            st.write(newsletter['intro'])
                            st.write("---")
                            
                            # Display content sections
                            for section in newsletter['content_sections']:
                                st.markdown(f"### {section['heading']}")
                                st.write(section['content'])
                                st.write(f"[{section['cta']}]({section['cta_link']})")
                                st.write("---")
                            
                            st.write(newsletter['closing'])
                            st.write("---")
                            st.write(newsletter['signature'])
                    else:
                        st.error("Unable to generate newsletter. Please check the content data.")
            
            # Newsletter templates and guides
            st.subheader("Newsletter Templates")
            
            template_options = [
                "Monthly Community Update",
                "Program Announcement",
                "Member Spotlight",
                "Partnership Showcase",
                "Event Invitation"
            ]
            
            selected_template = st.selectbox(
                "Select a newsletter template",
                options=template_options
            )
            
            with st.expander("Template Structure"):
                if selected_template == "Monthly Community Update":
                    st.markdown("""
                    ### Monthly Community Update Template
                    
                    **Subject Line:** CSI Community Update: [Month Year]
                    
                    #### Introduction
                    Brief overview of recent happenings at CSI and what's included in this newsletter.
                    
                    #### Sections
                    1. **Community Highlights**
                       - Feature 1-2 member or community stories
                       - Include images whenever possible
                    
                    2. **Upcoming Events**
                       - List 2-3 upcoming events with dates, times, and brief descriptions
                       - Include clear registration links
                    
                    3. **Program Updates**
                       - Highlight current and upcoming programs
                       - Include application deadlines if applicable
                    
                    4. **Resources & Opportunities**
                       - Share useful resources for members
                       - List partnership or funding opportunities
                    
                    #### Call to Action
                    Encourage community engagement, event registration, or resource utilization.
                    
                    #### Footer
                    Contact information, social media links, unsubscribe option.
                    """)
                elif selected_template == "Program Announcement":
                    st.markdown("""
                    ### Program Announcement Template
                    
                    **Subject Line:** Introducing [Program Name]: [Brief Value Proposition]
                    
                    #### Introduction
                    Announce the new program with a compelling opening that highlights the value to recipients.
                    
                    #### Sections
                    1. **Program Overview**
                       - Clearly explain what the program is
                       - Highlight key benefits and features
                    
                    2. **Who Should Apply**
                       - Define target audience
                       - List eligibility criteria
                    
                    3. **Key Dates & Process**
                       - Application deadline
                       - Program timeline
                       - Selection process
                    
                    4. **Success Stories** (if applicable)
                       - Share examples from similar previous programs
                    
                    #### Call to Action
                    Clear application instructions with prominent button/link.
                    
                    #### Footer
                    Contact information for questions, social media links, unsubscribe option.
                    """)
                elif selected_template == "Member Spotlight":
                    st.markdown("""
                    ### Member Spotlight Template
                    
                    **Subject Line:** Member Spotlight: [Member Organization Name] [Brief Achievement]
                    
                    #### Introduction
                    Brief introduction of the featured member and why they're being highlighted.
                    
                    #### Sections
                    1. **About the Member**
                       - Organization background
                       - Mission and vision
                       - Key team members
                    
                    2. **Success Story/Impact**
                       - Highlight recent achievement
                       - Share impact metrics
                       - Include quotes
                    
                    3. **CSI Connection**
                       - How they've utilized CSI resources/community
                       - Length of membership and involvement
                    
                    4. **What's Next**
                       - Upcoming initiatives or goals
                       - How the community can support them
                    
                    #### Call to Action
                    Encourage connecting with the featured member or nominating future spotlights.
                    
                    #### Footer
                    Contact information, social media links, unsubscribe option.
                    """)
                elif selected_template == "Partnership Showcase":
                    st.markdown("""
                    ### Partnership Showcase Template
                    
                    **Subject Line:** Partnering for Impact: CSI & [Partner Name]
                    
                    #### Introduction
                    Overview of the partnership and its significance to the CSI community.
                    
                    #### Sections
                    1. **Partnership Overview**
                       - Introduce the partner organization
                       - Explain the nature of the partnership
                       - Duration and scope
                    
                    2. **Value Creation**
                       - How this partnership benefits CSI members
                       - Specific resources or opportunities available
                    
                    3. **Success Stories**
                       - Highlight outcomes achieved through the partnership
                       - Include testimonials or case studies
                    
                    4. **Get Involved**
                       - Ways for members to engage with or benefit from the partnership
                    
                    #### Call to Action
                    Direct members to specific opportunities or resources from the partnership.
                    
                    #### Footer
                    Contact information, social media links, unsubscribe option.
                    """)
                elif selected_template == "Event Invitation":
                    st.markdown("""
                    ### Event Invitation Template
                    
                    **Subject Line:** Join Us: [Event Name] - [Date]
                    
                    #### Introduction
                    Exciting invitation with brief overview of the event and its value to recipients.
                    
                    #### Sections
                    1. **Event Details**
                       - Date, time, location (virtual or physical)
                       - Format and duration
                    
                    2. **What to Expect**
                       - Program highlights
                       - Speakers or special guests
                       - Key takeaways
                    
                    3. **Why Attend**
                       - Specific benefits to participants
                       - Networking opportunities
                    
                    4. **Registration Information**
                       - Registration deadline
                       - Cost (if any)
                       - Capacity limitations
                    
                    #### Call to Action
                    Prominent "Register Now" button with link.
                    
                    #### Footer
                    Contact information for questions, social media links, unsubscribe option.
                    """)
        else:
            st.info("No content data available. Please generate content ideas or create a content calendar first.")
        
        # Email marketing best practices
        with st.expander("Email Marketing Best Practices"):
            st.markdown("""
            ### Email Marketing Best Practices for CSI
            
            #### General Guidelines
            - **Frequency**: Monthly newsletter plus specific announcements as needed
            - **Timing**: Tuesday-Thursday mornings (10 AM) generally perform best
            - **Subject Lines**: Keep under 50 characters, focus on value to recipient
            - **Preview Text**: Use this often-overlooked space to complement your subject line
            
            #### Design Elements
            - **Mobile-First**: Ensure all emails are responsive and mobile-friendly
            - **Branding**: Consistent colors, logos, and visual identity
            - **Images**: Use high-quality, relevant images with proper alt text
            - **White Space**: Include adequate white space for better readability
            
            #### Content Strategy
            - **Segmentation**: Target content based on member types, interests, or behavior
            - **Personalization**: Use recipient names and personalized content when possible
            - **Value-First**: Focus on providing value before asking for actions
            - **Content Mix**: Blend community news, program information, and external resources
            
            #### Accessibility
            - **Alt Text**: Always include descriptive alt text for images
            - **Contrast**: Ensure text has sufficient contrast against backgrounds
            - **Text Size**: Use at least 14pt font for body text
            - **Plain Text**: Always provide a plain text alternative
            
            #### Technical Considerations
            - **Testing**: Test emails across multiple devices and email clients
            - **Analytics**: Review open rates, click rates, and engagement regularly
            - **List Management**: Regularly clean email lists and remove unengaged contacts
            - **Unsubscribe**: Make unsubscribe options clear and simple
            
            #### Compliance
            - **Permission**: Only email those who have explicitly opted in
            - **Footer Requirements**: Include physical address and unsubscribe option
            - **Privacy Policy**: Link to your privacy policy in every email
            - **Transparency**: Be clear about who the email is from
            """)

if __name__ == "__main__":
    app()
