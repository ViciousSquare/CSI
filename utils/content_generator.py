import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

def generate_content_ideas(membership_data, partnership_data, program_data, n_ideas=5):
    """
    Generate content ideas based on data from memberships, partnerships, and programs
    
    Parameters:
    - membership_data: DataFrame with membership information
    - partnership_data: DataFrame with partnership information
    - program_data: DataFrame with program information
    - n_ideas: Number of content ideas to generate
    
    Returns:
    - DataFrame with content ideas
    """
    # Content types
    content_types = [
        "Blog Post", "Newsletter", "Social Media", "Case Study", 
        "Email Campaign", "Member Spotlight", "Partner Spotlight",
        "Program Announcement", "Success Story", "Event Announcement"
    ]
    
    # Content themes
    content_themes = [
        "Community Impact", "Innovation", "Sustainability", "Collaboration",
        "Member Success", "Social Enterprise", "Future of Work", "SDGs",
        "Emerging Trends", "Diversity & Inclusion", "Social Innovation"
    ]
    
    # Generate potential content ideas
    content_ideas = []
    today = datetime.now()
    
    # Analyze available data to inform content ideas
    popular_industries = []
    if membership_data is not None and 'industry' in membership_data.columns:
        popular_industries = membership_data['industry'].value_counts().head(3).index.tolist()
    
    active_programs = []
    if program_data is not None:
        # Get names of active or upcoming programs
        active_programs = program_data[
            (program_data['status'] == 'Active') | (program_data['status'] == 'Planned')
        ]['name'].tolist() if 'status' in program_data.columns else program_data['name'].tolist()[:3]
    
    successful_partnerships = []
    if partnership_data is not None and 'name' in partnership_data.columns:
        # Get names of active partnerships with high ratings if available
        if 'status' in partnership_data.columns and 'performance_rating' in partnership_data.columns:
            successful_partnerships = partnership_data[
                (partnership_data['status'] == 'Active') & 
                (partnership_data['performance_rating'] >= 8)
            ]['name'].tolist()
        else:
            successful_partnerships = partnership_data['name'].tolist()[:3]
    
    # Title templates
    title_templates = [
        "How {0} is Transforming Social Innovation",
        "The Future of {0} in Social Impact",
        "{0}: A Case Study in Successful Social Enterprise",
        "5 Ways {0} is Changing the Social Innovation Landscape",
        "Spotlight on {0}: Driving Sustainable Change",
        "The Impact of {0} on Community Development",
        "Innovation Spotlight: {0}",
        "Collaborating for Change: The Story of {0}",
        "Meet the Change-Makers: {0}",
        "How {0} Achieves Social Impact Goals"
    ]
    
    for i in range(n_ideas):
        # Select content type and theme
        content_type = np.random.choice(content_types)
        theme = np.random.choice(content_themes)
        
        # Decide on the content subject
        subject_type = np.random.choice(['program', 'member', 'partner', 'theme', 'industry'])
        
        if subject_type == 'program' and active_programs:
            subject = np.random.choice(active_programs)
        elif subject_type == 'partner' and successful_partnerships:
            subject = np.random.choice(successful_partnerships)
        elif subject_type == 'industry' and popular_industries:
            subject = np.random.choice(popular_industries)
        elif subject_type == 'theme':
            subject = theme
        else:
            # Default to a generic subject
            subject = "Social Innovation in Practice"
        
        # Generate title based on template
        title_template = np.random.choice(title_templates)
        title = title_template.format(subject)
        
        # Generate a brief description
        descriptions = [
            f"An in-depth look at how {subject} is making a difference in the social innovation space.",
            f"Exploring the impact of {subject} on communities and the future of social enterprise.",
            f"Highlighting the success and learnings from {subject} for the CSI community.",
            f"A thought leadership piece on {subject} and its relevance to social innovation.",
            f"Showcasing the collaborative approach of {subject} in driving sustainable change."
        ]
        description = np.random.choice(descriptions)
        
        # Determine target audience
        if content_type == "Member Spotlight":
            target_audience = "All Members"
        elif content_type == "Partner Spotlight":
            target_audience = "Partners, Members"
        elif content_type == "Program Announcement":
            target_audience = "Potential Participants, Members"
        else:
            target_audience = np.random.choice([
                "All Members", "All Partners", "General Public", 
                "Potential Members", "Specific Member Segments", "All Audiences"
            ])
        
        # Determine channel based on content type
        if content_type == "Blog Post":
            channel = "Website, Social Media"
        elif content_type == "Newsletter":
            channel = "Email"
        elif content_type == "Social Media":
            channel = np.random.choice(["LinkedIn", "Twitter", "Instagram", "Facebook"])
        elif content_type == "Email Campaign":
            channel = "Email"
        else:
            channel = np.random.choice([
                "Website", "Email", "LinkedIn, Twitter", 
                "All Social Media", "Website, Email", "All Channels"
            ])
        
        # Assign publish date (between now and 60 days in the future)
        publish_date = today + timedelta(days=np.random.randint(1, 61))
        
        # Determine status based on publish date
        if publish_date < today + timedelta(days=7):
            status = "Draft"
        elif publish_date < today + timedelta(days=14):
            status = "In Progress"
        else:
            status = "Idea"
        
        # Estimate engagement level
        if content_type in ["Member Spotlight", "Partner Spotlight", "Success Story"]:
            estimated_engagement = np.random.randint(70, 101)
        elif content_type in ["Program Announcement", "Event Announcement"]:
            estimated_engagement = np.random.randint(60, 91)
        else:
            estimated_engagement = np.random.randint(40, 81)
        
        # Add keywords based on subject and theme
        keywords = []
        keywords.append(theme.lower())
        keywords.append("social innovation")
        
        if subject_type == 'industry':
            keywords.append(subject.lower())
        
        if theme == "Sustainability":
            keywords.extend(["sustainable development", "SDGs"])
        elif theme == "Innovation":
            keywords.extend(["innovation", "technology"])
        elif theme == "Collaboration":
            keywords.extend(["partnership", "collaboration"])
        
        # Add content idea to list
        content_ideas.append({
            'content_id': f"CNT{i+1:03d}",
            'title': title,
            'content_type': content_type,
            'theme': theme,
            'description': description,
            'target_audience': target_audience,
            'channel': channel,
            'publish_date': publish_date,
            'status': status,
            'estimated_engagement': estimated_engagement,
            'keywords': ", ".join(keywords)
        })
    
    # Convert to DataFrame
    ideas_df = pd.DataFrame(content_ideas)
    
    return ideas_df

def generate_content_calendar(content_ideas, start_date=None, end_date=None):
    """
    Generate a content calendar based on content ideas
    
    Parameters:
    - content_ideas: DataFrame with content ideas
    - start_date: Start date for the calendar (default: today)
    - end_date: End date for the calendar (default: 90 days from start)
    
    Returns:
    - DataFrame with a structured content calendar
    """
    if content_ideas is None or len(content_ideas) == 0:
        return pd.DataFrame()
    
    # Set default dates if not provided
    today = datetime.now()
    if start_date is None:
        start_date = today
    if end_date is None:
        end_date = start_date + timedelta(days=90)
    
    # Create a copy of the content ideas
    calendar_df = content_ideas.copy()
    
    # Sort by publish date
    if 'publish_date' in calendar_df.columns:
        calendar_df = calendar_df.sort_values('publish_date')
    
    # Add scheduling and production information
    if 'publish_date' in calendar_df.columns:
        # Calculate production timeline
        calendar_df['content_creation_date'] = calendar_df['publish_date'] - timedelta(days=14)
        calendar_df['review_date'] = calendar_df['publish_date'] - timedelta(days=7)
        calendar_df['final_approval_date'] = calendar_df['publish_date'] - timedelta(days=3)
    
    # Add responsible person (simulated)
    team_members = ["Alex", "Jordan", "Taylor", "Morgan", "Casey"]
    calendar_df['assigned_to'] = np.random.choice(team_members, size=len(calendar_df))
    
    # Add content production status
    if 'status' in calendar_df.columns and 'publish_date' in calendar_df.columns:
        conditions = [
            (calendar_df['publish_date'] < today),
            (calendar_df['status'] == 'Draft'),
            (calendar_df['status'] == 'In Progress'),
            (calendar_df['content_creation_date'] > today)
        ]
        choices = ['Published', 'Draft', 'In Progress', 'Scheduled']
        calendar_df['production_status'] = np.select(conditions, choices, default='Idea')
    
    # Filter by date range if needed
    if 'publish_date' in calendar_df.columns:
        calendar_df = calendar_df[
            (calendar_df['publish_date'] >= start_date) & 
            (calendar_df['publish_date'] <= end_date)
        ]
    
    return calendar_df

def generate_social_media_post(content_row):
    """
    Generate a social media post based on content information
    
    Parameters:
    - content_row: Series or dict with content information
    
    Returns:
    - Dictionary with generated post content for different platforms
    """
    if content_row is None:
        return {}
    
    # Extract relevant information
    title = content_row.get('title', 'New Content')
    content_type = content_row.get('content_type', 'Blog Post')
    description = content_row.get('description', '')
    theme = content_row.get('theme', 'Social Innovation')
    keywords = content_row.get('keywords', 'social innovation').split(", ")
    
    # Generate hashtags from keywords
    hashtags = ["#" + re.sub(r'\s+', '', keyword) for keyword in keywords]
    hashtags.append("#CSI")
    hashtags.append("#SocialInnovation")
    hashtags_text = " ".join(hashtags[:5])  # Limit to 5 hashtags
    
    # Platform-specific posts
    posts = {}
    
    # LinkedIn post (more professional, longer)
    linkedin_templates = [
        "🚀 NEW {0}: {1}\n\n{2}\n\nLearn more on our website. {3}",
        "📢 Announcing: {1}\n\n{2}\n\nStay tuned for more updates! {3}",
        "📌 {1}\n\n{2}\n\nVisit our website to learn more about how CSI is driving social innovation. {3}",
        "🔍 Spotlight on {1}\n\n{2}\n\nConnect with us to be part of the social innovation community! {3}"
    ]
    
    linkedin_template = np.random.choice(linkedin_templates)
    posts['linkedin'] = linkedin_template.format(content_type, title, description, hashtags_text)
    
    # Twitter post (shorter, more concise)
    # Limit to ~240 characters to leave room for hashtags
    twitter_description = description
    if len(description) > 180:
        twitter_description = description[:177] + "..."
    
    twitter_templates = [
        "New {0}: {1}\n\n{2}\n\n{3}",
        "Check out: {1}\n\n{2}\n\n{3}",
        "{1}\n\n{2}\n\n{3}",
        "Just released: {1}\n\n{2}\n\n{3}"
    ]
    
    twitter_template = np.random.choice(twitter_templates)
    posts['twitter'] = twitter_template.format(content_type, title, twitter_description, hashtags_text)
    
    # Instagram post
    instagram_templates = [
        "📸 {1}\n\n{2}\n\n👉 Link in bio to learn more!\n\n{3}",
        "✨ New from CSI: {1}\n\n{2}\n\n👉 More details on our website (link in bio)\n\n{3}",
        "🔆 {1}\n\n{2}\n\n👉 Follow us for more social innovation content!\n\n{3}"
    ]
    
    instagram_template = np.random.choice(instagram_templates)
    posts['instagram'] = instagram_template.format(content_type, title, description, hashtags_text)
    
    # Facebook post
    facebook_templates = [
        "📢 {1}\n\n{2}\n\nLearn more on our website!\n\n{3}",
        "🚀 Introducing: {1}\n\n{2}\n\nVisit our page for more social innovation content.\n\n{3}",
        "📌 {1}\n\n{2}\n\nStay connected with CSI for the latest in social innovation!\n\n{3}"
    ]
    
    facebook_template = np.random.choice(facebook_templates)
    posts['facebook'] = facebook_template.format(content_type, title, description, hashtags_text)
    
    return posts

def generate_email_newsletter(content_ideas, org_name="Centre for Social Innovation"):
    """
    Generate an email newsletter based on content ideas
    
    Parameters:
    - content_ideas: DataFrame with content ideas
    - org_name: Name of the organization
    
    Returns:
    - Dictionary with newsletter content including subject, greeting, and sections
    """
    if content_ideas is None or len(content_ideas) == 0:
        return {
            "subject": f"{org_name} Newsletter",
            "greeting": "Hello from CSI!",
            "intro": "Welcome to our newsletter. Stay tuned for future content!",
            "content_sections": [],
            "closing": "Thank you for being part of our community.",
            "signature": f"The {org_name} Team"
        }
    
    # Get the current date for the newsletter
    today = datetime.now()
    month_year = today.strftime("%B %Y")
    
    # Generate subject line
    subject_templates = [
        f"{org_name} Newsletter: {month_year}",
        f"{month_year} Updates from {org_name}",
        f"What's New at {org_name} - {month_year}",
        f"The Latest from {org_name}: {month_year} Edition",
        f"{org_name} Connects: {month_year} News and Updates"
    ]
    subject = np.random.choice(subject_templates)
    
    # Generate greeting
    greeting_templates = [
        "Hello CSI Community!",
        "Greetings from the Centre for Social Innovation!",
        "Hello Social Innovators!",
        "Dear CSI Members and Partners,",
        "Welcome to our community update!"
    ]
    greeting = np.random.choice(greeting_templates)
    
    # Generate intro paragraph
    intro_templates = [
        f"Welcome to our {month_year} newsletter, where we share the latest updates, events, and stories from our community of social innovators.",
        f"We hope this newsletter finds you well. Here's what's been happening at CSI and what's coming up in {month_year}.",
        f"In this month's newsletter, we're excited to share some updates from our community and highlight upcoming opportunities for engagement.",
        f"Thank you for being part of the CSI community. We're thrilled to share our latest news and updates with you in this {month_year} edition."
    ]
    intro = np.random.choice(intro_templates)
    
    # Generate content sections from content ideas
    content_sections = []
    
    # Try to organize content by type
    content_types = ['Program Announcement', 'Event Announcement', 'Member Spotlight', 'Partner Spotlight', 'Blog Post']
    
    for content_type in content_types:
        type_content = content_ideas[content_ideas['content_type'] == content_type] if 'content_type' in content_ideas.columns else pd.DataFrame()
        
        if len(type_content) > 0:
            # Take up to 2 items of each type
            for _, row in type_content.head(2).iterrows():
                section = {
                    "heading": row.get('title', f"New {content_type}"),
                    "content": row.get('description', "More details coming soon!"),
                    "type": content_type
                }
                
                # Add call to action based on content type
                if content_type == 'Program Announcement':
                    section["cta"] = "Register Now"
                    section["cta_link"] = "#"
                elif content_type == 'Event Announcement':
                    section["cta"] = "Save Your Spot"
                    section["cta_link"] = "#"
                elif content_type in ['Member Spotlight', 'Partner Spotlight', 'Blog Post']:
                    section["cta"] = "Read More"
                    section["cta_link"] = "#"
                else:
                    section["cta"] = "Learn More"
                    section["cta_link"] = "#"
                
                content_sections.append(section)
    
    # Add any remaining content if we have few sections
    if len(content_sections) < 3:
        remaining_content = content_ideas[~content_ideas['content_type'].isin(content_types)] if 'content_type' in content_ideas.columns else content_ideas
        
        for _, row in remaining_content.head(3 - len(content_sections)).iterrows():
            section = {
                "heading": row.get('title', "Latest Update"),
                "content": row.get('description', "More details coming soon!"),
                "type": row.get('content_type', "Update"),
                "cta": "Discover More",
                "cta_link": "#"
            }
            content_sections.append(section)
    
    # Generate closing paragraph
    closing_templates = [
        "Thank you for being part of our community. We look forward to connecting with you at our upcoming events!",
        "We're excited about the months ahead and hope you'll continue to engage with our community and programs.",
        "As always, we're grateful for your continued support and participation in the CSI community.",
        "Stay connected with us on social media for the latest updates and opportunities to engage with our community."
    ]
    closing = np.random.choice(closing_templates)
    
    # Generate signature
    signature = f"The {org_name} Team"
    
    # Combine all elements into a newsletter structure
    newsletter = {
        "subject": subject,
        "greeting": greeting,
        "intro": intro,
        "content_sections": content_sections,
        "closing": closing,
        "signature": signature
    }
    
    return newsletter
