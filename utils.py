import pandas as pd 
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go


def process_data(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df['Amount'] = df['Amount'].astype(float)
    return df


def main_kpi_metrics(df, median=False):
    total_spent = df['Amount'].sum() # Total amount spent overall
    num_transactions = len(df) # Total number of transactions made
    avg_transaction = df['Amount'].mean() # Average amount of transactions
    max_transaction = df.loc[df['Amount'].idxmax()] # The highest amount in one single transaction
    
    # First row of KPI metrics 
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Spent", f"${total_spent:,.2f}")
    col2.metric("Number of Transactions", num_transactions)
    col3.metric("Avg Transaction", f"${avg_transaction:,.2f}")
    
    
    # Second row of KPI metrics
    col4, col5, col6 = st.columns(3)
    col4.metric("Highest Transaction", f"${max_transaction['Amount']:,.2f}", help=f"{max_transaction['Category']}: {max_transaction['Description']}")
    
    if median:
        lowest_transaction = df['Amount'].min() # Returns the lowest transaction amount
        median_transaction = df['Amount'].median() # Returns the median amount of spending
        col5.metric("Lowest Transaction", f"${lowest_transaction:,.2f}")
        col6.metric("Median Transaction", f"${median_transaction:,.2f}")
    else:
        category_totals = df.groupby('Category')['Amount'].sum()
        category_grouped = df.groupby('Category')['Amount']
        
        top_category = category_totals.idxmax() # Returns the category name with the highest amount total
        top_amount = category_grouped.sum().max() # Returns the highest amount spent in all the categories 
        top_count = df[df['Category'] == top_category].shape[0] # Returns the number of transactions made in category
        
        least_category = category_grouped.sum().idxmin() # Returns the category name with the lowest amount total
        least_amount = category_grouped.sum().min() # Returns the smallest amount spent in all the categories 
        least_count = df[df['Category'] == least_category].shape[0] # Returns the number of transactions made in category
        
        col5.metric("Top Spending Category", top_category, help=f"Spent ${top_amount:,.2f} in {top_count} transactions")
        col6.metric("Least Spending Category", least_category, help=f"Spent ${least_amount:,.2f} in {least_count} transactions")

    
def pie_chart(df, title=False):
    if title:
        pie_chart = px.pie(df, names="Category", values="Amount",
                           title=title, hole=0.4, template='plotly_white')
    else:
        pie_chart = px.pie(df, names="Category", values="Amount",
                           hole=0.4, template='plotly_white')
    st.plotly_chart(pie_chart, use_container_width=True)
    
    
def line_chart(df):
    line_chart = px.line(df, x="Date", y="Cumulative Spending",
                             title="Cumulative Spending Over Time",
                             labels={'Cumulative Spending': 'Cumulative ($)', 'Date': 'Date'},
                             template="plotly_white")
    st.plotly_chart(line_chart, use_container_width=True)
    
    
    
def list_transactions(df):
    for i, row in df.iterrows():
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
                
    tree_map = px.treemap(df, path=['Category', 'Description'],  values='Amount',
                                title="Transactions Treemap", color='Amount',
                                color_continuous_scale='Viridis')
    tree_map.update_layout(margin=dict(t=40, l=0, r=0, b=0))
    st.plotly_chart(tree_map, use_container_width=True)
    