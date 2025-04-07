import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

def recommend_potential_members(membership_data, n_recommendations=5):
    """
    Generate recommendations for potential new members based on existing membership patterns
    
    Parameters:
    - membership_data: DataFrame with current membership information
    - n_recommendations: Number of recommendations to generate
    
    Returns:
    - DataFrame with potential member recommendations
    """
    if membership_data is None or len(membership_data) == 0:
        return pd.DataFrame()
        
    # Analyze patterns in current membership data
    
    # 1. Identify most common industries
    if 'industry' in membership_data.columns:
        top_industries = membership_data['industry'].value_counts().head(3).index.tolist()
    else:
        top_industries = ['Technology', 'Non-profit', 'Education']
    
    # 2. Identify most successful membership types
    if 'membership_type' in membership_data.columns and 'satisfaction_score' in membership_data.columns:
        type_satisfaction = membership_data.groupby('membership_type')['satisfaction_score'].mean()
        top_types = type_satisfaction.sort_values(ascending=False).head(2).index.tolist()
    else:
        top_types = ['Premium', 'Enterprise']
    
    # 3. Generate names for potential members
    organization_prefixes = [
        "Innovation", "Future", "Green", "Digital", "Smart", "Eco", 
        "Tech", "Global", "Social", "Sustainable", "Community"
    ]
    
    organization_suffixes = [
        "Solutions", "Initiatives", "Ventures", "Network", "Collective", 
        "Foundation", "Alliance", "Partners", "Hub", "Accelerator"
    ]
    
    # Generate potential member data
    potential_members = []
    
    for i in range(n_recommendations):
        # Generate a name by combining a prefix and suffix
        name = f"{np.random.choice(organization_prefixes)} {np.random.choice(organization_suffixes)}"
        
        # Pick an industry with emphasis on top industries
        if np.random.random() < 0.7:  # 70% chance to pick from top industries
            industry = np.random.choice(top_industries)
        else:
            industry = np.random.choice(['Healthcare', 'Environment', 'Media', 'Arts', 'Social Enterprise'])
        
        # Pick a recommended membership type with emphasis on top types
        if np.random.random() < 0.7:  # 70% chance to pick from top types
            membership_type = np.random.choice(top_types)
        else:
            membership_type = np.random.choice(['Basic', 'Non-profit', 'Academic'])
        
        # Generate other fields
        contact_person = f"Contact Person {i+1}"
        email = f"contact{i+1}@{name.lower().replace(' ', '')}.org"
        location = np.random.choice(['Toronto', 'New York', 'London', 'Remote'])
        
        # Add a match score (simulating how well they match CSI's criteria)
        match_score = np.random.randint(75, 96)
        
        # Add reasons for recommendation
        reasons = []
        if industry in top_industries:
            reasons.append(f"Industry ({industry}) aligns with current members")
        if np.random.random() > 0.5:
            reasons.append("Mission alignment with CSI values")
        if np.random.random() > 0.7:
            reasons.append("Potential for cross-member collaboration")
        if np.random.random() > 0.6:
            reasons.append("Growing organization with increasing impact")
            
        reasons_text = "; ".join(reasons)
        
        potential_members.append({
            'name': name,
            'contact_person': contact_person,
            'email': email,
            'industry': industry,
            'recommended_membership': membership_type,
            'location': location,
            'match_score': match_score,
            'recommendation_reasons': reasons_text
        })
    
    # Convert to DataFrame and sort by match score
    recommendations_df = pd.DataFrame(potential_members)
    recommendations_df = recommendations_df.sort_values('match_score', ascending=False)
    
    return recommendations_df

def recommend_partnerships(membership_data, partnership_data, n_recommendations=5):
    """
    Generate recommendations for potential new partnerships
    
    Parameters:
    - membership_data: DataFrame with current membership information
    - partnership_data: DataFrame with current partnership information
    - n_recommendations: Number of recommendations to generate
    
    Returns:
    - DataFrame with potential partnership recommendations
    """
    if partnership_data is None or len(partnership_data) == 0:
        # Create a default partnership DataFrame with minimal fields
        partnership_data = pd.DataFrame({
            'partnership_type': ['Funding', 'Program Collaboration', 'Strategic Alliance'],
            'focus_area': ['Social Justice', 'Technology', 'Environment'],
            'performance_rating': [8, 9, 7]
        })
    
    # Analyze patterns in current partnership data
    
    # 1. Identify most successful partnership types
    if 'partnership_type' in partnership_data.columns and 'performance_rating' in partnership_data.columns:
        type_performance = partnership_data.groupby('partnership_type')['performance_rating'].mean()
        top_types = type_performance.sort_values(ascending=False).head(2).index.tolist()
    else:
        top_types = ['Program Collaboration', 'Strategic Alliance']
    
    # 2. Identify most common focus areas
    if 'focus_area' in partnership_data.columns:
        top_focus_areas = partnership_data['focus_area'].value_counts().head(3).index.tolist()
    else:
        top_focus_areas = ['Technology', 'Environment', 'Social Justice']
    
    # 3. Generate names for potential partners
    organization_prefixes = [
        "Global", "National", "International", "Universal", "World", 
        "Alliance for", "Institute of", "Foundation for", "Center for"
    ]
    
    organization_suffixes = [
        "Innovation", "Sustainability", "Development", "Social Impact", 
        "Technology", "Advancement", "Education", "Research", "Policy"
    ]
    
    # Generate potential partnership data
    potential_partnerships = []
    
    for i in range(n_recommendations):
        # Generate a name by combining a prefix and suffix
        name = f"{np.random.choice(organization_prefixes)} {np.random.choice(organization_suffixes)}"
        
        # Pick a focus area with emphasis on top areas
        if np.random.random() < 0.7:  # 70% chance to pick from top areas
            focus_area = np.random.choice(top_focus_areas)
        else:
            focus_area = np.random.choice(['Healthcare', 'Education', 'Arts', 'Human Rights'])
        
        # Pick a recommended partnership type with emphasis on top types
        if np.random.random() < 0.7:  # 70% chance to pick from top types
            partnership_type = np.random.choice(top_types)
        else:
            partnership_type = np.random.choice(['Resource Sharing', 'Event Co-hosting', 'Funding'])
        
        # Generate other fields
        contact_person = f"Partner Contact {i+1}"
        email = f"contact{i+1}@{name.lower().replace(' ', '').replace('for', '')}.org"
        
        # Add a value potential score (estimated value contribution)
        value_potential = np.random.randint(10000, 50001)
        
        # Add an alignment score (how well they align with CSI's mission)
        alignment_score = np.random.randint(7, 11)
        
        # Add reasons for recommendation
        reasons = []
        if focus_area in top_focus_areas:
            reasons.append(f"Focus area ({focus_area}) aligns with CSI priorities")
        if partnership_type in top_types:
            reasons.append(f"Partnership type ({partnership_type}) has proven successful")
        if np.random.random() > 0.5:
            reasons.append("Strong reputation in the social innovation space")
        if np.random.random() > 0.7:
            reasons.append("Complementary resources and capabilities")
        if np.random.random() > 0.6:
            reasons.append("Potential for long-term strategic value")
            
        reasons_text = "; ".join(reasons)
        
        potential_partnerships.append({
            'name': name,
            'contact_person': contact_person,
            'email': email,
            'focus_area': focus_area,
            'recommended_partnership_type': partnership_type,
            'value_potential': value_potential,
            'alignment_score': alignment_score,
            'recommendation_reasons': reasons_text
        })
    
    # Convert to DataFrame and sort by alignment score and value potential
    recommendations_df = pd.DataFrame(potential_partnerships)
    recommendations_df['combined_score'] = (
        recommendations_df['alignment_score'] * 5000 + 
        recommendations_df['value_potential'] / 10000
    )
    recommendations_df = recommendations_df.sort_values('combined_score', ascending=False)
    
    # Drop the combined score column before returning
    return recommendations_df.drop(columns=['combined_score'])

def recommend_programs(membership_data, program_data, n_recommendations=5):
    """
    Generate recommendations for potential new programs
    
    Parameters:
    - membership_data: DataFrame with current membership information
    - program_data: DataFrame with current program information
    - n_recommendations: Number of recommendations to generate
    
    Returns:
    - DataFrame with potential program recommendations
    """
    if program_data is None or len(program_data) == 0:
        # Create a default program DataFrame with minimal fields
        program_data = pd.DataFrame({
            'program_type': ['Workshop', 'Mentoring', 'Training'],
            'target_audience': ['Startups', 'Non-profits', 'Social Enterprises'],
            'satisfaction_score': [8, 9, 7]
        })
    
    if membership_data is None or len(membership_data) == 0:
        # Create a default membership DataFrame with minimal fields
        membership_data = pd.DataFrame({
            'industry': ['Technology', 'Non-profit', 'Education'],
            'membership_type': ['Basic', 'Premium', 'Enterprise']
        })
    
    # Analyze patterns in current data
    
    # 1. Identify most successful program types
    if 'program_type' in program_data.columns and 'satisfaction_score' in program_data.columns:
        type_satisfaction = program_data.groupby('program_type')['satisfaction_score'].mean()
        top_types = type_satisfaction.sort_values(ascending=False).head(2).index.tolist()
    else:
        top_types = ['Mentoring', 'Workshop']
    
    # 2. Identify most common target audiences
    if 'target_audience' in program_data.columns:
        top_audiences = program_data['target_audience'].value_counts().head(3).index.tolist()
    else:
        top_audiences = ['Startups', 'Non-profits', 'Social Enterprises']
    
    # 3. Identify popular industries from membership data
    if 'industry' in membership_data.columns:
        top_industries = membership_data['industry'].value_counts().head(3).index.tolist()
    else:
        top_industries = ['Technology', 'Non-profit', 'Education']
    
    # Program name components
    program_prefixes = [
        "Accelerate", "Launch", "Grow", "Innovate", "Transform", 
        "Scale", "Impact", "Amplify", "Connect", "Empower"
    ]
    
    program_suffixes = [
        "Impact", "Growth", "Solutions", "Ventures", "Innovation", 
        "Leadership", "Sustainability", "Collaboration", "Future", "Change"
    ]
    
    # Program types to choose from
    program_types = [
        "Workshop", "Mentoring", "Networking", "Training", 
        "Accelerator", "Incubator", "Conference", "Bootcamp", 
        "Hackathon", "Fellowship", "Webinar Series"
    ]
    
    # Generate potential program data
    potential_programs = []
    
    for i in range(n_recommendations):
        # Generate a program name
        name = f"{np.random.choice(program_prefixes)} {np.random.choice(program_suffixes)}"
        
        # Pick a program type with emphasis on successful types
        if np.random.random() < 0.6 and top_types:  # 60% chance to pick from top types
            program_type = np.random.choice(top_types)
        else:
            program_type = np.random.choice(program_types)
        
        # Pick a target audience with emphasis on common audiences
        if np.random.random() < 0.7 and top_audiences:  # 70% chance to pick from top audiences
            target_audience = np.random.choice(top_audiences)
        else:
            target_audience = np.random.choice(['Students', 'Community Leaders', 'General Public', 'Researchers'])
        
        # Generate description based on program type and audience
        description = f"A {program_type.lower()} program designed for {target_audience.lower()}"
        if program_type == "Workshop":
            description += " to develop practical skills in social innovation."
        elif program_type == "Mentoring":
            description += " to connect with experienced leaders in the field."
        elif program_type == "Networking":
            description += " to build valuable connections in the social impact ecosystem."
        elif program_type == "Training":
            description += " to acquire specialized knowledge and capabilities."
        elif program_type == "Accelerator":
            description += " to rapidly scale their social impact initiatives."
        elif program_type == "Incubator":
            description += " to nurture early-stage social innovation ideas."
        else:
            description += " to advance their social impact goals."
        
        # Estimate resource requirements (1-10 scale, lower is better for low-capacity deployment)
        resource_requirement = np.random.randint(2, 8)
        
        # Estimate potential impact (1-10 scale)
        potential_impact = np.random.randint(6, 11)
        
        # Estimate expected satisfaction
        expected_satisfaction = np.random.randint(7, 11)
        
        # Generate an estimated budget
        estimated_budget = resource_requirement * np.random.randint(1000, 3001)
        
        # Calculate implementation complexity (1-10 scale, lower is easier)
        implementation_complexity = resource_requirement + np.random.randint(-1, 2)
        implementation_complexity = max(1, min(10, implementation_complexity))
        
        # Add reasons for recommendation
        reasons = []
        if program_type in top_types:
            reasons.append(f"Program type ({program_type}) has proven successful")
        if target_audience in top_audiences:
            reasons.append(f"High demand from target audience ({target_audience})")
        if resource_requirement <= 5:
            reasons.append("Low resource requirements for implementation")
        if potential_impact >= 8:
            reasons.append("High potential impact for CSI community")
        if implementation_complexity <= 4:
            reasons.append("Relatively simple to implement")
            
        # Ensure at least one reason
        if not reasons:
            reasons.append("Addresses emerging needs in the social innovation space")
            
        reasons_text = "; ".join(reasons)
        
        # Calculate a feasibility score (higher is better)
        feasibility_score = ((11 - implementation_complexity) * 5 + 
                             (11 - resource_requirement) * 3 + 
                             potential_impact * 4 + 
                             expected_satisfaction * 3) / 15
        
        potential_programs.append({
            'name': name,
            'program_type': program_type,
            'target_audience': target_audience,
            'description': description,
            'resource_requirement': resource_requirement,
            'potential_impact': potential_impact,
            'expected_satisfaction': expected_satisfaction,
            'estimated_budget': estimated_budget,
            'implementation_complexity': implementation_complexity,
            'feasibility_score': round(feasibility_score, 1),
            'recommendation_reasons': reasons_text
        })
    
    # Convert to DataFrame and sort by feasibility score
    recommendations_df = pd.DataFrame(potential_programs)
    recommendations_df = recommendations_df.sort_values('feasibility_score', ascending=False)
    
    return recommendations_df

def find_similar_members(membership_data, member_id, n_similar=5):
    """
    Find similar members to a given member based on their attributes
    
    Parameters:
    - membership_data: DataFrame with membership information
    - member_id: ID of the target member
    - n_similar: Number of similar members to find
    
    Returns:
    - DataFrame with similar members
    """
    if membership_data is None or len(membership_data) == 0 or member_id not in membership_data['member_id'].values:
        return pd.DataFrame()
    
    # Get feature columns for similarity calculation
    feature_columns = []
    
    # Numeric features
    numeric_features = [
        'satisfaction_score', 'attendance_rate', 'engagement_score', 
        'membership_duration_days', 'fees_paid'
    ]
    
    # Categorical features to one-hot encode
    categorical_features = [
        'membership_type', 'industry', 'engagement_level', 'location'
    ]
    
    # Add numeric features if they exist
    for feature in numeric_features:
        if feature in membership_data.columns:
            feature_columns.append(feature)
    
    # One-hot encode categorical features if they exist
    encoded_data = membership_data.copy()
    for feature in categorical_features:
        if feature in membership_data.columns:
            # One-hot encode the feature
            one_hot = pd.get_dummies(membership_data[feature], prefix=feature)
            # Add the one-hot encoded columns to the data
            encoded_data = pd.concat([encoded_data, one_hot], axis=1)
            # Add the new column names to feature_columns
            feature_columns.extend(one_hot.columns)
    
    # If no suitable features found, return empty DataFrame
    if not feature_columns:
        return pd.DataFrame()
    
    # Extract feature matrix
    X = encoded_data[feature_columns].values
    
    # Standardize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Calculate cosine similarity between members
    similarity_matrix = cosine_similarity(X_scaled)
    
    # Get the index of the target member
    target_index = encoded_data[encoded_data['member_id'] == member_id].index[0]
    
    # Get similarity scores for the target member
    similarity_scores = similarity_matrix[target_index]
    
    # Create a DataFrame with member IDs and similarity scores
    similarity_df = pd.DataFrame({
        'member_id': encoded_data['member_id'],
        'name': encoded_data['name'],
        'similarity_score': similarity_scores
    })
    
    # Remove the target member and sort by similarity score
    similarity_df = similarity_df[similarity_df['member_id'] != member_id]
    similarity_df = similarity_df.sort_values('similarity_score', ascending=False)
    
    # Return top n similar members
    return similarity_df.head(n_similar)
