import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

from utils.data_processor import analyze_program_performance
from utils.visualizer import plot_program_performance
from utils.recommender import recommend_programs

def app():
    st.title("Program Management")
    
    if 'program_data' not in st.session_state or st.session_state.program_data is None:
        st.info("No program data available. Please upload program data from the main page.")
        return
    
    # Process the data to add performance metrics
    program_data = analyze_program_performance(st.session_state.program_data)
    
    # Create tabs for different program management views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Program Overview", 
        "Performance Analysis", 
        "Program Recommendations",
        "Program Details"
    ])
    
    with tab1:
        st.header("Program Overview")
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_programs = len(program_data)
            st.metric("Total Programs", total_programs)
            
        with col2:
            # Calculate active programs
            if 'status' in program_data.columns:
                active_programs = program_data[program_data['status'] == 'Active'].shape[0]
                st.metric("Active Programs", active_programs)
            else:
                st.metric("Active Programs", "N/A")
            
        with col3:
            # Calculate average satisfaction if available
            if 'satisfaction_score' in program_data.columns:
                avg_satisfaction = round(program_data['satisfaction_score'].mean(), 1)
                st.metric("Avg. Satisfaction", f"{avg_satisfaction}/10")
            else:
                st.metric("Avg. Satisfaction", "N/A")
            
        with col4:
            # Calculate average enrollment rate if available
            if 'enrollment_rate' in program_data.columns:
                avg_enrollment = round(program_data['enrollment_rate'].mean() * 100, 1)
                st.metric("Avg. Enrollment Rate", f"{avg_enrollment}%")
            else:
                st.metric("Avg. Enrollment Rate", "N/A")
        
        # Program type distribution
        if 'program_type' in program_data.columns:
            st.subheader("Program Type Distribution")
            type_counts = program_data['program_type'].value_counts().reset_index()
            type_counts.columns = ['program_type', 'count']
            
            fig = px.pie(
                type_counts, 
                values='count', 
                names='program_type',
                title='Program Types',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Program status distribution
        if 'status' in program_data.columns:
            st.subheader("Program Status")
            status_counts = program_data['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            fig = px.bar(
                status_counts,
                x='status',
                y='count',
                title='Program Status Distribution',
                color='status',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Target audience distribution if available
        if 'target_audience' in program_data.columns:
            st.subheader("Target Audience Distribution")
            
            audience_counts = program_data['target_audience'].value_counts().reset_index()
            audience_counts.columns = ['target_audience', 'count']
            
            fig = px.bar(
                audience_counts,
                x='target_audience',
                y='count',
                title='Program Target Audiences',
                color='target_audience',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Program timeline
        if 'start_date' in program_data.columns:
            st.subheader("Program Timeline")
            
            # Sort programs by start date
            timeline_data = program_data.sort_values('start_date')
            
            # Create a gantt chart of programs
            if 'end_date' in timeline_data.columns:
                # For programs without an end date, use today + 6 months as placeholder
                today = datetime.now()
                timeline_data['display_end_date'] = timeline_data['end_date'].fillna(today + timedelta(days=180))
                
                fig = px.timeline(
                    timeline_data,
                    x_start='start_date',
                    x_end='display_end_date',
                    y='name',
                    color='program_type' if 'program_type' in timeline_data.columns else 'status',
                    hover_name='name',
                    title='Program Timeline',
                    color_discrete_sequence=px.colors.qualitative.Bold
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
        
        # Budget utilization if available
        if 'budget' in program_data.columns and 'expenses' in program_data.columns:
            st.subheader("Budget Utilization")
            
            # Calculate budget utilization percentage
            program_data['budget_utilization_pct'] = (program_data['expenses'] / program_data['budget'] * 100).round(1)
            
            # Sort by budget utilization
            budget_data = program_data.sort_values('budget_utilization_pct', ascending=False)
            
            fig = px.bar(
                budget_data,
                x='name',
                y='budget_utilization_pct',
                title='Program Budget Utilization (%)',
                color='status' if 'status' in budget_data.columns else None,
                hover_data=['budget', 'expenses'],
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            # Add a horizontal line at 100% utilization
            fig.add_hline(
                y=100,
                line_width=2,
                line_dash="dash",
                line_color="grey"
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Program Performance Analysis")
        
        # Plot program performance
        performance_fig = plot_program_performance(program_data)
        st.plotly_chart(performance_fig, use_container_width=True)
        
        # Performance category distribution if available
        if 'performance_category' in program_data.columns:
            st.subheader("Performance Distribution")
            
            performance_counts = program_data['performance_category'].value_counts().reset_index()
            performance_counts.columns = ['performance_category', 'count']
            
            # Define a custom order for performance levels
            level_order = ['High', 'Medium', 'Low', 'Very Low']
            performance_counts['performance_category'] = pd.Categorical(
                performance_counts['performance_category'], 
                categories=level_order, 
                ordered=True
            )
            performance_counts = performance_counts.sort_values('performance_category')
            
            fig = px.bar(
                performance_counts,
                x='performance_category',
                y='count',
                title='Program Performance Levels',
                color='performance_category',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Satisfaction vs Enrollment Matrix
        if 'satisfaction_score' in program_data.columns and 'enrollment_rate' in program_data.columns:
            st.subheader("Satisfaction vs Enrollment Matrix")
            
            # Create a copy for safe manipulation
            plot_data = program_data.copy()
            
            # Ensure capacity is positive for plotting
            if 'capacity' in plot_data.columns:
                # Use absolute value to ensure positive values for size
                plot_data['plot_capacity'] = plot_data['capacity'].abs()
                size_col = 'plot_capacity'
            else:
                size_col = None
            
            fig = px.scatter(
                plot_data,
                x='satisfaction_score',
                y='enrollment_rate',
                color='program_type' if 'program_type' in plot_data.columns else None,
                size=size_col,
                hover_name='name',
                title='Program Satisfaction vs Enrollment Rate',
                labels={
                    'satisfaction_score': 'Satisfaction Score',
                    'enrollment_rate': 'Enrollment Rate',
                    'program_type': 'Program Type',
                    'plot_capacity': 'Capacity'
                }
            )
            
            # Convert enrollment rate to percentage for display
            fig.update_layout(
                yaxis_tickformat='.0%'
            )
            
            # Add quadrant lines
            mid_satisfaction = 7.5  # Midpoint on 1-10 scale
            mid_enrollment = 0.5    # 50% enrollment rate
            
            fig.add_hline(
                y=mid_enrollment,
                line_width=1,
                line_dash="dash",
                line_color="grey"
            )
            
            fig.add_vline(
                x=mid_satisfaction,
                line_width=1,
                line_dash="dash",
                line_color="grey"
            )
            
            # Add quadrant annotations
            fig.add_annotation(
                x=9,
                y=0.9,
                text="High Satisfaction<br>High Enrollment",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=5,
                y=0.9,
                text="Low Satisfaction<br>High Enrollment",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=9,
                y=0.2,
                text="High Satisfaction<br>Low Enrollment",
                showarrow=False,
                font=dict(size=10)
            )
            
            fig.add_annotation(
                x=5,
                y=0.2,
                text="Low Satisfaction<br>Low Enrollment",
                showarrow=False,
                font=dict(size=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Programs requiring attention
        if 'performance_score' in program_data.columns:
            st.subheader("Programs Requiring Attention")
            
            # Filter for low performance programs
            attention_needed = program_data[
                (program_data['performance_score'] < 60) & 
                (program_data['status'] == 'Active' if 'status' in program_data.columns else True)
            ].sort_values('performance_score')
            
            if not attention_needed.empty:
                # Show in a data table
                st.write(f"Found {len(attention_needed)} programs with low performance:")
                
                # Select columns to display
                display_cols = ['name', 'program_type', 'performance_score', 
                                'enrollment_rate' if 'enrollment_rate' in attention_needed.columns else None,
                                'satisfaction_score' if 'satisfaction_score' in attention_needed.columns else None]
                display_cols = [col for col in display_cols if col is not None]
                
                st.dataframe(attention_needed[display_cols])
                
                # Add improvement strategies
                st.subheader("Recommended Improvement Strategies")
                st.write("""
                For programs with low performance:
                
                1. **Program Review**: Conduct a thorough review to identify specific issues.
                2. **Participant Feedback**: Gather detailed feedback from participants.
                3. **Content Refresh**: Update program content to better meet participant needs.
                4. **Marketing Boost**: Enhance marketing efforts to increase enrollment.
                5. **Format Adjustments**: Consider format changes (length, delivery method, etc.).
                6. **Facilitator Training**: Provide additional training to program facilitators.
                7. **Resource Allocation**: Ensure adequate resources are allocated to the program.
                """)
            else:
                st.write("No active programs with low performance found.")
    
    with tab3:
        st.header("Program Recommendations")
        
        # Generate new program recommendations
        st.subheader("Potential New Programs")
        
        # Allow user to set number of recommendations
        num_recommendations = st.slider(
            "Number of recommendations", 
            min_value=3, 
            max_value=10, 
            value=5,
            help="Select how many potential program recommendations to generate"
        )
        
        if st.button("Generate Program Recommendations"):
            with st.spinner("Generating potential program recommendations..."):
                membership_data = st.session_state.membership_data if 'membership_data' in st.session_state else None
                potential_programs = recommend_programs(
                    membership_data,
                    program_data, 
                    n_recommendations=num_recommendations
                )
                
                if not potential_programs.empty:
                    # Display in an expandable dataframe
                    st.dataframe(
                        potential_programs[[
                            'name', 'program_type', 'target_audience', 
                            'feasibility_score', 'potential_impact', 'resource_requirement'
                        ]], 
                        use_container_width=True
                    )
                    
                    # Show detailed view for each potential program
                    for i, program in potential_programs.iterrows():
                        with st.expander(f"📋 Details for {program['name']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Program Type:** {program['program_type']}")
                                st.write(f"**Target Audience:** {program['target_audience']}")
                                st.write(f"**Description:** {program['description']}")
                                st.write(f"**Estimated Budget:** ${program['estimated_budget']:,}")
                            
                            with col2:
                                st.write(f"**Feasibility Score:** {program['feasibility_score']}/10")
                                st.write(f"**Potential Impact:** {program['potential_impact']}/10")
                                st.write(f"**Resource Requirement:** {program['resource_requirement']}/10 (lower is better)")
                                st.write(f"**Implementation Complexity:** {program['implementation_complexity']}/10 (lower is easier)")
                                st.write(f"**Expected Satisfaction:** {program['expected_satisfaction']}/10")
                                
                            st.write("**Why this recommendation:**")
                            for reason in program['recommendation_reasons'].split(";"):
                                st.write(f"- {reason.strip()}")
                            
                            # Implementation plan
                            st.subheader("Implementation Plan")
                            st.write(f"""
                            **Phase 1: Planning** (4-6 weeks)
                            - Define detailed program objectives and success metrics
                            - Develop curriculum and program materials
                            - Identify necessary resources and staff requirements
                            - Create marketing and outreach plan
                            
                            **Phase 2: Pilot** (4-8 weeks)
                            - Launch small-scale pilot with limited participants
                            - Gather detailed feedback
                            - Make necessary adjustments
                            
                            **Phase 3: Launch** (2-4 weeks)
                            - Finalize program materials based on pilot feedback
                            - Launch full marketing campaign
                            - Open registration
                            
                            **Phase 4: Evaluation** (Ongoing)
                            - Collect participant feedback
                            - Monitor key performance indicators
                            - Make iterative improvements
                            
                            **Estimated Timeline:** {8 + 2*program['implementation_complexity']}-{12 + 3*program['implementation_complexity']} weeks to full implementation
                            """)
                else:
                    st.error("Unable to generate recommendations. Please check the data.")
        
        # Program optimization strategies
        st.subheader("Program Optimization Strategies")
        
        # Categorize programs based on performance if performance_score is available
        if 'performance_score' in program_data.columns and 'status' in program_data.columns:
            active_programs = program_data[program_data['status'] == 'Active']
            
            if not active_programs.empty:
                # Create program categories
                high_performing = active_programs[active_programs['performance_score'] >= 80]
                mid_performing = active_programs[(active_programs['performance_score'] >= 60) & (active_programs['performance_score'] < 80)]
                low_performing = active_programs[active_programs['performance_score'] < 60]
                
                # Allow user to select a category
                program_category = st.selectbox(
                    "Select program category for optimization strategies",
                    ["High Performing Programs", "Medium Performing Programs", "Low Performing Programs", "All Active Programs"]
                )
                
                if program_category == "High Performing Programs":
                    selected_programs = high_performing
                    st.write("""
                    **Optimization Strategies for High Performing Programs:**
                    
                    1. **Expansion Strategy**: Consider expanding successful programs to reach more participants.
                    2. **Documentation**: Document best practices and key success factors.
                    3. **Knowledge Transfer**: Use insights from these programs to improve others.
                    4. **Advanced Offerings**: Develop advanced or next-level offerings for repeat participants.
                    5. **Showcase Success**: Feature these programs in marketing and partnership discussions.
                    6. **Impact Measurement**: Enhance impact measurement to quantify success.
                    7. **Resource Optimization**: Ensure optimal resource allocation for sustained excellence.
                    """)
                elif program_category == "Medium Performing Programs":
                    selected_programs = mid_performing
                    st.write("""
                    **Optimization Strategies for Medium Performing Programs:**
                    
                    1. **Gap Analysis**: Identify specific gaps preventing higher performance.
                    2. **Targeted Improvements**: Focus on 2-3 key improvement areas rather than complete overhaul.
                    3. **Participant Feedback**: Gather detailed participant feedback on improvement areas.
                    4. **Content Review**: Ensure content remains relevant and engaging.
                    5. **Facilitator Support**: Provide additional support or training to facilitators.
                    6. **Marketing Refinement**: Refine messaging to better target ideal participants.
                    7. **Format Optimization**: Test format adjustments (timing, duration, delivery).
                    """)
                elif program_category == "Low Performing Programs":
                    selected_programs = low_performing
                    st.write("""
                    **Optimization Strategies for Low Performing Programs:**
                    
                    1. **Comprehensive Review**: Conduct a thorough program review with stakeholders.
                    2. **Major Redesign**: Consider significant redesign based on feedback.
                    3. **Market Validation**: Re-validate market need and program positioning.
                    4. **Resource Evaluation**: Assess if adequate resources are allocated.
                    5. **Pilot Approach**: Test major changes with small pilot groups.
                    6. **Sunset Consideration**: Evaluate if some programs should be discontinued.
                    7. **New Partnerships**: Explore partnerships to enhance program value.
                    """)
                else:
                    selected_programs = active_programs
                    st.write("""
                    **General Program Optimization Strategies:**
                    
                    1. **Regular Review Cycle**: Implement quarterly program performance reviews.
                    2. **Feedback Systems**: Ensure robust feedback collection from all participants.
                    3. **Content Updates**: Schedule regular content refreshes to maintain relevance.
                    4. **Resource Allocation**: Align resource allocation with program performance and strategic importance.
                    5. **Cross-Program Learning**: Create mechanisms for sharing best practices across programs.
                    6. **Trend Monitoring**: Stay informed about industry trends and incorporate as appropriate.
                    7. **Technology Enhancement**: Regularly assess how technology can improve program delivery.
                    """)
                
                # Show list of programs in this category
                st.subheader(f"Programs in this Category ({len(selected_programs)})")
                
                # Select columns to display
                display_cols = ['name', 'program_type', 'performance_score', 'satisfaction_score', 'enrollment_rate']
                display_cols = [col for col in display_cols if col in selected_programs.columns]
                
                if not selected_programs.empty:
                    st.dataframe(selected_programs[display_cols], use_container_width=True)
                else:
                    st.write("No programs found in this category.")
            else:
                st.write("No active programs found for optimization recommendations.")
        else:
            st.write("Insufficient data to provide program optimization strategies. Please ensure program data includes performance metrics.")
    
    with tab4:
        st.header("Program Details")
        
        # Create search/filter options
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            if 'name' in program_data.columns:
                search_term = st.text_input("Search by program name", "")
        
        with col2:
            # Filter by status
            if 'status' in program_data.columns:
                status_options = ['All'] + sorted(program_data['status'].unique().tolist())
                selected_status = st.selectbox("Filter by status", status_options)
        
        # Apply filters
        filtered_data = program_data.copy()
        
        if 'name' in filtered_data.columns and search_term:
            filtered_data = filtered_data[filtered_data['name'].str.contains(search_term, case=False)]
            
        if 'status' in filtered_data.columns and selected_status != 'All':
            filtered_data = filtered_data[filtered_data['status'] == selected_status]
        
        # Display filtered programs
        st.subheader(f"Programs ({len(filtered_data)})")
        
        if not filtered_data.empty:
            # Select columns to display in the main table
            display_cols = ['program_id', 'name', 'program_type', 'status', 'start_date', 'end_date']
            
            # Add optional columns if they exist
            optional_cols = ['performance_score', 'target_audience', 'enrollment_rate']
            display_cols.extend([col for col in optional_cols if col in filtered_data.columns])
            
            # Display table with only selected columns
            display_cols = [col for col in display_cols if col in filtered_data.columns]
            st.dataframe(filtered_data[display_cols], use_container_width=True)
            
            # Program detail view
            st.subheader("Program Detail View")
            
            # Create program selector for detailed view
            program_options = dict(zip(filtered_data['name'], filtered_data.index))
            selected_program_name = st.selectbox("Select a program for detailed view", options=list(program_options.keys()))
            selected_program_idx = program_options[selected_program_name]
            
            # Get the selected program data
            program = filtered_data.iloc[selected_program_idx]
            
            # Display program details
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {program['name']}")
                st.write(f"**Program ID:** {program['program_id']}")
                st.write(f"**Program Type:** {program.get('program_type', 'N/A')}")
                st.write(f"**Status:** {program.get('status', 'N/A')}")
                st.write(f"**Start Date:** {program.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {program.get('end_date', 'N/A')}")
                st.write(f"**Target Audience:** {program.get('target_audience', 'N/A')}")
                
                if 'description' in program:
                    st.write(f"**Description:** {program['description']}")
            
            with col2:
                if 'performance_score' in program:
                    st.write(f"**Performance Score:** {program['performance_score']:.1f}/100")
                if 'satisfaction_score' in program:
                    st.write(f"**Satisfaction Score:** {program['satisfaction_score']}/10")
                if 'enrollment_rate' in program:
                    st.write(f"**Enrollment Rate:** {program['enrollment_rate']*100:.1f}%")
                if 'capacity' in program and 'current_enrollment' in program:
                    st.write(f"**Enrollment:** {program['current_enrollment']}/{program['capacity']} ({program['current_enrollment']/program['capacity']*100:.1f}%)")
                if 'budget' in program and 'expenses' in program:
                    st.write(f"**Budget:** ${program['budget']:,}")
                    st.write(f"**Expenses:** ${program['expenses']:,}")
                    budget_utilization = program['expenses'] / program['budget'] * 100
                    st.write(f"**Budget Utilization:** {budget_utilization:.1f}%")
                if 'coordinator' in program:
                    st.write(f"**Coordinator:** {program['coordinator']}")
            
            # Program metrics visualization
            st.subheader("Program Metrics")
            
            # Create a bar chart with key metrics
            metrics = {}
            
            if 'satisfaction_score' in program:
                metrics['Satisfaction'] = program['satisfaction_score'] / 10  # Normalize to 0-1
            if 'enrollment_rate' in program:
                metrics['Enrollment'] = program['enrollment_rate']
            if 'budget' in program and 'expenses' in program:
                # Budget utilization (closer to 1.0 is better)
                budget_score = 1 - abs(program['expenses'] / program['budget'] - 1)
                metrics['Budget Utilization'] = budget_score
            if 'success_metric' in program:
                metrics['Success Metric'] = program['success_metric']
                
            if metrics:
                metrics_df = pd.DataFrame({
                    'Metric': list(metrics.keys()),
                    'Value': list(metrics.values())
                })
                
                fig = px.bar(
                    metrics_df,
                    x='Metric',
                    y='Value',
                    title=f"Key Metrics for {program['name']}",
                    color='Metric',
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                
                fig.update_layout(
                    yaxis_title="Score (normalized 0-1)",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Program assessment
            st.subheader("Program Assessment")
            
            # Create assessment based on available metrics
            assessment_items = []
            
            if 'performance_score' in program:
                performance = program['performance_score']
                if performance >= 80:
                    assessment_items.append("✅ **High Performance**: This program is performing exceptionally well.")
                elif performance >= 60:
                    assessment_items.append("✓ **Moderate Performance**: This program is performing adequately but could be improved.")
                else:
                    assessment_items.append("❗ **Low Performance**: This program needs attention to improve performance.")
            
            if 'enrollment_rate' in program:
                enrollment = program['enrollment_rate']
                if enrollment >= 0.8:
                    assessment_items.append("✅ **Strong Enrollment**: This program has excellent enrollment rates.")
                elif enrollment >= 0.5:
                    assessment_items.append("✓ **Moderate Enrollment**: This program has good enrollment, but could be improved.")
                else:
                    assessment_items.append("❗ **Low Enrollment**: The enrollment rate for this program needs attention.")
            
            if 'satisfaction_score' in program:
                satisfaction = program['satisfaction_score']
                if satisfaction >= 8:
                    assessment_items.append("✅ **High Satisfaction**: Participants report high satisfaction with this program.")
                elif satisfaction >= 6:
                    assessment_items.append("✓ **Moderate Satisfaction**: Participant satisfaction is good but could be improved.")
                else:
                    assessment_items.append("❗ **Low Satisfaction**: Participant satisfaction needs to be addressed.")
            
            if 'budget' in program and 'expenses' in program:
                budget_ratio = program['expenses'] / program['budget']
                if 0.9 <= budget_ratio <= 1.1:
                    assessment_items.append("✅ **Good Budget Management**: Expenses are well aligned with budget.")
                elif budget_ratio > 1.1:
                    assessment_items.append(f"❗ **Over Budget**: Program is {(budget_ratio-1)*100:.1f}% over budget.")
                elif budget_ratio < 0.7:
                    assessment_items.append(f"⚠️ **Underutilized Budget**: Program is significantly under budget ({budget_ratio*100:.1f}%).")
            
            # Display assessment items
            if assessment_items:
                for item in assessment_items:
                    st.write(item)
            else:
                st.write("Insufficient data for detailed program assessment.")
            
            # Recommendations for this program
            st.subheader("Recommendations")
            
            # Generate recommendations based on program data
            recommendations = []
            
            if 'performance_score' in program and program['performance_score'] < 60:
                recommendations.append("**Performance Review**: Conduct a thorough program review to identify improvement areas.")
            
            if 'enrollment_rate' in program and program['enrollment_rate'] < 0.5:
                recommendations.append("**Enrollment Boost**: Enhance marketing and outreach to increase participation.")
            
            if 'satisfaction_score' in program and program['satisfaction_score'] < 7:
                recommendations.append("**Satisfaction Improvement**: Gather detailed participant feedback to address satisfaction issues.")
            
            if 'budget' in program and 'expenses' in program:
                budget_ratio = program['expenses'] / program['budget']
                if budget_ratio > 1.1:
                    recommendations.append("**Budget Review**: Review expenses and adjust budget planning for future iterations.")
                elif budget_ratio < 0.7:
                    recommendations.append("**Resource Allocation**: Evaluate if resources are being underutilized or could be better allocated.")
            
            if 'status' in program and program['status'] == 'Active' and 'end_date' in program:
                try:
                    days_remaining = (program['end_date'] - datetime.now()).days
                    if days_remaining < 30 and days_remaining > 0:
                        recommendations.append(f"**End of Program Planning**: Program ends in {days_remaining} days. Plan for evaluation and potential renewal.")
                except:
                    pass
            
            if recommendations:
                for rec in recommendations:
                    st.write(f"- {rec}")
            else:
                st.write("No specific recommendations at this time.")
        else:
            st.write("No programs found with the selected filters.")

if __name__ == "__main__":
    app()
