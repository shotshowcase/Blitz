import streamlit as st
import plotly.graph_objects as go

def Analytics(result_df, Display_list):
    allStatuses = []
    for statuses in result_df['Shipment Status']:
        allStatuses += statuses

    st.subheader('Total Orders')
    st.write(len(result_df))

    TotalOrderBook = result_df['Price'].astype(float).sum()
    CashOnDelivery = result_df[result_df['Shipment Status'].apply(lambda x: 'REMITTED' in x)]['Price'].astype(float).sum()
    Prepaid = result_df[result_df['Shipment Status'].apply(lambda x: 'DELIVERED-PREPAID' in x)]['Price'].astype(float).sum()
    Remitted = CashOnDelivery+Prepaid
    RemittanceInitiated = result_df[result_df['Shipment Status'].apply(lambda x: 'REMITTANCE INITIATED' in x)]['Price'].astype(float).sum()
    Delivered = Remitted + RemittanceInitiated
    InTransit = result_df[result_df['Shipment Status'].apply(lambda x: 'IN TRANSIT' in x)]['Price'].astype(float).sum()
    RTOInTransit = result_df[result_df['Shipment Status'].apply(lambda x: 'RTO IN TRANSIT' in x)]['Price'].astype(float).sum()
    NDR1 = result_df[result_df['Shipment Status'].apply(lambda x: 'UNDELIVERED-1ST ATTEMPT' in x)]['Price'].astype(float).sum()
    NDR2 = result_df[result_df['Shipment Status'].apply(lambda x: 'UNDELIVERED-2ND ATTEMPT' in x)]['Price'].astype(float).sum()
    NDR3 = result_df[result_df['Shipment Status'].apply(lambda x: 'UNDELIVERED-3RD ATTEMPT' in x)]['Price'].astype(float).sum()
    Cancled = result_df[result_df['Cancel Reason'].apply(lambda x: 'customer' == x or 'fraud' == x)]['Price'].astype(float).sum()
    New = result_df[(result_df['Shipment Status'].apply(lambda x: 'NEW' in x)) & (result_df['Cancel Reason'].apply(lambda x: 'customer' == x or 'fraud' == x))]['Price'].astype(float).sum()
    NDR = NDR1+NDR2+NDR3
    for i in Display_list:
        if i[1]=='Delayed Delivery':
            Delayed = i[0]['Price'].astype(float).sum()
    Undelivered = InTransit + NDR + Delayed
    Others = TotalOrderBook - (Delivered + InTransit + Cancled + RTOInTransit + Delayed + NDR)

    # Data setup for the sunburst chart
    labels = ["TOTAL ORDERS", 'DELIVERED', 'REMITTED', 'PREPAID','COD', 'REMITTANCE INITIATED', 'UNDELIVERED', 'IN TRANSIT','NDR','NDR 1ST ATTEMPT','NDR 2ND ATTEMPT','NDR 3RD ATTEMPT','RTO IN TRANSIT','CANCLED','DELAYED DELIVERY' ,'OTHERS']
    parents = ["", "TOTAL ORDERS", "DELIVERED", "REMITTED", "REMITTED", "DELIVERED", "TOTAL ORDERS", "UNDELIVERED", "UNDELIVERED",'NDR','NDR','NDR', "TOTAL ORDERS", "TOTAL ORDERS", "UNDELIVERED", "TOTAL ORDERS"]
    values = [TotalOrderBook, Delivered, Remitted, Prepaid, CashOnDelivery, RemittanceInitiated, Undelivered, InTransit, NDR, NDR1, NDR2, NDR3, RTOInTransit, Cancled, Delayed, Others]

    # Create the sunburst chart
    fig = go.Figure(go.Sunburst(
        labels=labels, 
        parents=parents, 
        values=values, 
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentEntry:.2%}',
        marker=dict(
            pattern=dict(
                shape=["", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", ".", "."], solidity=0.9
            )
        ),
        name=''
    ))
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    # Display the chart in Streamlit
    st.plotly_chart(fig)
