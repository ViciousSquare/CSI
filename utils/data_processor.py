import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io

def process_uploaded_data(uploaded_file, data_type):
    """
    Process uploaded CSV files based on data type
    
    Parameters:
    - uploaded_file: The file object from st.file_uploader
    - data_type: The type of data being processed (membership, partnership, program, content)
    
    Returns:
    - DataFrame with processed data
    """
    # Read the CSV file
    data = pd.read_csv(uploaded_file)
    
    # Basic validation based on data type
    if data_type == "membership":
        required_columns = ["member_id", "name", "join_date", "membership_type"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert date columns if present
        if "join_date" in data.columns:
            data["join_date"] = pd.to_datetime(data["join_date"])
        
        # Calculate additional metrics
        data["membership_duration_days"] = (datetime.now() - data["join_date"]).dt.days
        
    elif data_type == "partnership":
        required_columns = ["partner_id", "name", "partnership_type", "start_date"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert date columns if present
        if "start_date" in data.columns:
            data["start_date"] = pd.to_datetime(data["start_date"])
        if "end_date" in data.columns:
            data["end_date"] = pd.to_datetime(data["end_date"])
            
    elif data_type == "program":
        required_columns = ["program_id", "name", "start_date", "status"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert date columns if present
        if "start_date" in data.columns:
            data["start_date"] = pd.to_datetime(data["start_date"])
        if "end_date" in data.columns:
            data["end_date"] = pd.to_datetime(data["end_date"])
    
    elif data_type == "content":
        required_columns = ["content_id", "title", "content_type", "publish_date"]
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert date columns if present
        if "publish_date" in data.columns:
            data["publish_date"] = pd.to_datetime(data["publish_date"])
    
    return data

def load_sample_data(data_type):
    """
    Generate sample data for demonstration purposes
    
    Parameters:
    - data_type: The type of data to generate (membership, partnership, program, content)
    
    Returns:
    - DataFrame with sample data
    """
    # Generate appropriate sample data based on the data type
    today = datetime.now()
    
    if data_type == "membership":
        # Create sample membership data
        member_types = ["Basic", "Premium", "Enterprise", "Non-profit", "Academic"]
        engagement_levels = ["Low", "Medium", "High"]
        industries = ["Technology", "Healthcare", "Education", "Non-profit", "Environment", "Social Enterprise"]
        
        data = {
            "member_id": [f"M{i:04d}" for i in range(1, 51)],
            "name": [f"Member Organization {i}" for i in range(1, 51)],
            "contact_person": [f"Contact {i}" for i in range(1, 51)],
            "email": [f"contact{i}@example.org" for i in range(1, 51)],
            "join_date": [today - timedelta(days=np.random.randint(30, 1500)) for _ in range(50)],
            "membership_type": np.random.choice(member_types, 50),
            "renewal_date": [today + timedelta(days=np.random.randint(1, 365)) for _ in range(50)],
            "industry": np.random.choice(industries, 50),
            "satisfaction_score": np.random.randint(5, 11, 50),
            "engagement_level": np.random.choice(engagement_levels, 50),
            "last_interaction": [today - timedelta(days=np.random.randint(1, 90)) for _ in range(50)],
            "attendance_rate": [round(np.random.uniform(0.1, 1.0), 2) for _ in range(50)],
            "fees_paid": np.random.randint(1000, 10000, 50),
            "location": np.random.choice(["Toronto", "New York", "London", "Remote"], 50)
        }
        
        df = pd.DataFrame(data)
        df["membership_duration_days"] = (today - df["join_date"]).dt.days
        
        # Set some renewal dates to past dates to simulate expired memberships
        expired_indices = np.random.choice(range(50), 10, replace=False)
        # Generate random days for each expired index individually
        for i, idx in enumerate(expired_indices):
            df.loc[idx, "renewal_date"] = today - timedelta(days=np.random.randint(1, 90))
        
        return df
        
    elif data_type == "partnership":
        # Create sample partnership data
        partnership_types = ["Funding", "Program Collaboration", "Resource Sharing", "Event Co-hosting", "Strategic Alliance"]
        statuses = ["Active", "Pending", "Completed", "Negotiation"]
        
        data = {
            "partner_id": [f"P{i:04d}" for i in range(1, 31)],
            "name": [f"Partner Organization {i}" for i in range(1, 31)],
            "partnership_type": np.random.choice(partnership_types, 30),
            "start_date": [today - timedelta(days=np.random.randint(30, 730)) for _ in range(30)],
            "end_date": [today + timedelta(days=np.random.randint(-90, 365)) for _ in range(30)],
            "status": np.random.choice(statuses, 30),
            "focus_area": np.random.choice(["Education", "Environment", "Technology", "Social Justice", "Healthcare"], 30),
            "contact_person": [f"Partner Contact {i}" for i in range(1, 31)],
            "email": [f"partner{i}@example.org" for i in range(1, 31)],
            "value_contribution": np.random.randint(5000, 50000, 30),
            "performance_rating": np.random.randint(1, 11, 30),
            "alignment_score": np.random.randint(1, 11, 30),
            "meetings_count": np.random.randint(1, 20, 30),
            "shared_resources": np.random.randint(0, 10, 30)
        }
        
        df = pd.DataFrame(data)
        
        # Update status based on dates
        df.loc[df["end_date"] < today, "status"] = "Completed"
        df.loc[(df["start_date"] > today) & (df["status"] != "Negotiation"), "status"] = "Pending"
        
        return df
        
    elif data_type == "program":
        # Create sample program data
        program_statuses = ["Active", "Planned", "Completed", "On Hold"]
        program_types = ["Workshop", "Mentoring", "Networking", "Training", "Accelerator", "Incubator", "Conference"]
        target_audiences = ["Startups", "Non-profits", "Social Enterprises", "Students", "Community Leaders", "General Public"]
        
        data = {
            "program_id": [f"PRG{i:03d}" for i in range(1, 26)],
            "name": [f"Program {i}" for i in range(1, 26)],
            "description": [f"Description for Program {i}" for i in range(1, 26)],
            "program_type": np.random.choice(program_types, 25),
            "target_audience": np.random.choice(target_audiences, 25),
            "start_date": [today - timedelta(days=np.random.randint(-90, 365)) for _ in range(25)],
            "end_date": [today + timedelta(days=np.random.randint(-30, 730)) for _ in range(25)],
            "status": np.random.choice(program_statuses, 25),
            "capacity": np.random.randint(10, 101, 25),
            "current_enrollment": np.random.randint(0, 101, 25),
            "satisfaction_score": np.random.randint(5, 11, 25),
            "budget": np.random.randint(1000, 50000, 25),
            "expenses": np.random.randint(500, 50000, 25),
            "coordinator": [f"Coordinator {i}" for i in range(1, 26)],
            "success_metric": np.random.uniform(0.5, 1.0, 25).round(2)
        }
        
        df = pd.DataFrame(data)
        
        # Update status based on dates
        df.loc[df["end_date"] < today, "status"] = "Completed"
        df.loc[(df["start_date"] > today) & (df["status"] != "On Hold"), "status"] = "Planned"
        
        # Ensure enrollment doesn't exceed capacity
        for i in range(len(df)):
            if df.iloc[i]["current_enrollment"] > df.iloc[i]["capacity"]:
                df.iloc[i, df.columns.get_loc("current_enrollment")] = df.iloc[i]["capacity"]
        
        return df
        
    elif data_type == "content":
        # Create sample content calendar data
        content_types = ["Blog Post", "Newsletter", "Social Media", "Event Announcement", "Case Study", "Report"]
        content_statuses = ["Published", "Draft", "Scheduled", "Idea"]
        channels = ["Website", "Email", "LinkedIn", "Twitter", "Facebook", "Instagram"]
        
        data = {
            "content_id": [f"CNT{i:03d}" for i in range(1, 41)],
            "title": [f"Content Title {i}" for i in range(1, 41)],
            "content_type": np.random.choice(content_types, 40),
            "description": [f"Brief description for content {i}" for i in range(1, 41)],
            "target_audience": np.random.choice(["Members", "Partners", "General Public", "Potential Members"], 40),
            "publish_date": [today + timedelta(days=np.random.randint(-90, 90)) for _ in range(40)],
            "status": np.random.choice(content_statuses, 40),
            "author": [f"Author {i % 5 + 1}" for i in range(40)],
            "channel": [", ".join(np.random.choice(channels, np.random.randint(1, 4), replace=False)) for _ in range(40)],
            "engagement_score": np.random.randint(1, 101, 40),
            "related_program": [f"PRG{np.random.randint(1, 26):03d}" if np.random.random() > 0.3 else None for _ in range(40)],
            "keywords": [", ".join(np.random.choice(["innovation", "social impact", "sustainability", "community", "technology", "partnership"], np.random.randint(1, 4), replace=False)) for _ in range(40)],
            "estimated_reach": np.random.randint(100, 10000, 40)
        }
        
        df = pd.DataFrame(data)
        
        # Update status based on dates
        df.loc[df["publish_date"] < today, "status"] = "Published"
        df.loc[(df["publish_date"] > today) & (df["status"] != "Idea") & (df["status"] != "Draft"), "status"] = "Scheduled"
        
        return df
    
    # If data type is not recognized, return empty dataframe
    return pd.DataFrame()

def calculate_member_engagement(membership_data):
    """
    Calculate member engagement scores based on various metrics
    
    Parameters:
    - membership_data: DataFrame with membership information
    
    Returns:
    - DataFrame with added engagement scores
    """
    if membership_data is None or len(membership_data) == 0:
        return None
    
    data = membership_data.copy()
    
    # Calculate days since last interaction
    if "last_interaction" in data.columns:
        data["days_since_interaction"] = (datetime.now() - data["last_interaction"]).dt.days
    else:
        data["days_since_interaction"] = 30  # Default value
    
    # Calculate engagement score based on multiple factors
    # 1. Attendance rate (if available)
    # 2. Satisfaction score (if available)
    # 3. Days since last interaction
    # 4. Membership duration (loyalty factor)
    
    attendance_weight = 0.3
    satisfaction_weight = 0.3
    recency_weight = 0.2
    loyalty_weight = 0.2
    
    # Normalize each factor to 0-1 scale
    if "attendance_rate" in data.columns:
        attendance_score = data["attendance_rate"]
    else:
        attendance_score = pd.Series([0.5] * len(data))  # Default value
    
    if "satisfaction_score" in data.columns:
        satisfaction_score = data["satisfaction_score"] / 10
    else:
        satisfaction_score = pd.Series([0.5] * len(data))  # Default value
    
    # Recency score - more recent interactions get higher scores
    recency_score = 1 - (data["days_since_interaction"] / data["days_since_interaction"].max())
    
    # Loyalty score based on membership duration
    loyalty_score = data["membership_duration_days"] / data["membership_duration_days"].max()
    
    # Combine all factors into an overall engagement score
    data["engagement_score"] = (
        (attendance_weight * attendance_score) +
        (satisfaction_weight * satisfaction_score) +
        (recency_weight * recency_score) +
        (loyalty_weight * loyalty_score)
    )
    
    # Convert to a 0-100 scale for easier interpretation
    data["engagement_score"] = (data["engagement_score"] * 100).round(1)
    
    # Categorize engagement levels
    conditions = [
        (data["engagement_score"] >= 75),
        (data["engagement_score"] >= 50),
        (data["engagement_score"] >= 25)
    ]
    choices = ["High", "Medium", "Low"]
    data["engagement_level"] = np.select(conditions, choices, default="Very Low")
    
    return data

def calculate_partnership_effectiveness(partnership_data):
    """
    Calculate partnership effectiveness metrics
    
    Parameters:
    - partnership_data: DataFrame with partnership information
    
    Returns:
    - DataFrame with added effectiveness metrics
    """
    if partnership_data is None or len(partnership_data) == 0:
        return None
        
    data = partnership_data.copy()
    
    # Calculate partnership duration in days
    if "start_date" in data.columns and "end_date" in data.columns:
        data["partnership_duration"] = (data["end_date"] - data["start_date"]).dt.days
        
        # For ongoing partnerships, calculate duration until today
        today = datetime.now()
        data.loc[data["end_date"] > today, "partnership_duration"] = (today - data["start_date"]).dt.days
        
    # Calculate return on investment if we have value and cost data
    if "value_contribution" in data.columns and "cost" in data.columns:
        data["roi"] = (data["value_contribution"] - data["cost"]) / data["cost"]
    elif "value_contribution" in data.columns:
        # Estimate ROI using just the value
        data["roi"] = data["value_contribution"] / 5000  # Assuming average cost of 5000
    
    # Calculate effectiveness score
    if "performance_rating" in data.columns and "alignment_score" in data.columns:
        # Combine performance and alignment for overall effectiveness
        data["effectiveness_score"] = (data["performance_rating"] + data["alignment_score"]) / 2
    elif "performance_rating" in data.columns:
        data["effectiveness_score"] = data["performance_rating"]
    elif "alignment_score" in data.columns:
        data["effectiveness_score"] = data["alignment_score"]
    else:
        data["effectiveness_score"] = 5  # Default middle value
    
    # Categorize effectiveness
    conditions = [
        (data["effectiveness_score"] >= 8),
        (data["effectiveness_score"] >= 6),
        (data["effectiveness_score"] >= 4)
    ]
    choices = ["High", "Medium", "Low"]
    data["effectiveness_category"] = np.select(conditions, choices, default="Very Low")
    
    return data

def analyze_program_performance(program_data):
    """
    Analyze program performance metrics
    
    Parameters:
    - program_data: DataFrame with program information
    
    Returns:
    - DataFrame with added performance metrics
    """
    if program_data is None or len(program_data) == 0:
        return None
        
    data = program_data.copy()
    
    # Calculate enrollment rate
    if "capacity" in data.columns and "current_enrollment" in data.columns:
        data["enrollment_rate"] = (data["current_enrollment"] / data["capacity"]).round(2)
    
    # Calculate budget utilization
    if "budget" in data.columns and "expenses" in data.columns:
        data["budget_utilization"] = (data["expenses"] / data["budget"]).round(2)
    
    # Calculate overall performance score
    performance_metrics = []
    weights = []
    
    if "enrollment_rate" in data.columns:
        performance_metrics.append(data["enrollment_rate"])
        weights.append(0.3)
        
    if "satisfaction_score" in data.columns:
        # Normalize satisfaction to 0-1 scale
        performance_metrics.append(data["satisfaction_score"] / 10)
        weights.append(0.4)
        
    if "success_metric" in data.columns:
        performance_metrics.append(data["success_metric"])
        weights.append(0.3)
        
    if "budget_utilization" in data.columns:
        # For budget utilization, closer to 1.0 is better
        budget_score = 1 - abs(data["budget_utilization"] - 1)
        performance_metrics.append(budget_score)
        weights.append(0.2)
    
    # If we have metrics, calculate weighted average
    if performance_metrics:
        total_weight = sum(weights)
        weighted_metrics = [metric * (weight / total_weight) for metric, weight in zip(performance_metrics, weights)]
        data["performance_score"] = sum(weighted_metrics) * 100
    else:
        # Default value if no metrics available
        data["performance_score"] = 50
    
    # Categorize performance
    conditions = [
        (data["performance_score"] >= 80),
        (data["performance_score"] >= 60),
        (data["performance_score"] >= 40)
    ]
    choices = ["High", "Medium", "Low"]
    data["performance_category"] = np.select(conditions, choices, default="Very Low")
    
    return data
