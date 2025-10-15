import streamlit as st
import pandas as pd
import plotly.express as px
from utils import process_data, main_kpi_metrics, pie_chart, line_chart, list_transactions

st.title("Personal Expenses Dashboard")

# File upload
uploaded_file = st.file_uploader("To begin please upload your monthly expense file (.csv)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = process_data(df)
    
    st.success("Your file has been uploaded and processed!")

    tab1, tab2, tab3, tab4 = st.tabs(["Overall Expenses Summary", "Monthly Spending Overview", "Category-wise Spending", "Transaction History"])
        
    with tab1:
        st.subheader("See your overall spending habits!")
        
        # KPI metrics 
        main_kpi_metrics(df, False)
    
        # Bar Chart for total spending amount each day compared
        daily_expenses = df.groupby('Date')['Amount'].sum().reset_index()
        bar_chart = px.bar(df, x="Date", y="Amount",
                           title="Total Expenses Per Day",
                           labels={'Amount': 'Total Expense ($)', 'Date': 'Date'},
                           template='plotly_white')
        st.plotly_chart(bar_chart, use_container_width=True)   
        
        # Line Chart to show the overall spending overtime to show how/where spending adds up
        df_sorted = df.sort_values('Date') # Sorts in ascending order
        df_sorted['Cumulative Spending'] = df_sorted['Amount'].cumsum() # Adds amount column 
        
        line_chart(df_sorted) 
        
        option = st.selectbox("Total Spending Distribution by Category:", ['Tree Map', 'Pie Chart'])
        
        if option == 'Tree Map':
            # Tree map of overall spending total amount by category
            tree_map = px.treemap(df, path=['Category', 'Description'],  values='Amount',
                                    color='Amount', color_continuous_scale='Viridis')
            tree_map.update_layout(margin=dict(t=40, l=0, r=0, b=0))
            st.plotly_chart(tree_map, use_container_width=True)
        
        elif option == 'Pie Chart':
            # Pie chart for total amount by category 
            category_totals = df.groupby('Category')['Amount'].sum().reset_index()
            pie_chart(category_totals, False)

    with tab2:
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        
        months_spent = sorted(df['Month'].unique()) # Get a sorted list of unique months from the DataFrame
        monthly_totals = df.groupby('Month')['Amount'].sum().reset_index() # Group the data by 'Month' and sum the 'Amount' spent each month
        
        most_expense_month = monthly_totals.loc[monthly_totals['Amount'].idxmax()] # Find the row (month) with the highest total spending
        least_expense_month = monthly_totals.loc[monthly_totals['Amount'].idxmin()] # Find the row (month) with the lowest total spending

        # KPI Metrics
        col1, col2= st.columns(2)
        col1.metric("Most Expense Month", value=most_expense_month['Month'], help=f"Total Spent: ${most_expense_month['Amount']:,.2f}")
        col2.metric("Least Expense Month", value=least_expense_month['Month'], help=f"Total Spent: ${least_expense_month['Amount']:,.2f}")
        
        # Stacked Bar Chart of Category Spending per Month
        monthly_category_totals = df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
        
        stacked_bar_chart = px.bar(monthly_category_totals, x="Month", y="Amount", color="Category",
                                   title="Monthly Expenses by Category (Stacked)", 
                                   labels={"Amount": "Total Spent($)", "Month": "Month"},
                                   barmode="stack",
                                   template="plotly_white")
        st.plotly_chart(stacked_bar_chart, use_container_width=True)

        # Select dropdown to choose what month user want graphs for
        option = st.selectbox("Choose a month:", months_spent)
        st.subheader(f"Data Visualization for Month: {option}")
        
        # Filter the dataframe for the selected month
        filtered_df = df[df['Month'] == option] 
        
        # KPI metrics 
        main_kpi_metrics(filtered_df, False)
        
        # Pie chart for total amount by category 
        category_totals = filtered_df.groupby('Category')['Amount'].sum().reset_index()
        pie_chart(category_totals, True)
        
        # Box Plot Chart for daily expenses in the month
        daily_expenses = filtered_df.groupby('Date')['Amount'].sum().reset_index()
        box_plot = px.box(daily_expenses, y="Amount", 
                          title="Distrubtion of Daily Expenses",
                          labels={'Amount': 'Daily Total Expense ($)'},
                          template="plotly_white")

        st.plotly_chart(box_plot, use_container_width=True)
        
    with tab3:
        category_totals = df.groupby('Category')['Amount'].sum().reset_index()
        chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart", "Treemap"])
        
        if chart_type == "Bar Chart":
            bar_chart = px.bar(category_totals.sort_values("Amount", ascending=False),
                            x="Amount", y="Category", orientation="h", 
                            title="Total Spending by Category",
                            labels={'Amount': 'Total Spent ($)', 'Category': 'Category'},
                            template="plotly_white",
                            text=category_totals['Amount'].apply(lambda x: f"${x:,.2f}"))
            bar_chart.update_traces(textposition='outside') 
            st.plotly_chart(bar_chart, use_container_width=True, key="bar_chart")
        
        elif chart_type=="Pie Chart":
            pie_chart(category_totals, True)
            
        elif chart_type=="Treemap":
            tree_map = px.treemap(df, path=['Category', 'Description'],  values='Amount',
                                title="Spending Distribution by Category", color='Amount',
                                color_continuous_scale='Viridis')
            tree_map.update_layout(margin=dict(t=40, l=0, r=0, b=0))
            st.plotly_chart(tree_map, use_container_width=True)

        
        category_types = sorted(df['Category'].unique()) # Gets a list of all the types of categories
        option = st.selectbox("Choose a category:", category_types)
        
        # Filter the dataframe for the selected month
        filtered_df = df[df['Category'] == option]
        
        st.subheader(f"{option} Spending Information")
        main_kpi_metrics(filtered_df, True)
        
        daily_expenses1 = filtered_df.groupby('Date')['Amount'].sum().reset_index()        
        histogram_chart = px.histogram(filtered_df, x="Amount", nbins=10,
                            title=f"Distribution of {option} Transaction Amounts",
                            labels={'Amount': 'Transaction Amount ($)'},
                            template='plotly_white')
        st.plotly_chart(histogram_chart, use_container_width=True)
        
        
    with tab4:
        option = st.selectbox("Choose Type of Transaction History:", ["Largest Transactions", "Smallest Transactions", f"Category Specific Transactions"])
        
        if option == "Largest Transactions":
            # Top 5 Transaction   
            top_5 = df.sort_values(by='Amount', ascending=False).head(5)
            st.subheader("Top 5 Most Expensive Transactions")
            list_transactions(top_5)
        
        elif option == "Smallest Transactions":
            # Smallest 5 Transaction   
            small_5 = df.sort_values(by='Amount', ascending=True).head(5)
            st.subheader("Top 5 Least Expensive Transactions")
            list_transactions(small_5)
        
        elif option == "Category Specific Transactions":
            category_select = st.multiselect("Choose Categories:", category_types)
            # Only if the user is selecting something 
            if category_select:
                # Filter dataframe for selected categories
                filtered_df = df[df['Category'].isin(category_select)]
                
                st.subheader(f"Transactions in: {', '.join(category_select)}")
            
                for i, row in filtered_df.iterrows():
                    st.markdown(
                        f"""
                        **Date:** {row['Date'].strftime('%Y-%m-%d')}  
                        **Category:** {row['Category']}  
                        **Amount:** ${row['Amount']:,.2f}  
                        **Description:** {row.get('Description', 'N/A')}
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
                    
            else:
                st.info("Please select at least one category to see transactions.")
                
                
                    
        
        
        
    