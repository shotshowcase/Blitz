import pandas as pd
from datetime import datetime, timedelta

def cleanDeliveryStatus(lst):
    if len(lst)>1:
        return [status for status in lst if status != 'CANCELED']
    else:
        return lst
    
def cleanActivities(lst):
        split_list = ' '.join(lst).split('                                                         ')
        # st.write(split_list)
        if len(split_list)>2:
            for i in split_list:
                if 'ORDER_CANCELLED' not in i:
                    return i.strip().split(' ')
        else:
            return split_list[0].split(' ')
        
def Process_Data(df_shopify,df_shiprocket):
    df_shopify['OrderID'] = df_shopify['OrderID'].astype(str)
    df_shiprocket['OrderID'] = df_shiprocket['OrderID'].astype(str)
    Display_list = []

    result_df = pd.merge(df_shopify, df_shiprocket, on='OrderID', how='right')
    result_df.set_index('OrderID', inplace=True)

    descripent =result_df.loc[result_df['Shipment Status'].apply(lambda x: len(x) - x.count('CANCELED')>1)]
    twiking_df = result_df[~result_df.index.isin(descripent.index)]
    twiking_df['Shipment Status'] = twiking_df['Shipment Status'].apply(cleanDeliveryStatus)
    twiking_df['Activities'] = twiking_df['Activities'].apply(cleanActivities)

    def cleanDates(columnName, Year_first):
        if Year_first:
            twiking_df[columnName] = twiking_df[columnName].apply(lambda dates: [pd.to_datetime(date, errors='coerce', format='%Y-%m-%d %H:%M:%S') for date in dates])
        else:
            twiking_df[columnName] = twiking_df[columnName].apply(lambda dates: [pd.to_datetime(date, errors='coerce', format='%d-%m-%Y %H:%M:%S') for date in dates])
        twiking_df[columnName] = twiking_df[columnName].apply(lambda dates: [date for date in dates if not pd.isnull(date)])
        twiking_df[columnName] = twiking_df[columnName].apply(lambda dates: max(dates, default=''))

    cleanDates('Pickup Scheduled Date',True)
    twiking_df['Pickedup Date'] = twiking_df['Pickedup Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    twiking_df['Shipped Date'] = twiking_df['Shipped Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    cleanDates('Estimated Delivery Date',False)
    twiking_df['Out For Delivery Date'] = twiking_df['Out For Delivery Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    twiking_df['Delivered Date'] = twiking_df['Delivered Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    twiking_df['Remittance Date'] = twiking_df['Remittance Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    cleanDates('RTO Delivered Date',True)
    cleanDates('RTO Initiated Date',True)
    twiking_df['RTO Estimated Delivery Date'] = twiking_df['RTO Estimated Delivery Date'].apply(lambda dates: ''.join(str(date) for date in dates if date is not None).strip())
    twiking_df.fillna('',inplace=True)

    twiking_df['Created On'] = pd.to_datetime(twiking_df['Created On']).dt.tz_localize(None)
    twiking_df['Delay in Pickup Schedule'] = (datetime.now() - twiking_df['Created On'])
    delayed_df = twiking_df[(twiking_df['Delay in Pickup Schedule'] > timedelta(days=2)) & (twiking_df['Pickup Scheduled Date'] == '') & (twiking_df['Cancel Reason'] != 'customer') & (twiking_df['Cancel Reason'] != 'fraud') & (twiking_df['Tags'].apply(lambda x: 'RESOLVED' not in x))]
    DelayInPickupScheduledCount = len(delayed_df)
    header = 'Delay In Pickup Scheduled'
    help = "Orders that was created two days ago on Shopify and still need scheduling for pickup on Shiprocket. Please address this promptly to avoid delays."
    simplifyColumns = ['Name','Payment Type','Price','Created On','Delay in Pickup Schedule','Product']
    delayed_df['Remarks'] = 'Delay in Pickup Schedule'
    Display_list.append([delayed_df,header,DelayInPickupScheduledCount,help,simplifyColumns])

    twiking_df['Pickup Scheduled Date'] = pd.to_datetime(twiking_df['Pickup Scheduled Date']).dt.tz_localize(None)
    delayed_df = twiking_df[(datetime.now() - twiking_df['Pickup Scheduled Date'] > timedelta(days=1)) & (twiking_df['Pickedup Date'] == '') & (twiking_df['Cancel Reason'] != 'customer') & (twiking_df['Cancel Reason'] != 'fraud')]
    PickupDelayedCount = len(delayed_df)
    header = 'Pickup Delayed'
    help = "Orders scheduled for pickup on Shiprocket that have not been picked up by the delivery partner for over a day. Please investigate and take necessary actions to expedite the pickup process."
    simplifyColumns = ['Name','Phone Number','AWB Number','Pickup Scheduled Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'Pickup Delayed'
    Display_list.append([delayed_df,header,PickupDelayedCount,help,simplifyColumns])

    twiking_df['Estimated Delivery Date'] = pd.to_datetime(twiking_df['Estimated Delivery Date']).dt.tz_localize(None)
    delayed_df = twiking_df[(datetime.now() - twiking_df['Estimated Delivery Date'] > timedelta(days=1)) & (twiking_df['Delivered Date'] == '') & (twiking_df['Cancel Reason'] != 'customer') & (twiking_df['Cancel Reason'] != 'fraud') & (twiking_df['Activities'].apply(lambda x: 'ORDER_RTO_INIT_BATCH' not in x ))]
    DelayedDeliveryCount = len(delayed_df)
    header = 'Delayed Delivery'
    help = "Orders that have exceeded the estimated delivery date by more than a day. Please investigate and take necessary actions to expedite the delivery process."
    simplifyColumns = ['Name','Phone Number','AWB Number','Estimated Delivery Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'Delayed Delivery'
    Display_list.append([delayed_df,header,DelayedDeliveryCount,help,simplifyColumns])

    NDR1stAttemptCount = len(twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_1' in x and 'ORDER_UNDELIVERED_2' not in x and 'ORDER_UNDELIVERED_3' not in x and 'ORDER_RTO_INIT_BATCH' not in x and 'ORDER_DELIVERED' not in x)])
    delayed_df  = twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_1' in x and 'ORDER_UNDELIVERED_2' not in x and 'ORDER_UNDELIVERED_3' not in x and 
                                                    'ORDER_RTO_INIT_BATCH' not in x and 'ORDER_DELIVERED' not in x)]
    header = 'NDR 1st Attempt'
    help = "Orders with unsuccessful delivery attempts (NDR - Non-Delivery Report) on the first try. Investigate and take necessary actions to ensure successful delivery."
    simplifyColumns = ['Name','Phone Number','AWB Number','Email','Shipment Status','Activities']
    delayed_df['Remarks'] = 'NDR 1st Attempt'
    Display_list.append([delayed_df,header,NDR1stAttemptCount,help,simplifyColumns])

    NDR2stAttemptCount = len(twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_2' in x and 'ORDER_UNDELIVERED_3' not in x and 'ORDER_RTO_INIT_BATCH' not in x and 'ORDER_DELIVERED' not in x)])
    delayed_df = twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_2' in x and 'ORDER_UNDELIVERED_3' not in x and 
                                                'ORDER_RTO_INIT_BATCH' not in x and 'ORDER_DELIVERED' not in x)]
    header = 'NDR 2nd Attempt'
    help = "Orders with unsuccessful delivery attempts (NDR - Non-Delivery Report) on the second try. Investigate and take necessary actions to ensure successful delivery."
    simplifyColumns = ['Name','Phone Number','AWB Number','Email','Shipment Status','Activities']
    delayed_df['Remarks'] = 'NDR 2nd Attempt'
    Display_list.append([delayed_df,header,NDR2stAttemptCount,help,simplifyColumns])
        
    NDR3stAttemptCount = len(twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_3' in x and  'ORDER_RTO_INIT_BATCH' not in x and 'ORDER_DELIVERED' not in x)])
    delayed_df = twiking_df[twiking_df['Activities'].apply(lambda x: 'ORDER_UNDELIVERED_3' in x and  'ORDER_RTO_INIT_BATCH' not in x and 
                                                'ORDER_DELIVERED' not in x)]
    header = 'NDR 3rd Attempt'
    help = "Orders with unsuccessful delivery attempts (NDR - Non-Delivery Report) on the third try. Investigate and take necessary actions to ensure successful delivery."
    simplifyColumns = ['Name','Phone Number','AWB Number','Email','Shipment Status','Activities']
    delayed_df['Remarks'] = 'NDR 3rd Attempt'
    Display_list.append([delayed_df,header,NDR3stAttemptCount,help,simplifyColumns])

    RTOInitiatedCount = len(twiking_df[twiking_df['Shipment Status'].apply(lambda x: 'RTO INITIATED' in x)])
    delayed_df = twiking_df[twiking_df['Shipment Status'].apply(lambda x: 'RTO INITIATED' in x)]
    header = 'RTO Initiated'
    help = "Orders marked for Return to Origin (RTO)"
    simplifyColumns = ['Name','Phone Number','AWB Number','RTO Estimated Delivery Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'RTO Initiated'
    Display_list.append([delayed_df,header,RTOInitiatedCount,help,simplifyColumns])

    RTOInTransitCount = len(twiking_df[twiking_df['Shipment Status'].apply(lambda x: 'RTO IN TRANSIT' in x)])
    delayed_df = twiking_df[twiking_df['Shipment Status'].apply(lambda x: 'RTO IN TRANSIT' in x)]
    header = 'RTO In Transit'
    help = "RTO Orders that are in transit."
    simplifyColumns = ['Name','AWB Number','RTO Estimated Delivery Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'RTO In Transit'
    Display_list.append([delayed_df,header,RTOInTransitCount,help,simplifyColumns])

    twiking_df['RTO Estimated Delivery Date'] = pd.to_datetime(twiking_df['RTO Estimated Delivery Date']).dt.tz_localize(None)
    delayed_df = twiking_df[(datetime.now() - twiking_df['RTO Estimated Delivery Date'] > timedelta(days=1)) & (twiking_df['Shipment Status'].apply(lambda x: 'RTO DELIVERED' not in x)) & (twiking_df['Shipment Status'].apply(lambda x: 'LOST' not in x))]
    DelayedRTOCount = len(delayed_df)
    header = 'Delayed RTO'
    help = "RTO Orders that have exceeded the estimated delivery date by more than a day. Please investigate and take necessary actions to expedite the delivery process."
    simplifyColumns = ['Name','AWB Number','RTO Estimated Delivery Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'Delayed RTO'
    Display_list.append([delayed_df,header,DelayedRTOCount,help,simplifyColumns])

    twiking_df['Delivered Date'] = pd.to_datetime(twiking_df['Delivered Date'], format="%d-%m-%Y %H:%M:%S").dt.tz_localize(None)
    delayed_df = twiking_df[(datetime.now() - twiking_df['Delivered Date'] > timedelta(days=5)) & (twiking_df['Shipment Status'].apply(lambda x: 'DELIVERED' in x))]
    RemittanceNotInitiatedCount = len(delayed_df)
    header = 'Remittance Not Initiated'
    help = "Orders that are delivered but the remittance is still not initiated by more than 5 days. Please investigate and take necessary actions to expedite the pickup process."
    simplifyColumns = ['Name','Phone Number','AWB Number','Delivered Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'Remittance Not Initiated'
    Display_list.append([delayed_df,header,RemittanceNotInitiatedCount,help,simplifyColumns])

    twiking_df['Remittance Date'] = pd.to_datetime(twiking_df['Remittance Date'], format="%d %b %Y").dt.tz_localize(None)
    delayed_df = twiking_df[(datetime.now() - twiking_df['Remittance Date'] > timedelta(days=1)) & (twiking_df['Shipment Status'].apply(lambda x: 'REMITTED' not in x))]
    AmountNotRemittedCount = len(delayed_df)
    header = 'Amount Not Remitted'
    help = "Orders that are initiated for remittance but the amount is still not remitted. Please investigate and take necessary actions to expedite the pickup process."
    simplifyColumns = ['Name','Phone Number','AWB Number','Remittance Date','Shipment Status','Activities']
    delayed_df['Remarks'] = 'Amount Not Remitted'
    Display_list.append([delayed_df,header,AmountNotRemittedCount,help,simplifyColumns])

    delayed_df = twiking_df[twiking_df['Activities'].apply(lambda x: 'RETURN_ORDER_CREATED' in x) & (twiking_df['Tags'].apply(lambda x: 'RESOLVED' not in x))]
    ReturnsCount = len(delayed_df)
    header = 'Returns'
    help = "Orders that have called back for return."
    simplifyColumns = ['Name','AWB Number','Shipment Status','Activities','Product','Pickup Scheduled Date','Pickedup Date','Shipped Date','Estimated Delivery Date']
    delayed_df['Remarks'] = 'Returns'
    Display_list.append([delayed_df,header,ReturnsCount,help,simplifyColumns])

    delayed_df = twiking_df[twiking_df['Shipment Status'].apply(lambda x: 'LOST' in x) & (twiking_df['Tags'].apply(lambda x: 'RESOLVED' not in x))]
    LostCount = len(delayed_df)
    header = 'Lost'
    help = "Orders that have been lost during transit."
    simplifyColumns = ['Name','AWB Number','Shipment Status','Activities','Product']
    delayed_df['Remarks'] = 'Lost'
    Display_list.append([delayed_df,header,LostCount,help,simplifyColumns])

    return descripent,result_df,Display_list

def PostProcessSheetsData(result_df,Display_list,listed_columns):
    merged_df = result_df[list(['Name', 'Shipment Status','Tags', 'Cancel Reason']+listed_columns)].copy().fillna('')
    merged_df['Remarks'] = ''
    for i, filtered_df in enumerate(Display_list):
        suffix = f'_filter_{i+1}'  # Use a unique suffix for each merge
        merged_df = pd.merge(merged_df, filtered_df[0][['Remarks']], how='left', left_index=True, right_index=True, suffixes=('', suffix))

    merged_df['Remarks'] = merged_df.iloc[:, -len(Display_list):].apply(lambda row: ' | '.join(row.dropna()), axis=1)
    merged_df = merged_df[merged_df.columns[:-len(Display_list)]]
    # Function to color code cells based on 'Shipment Status'
    def color_delivery_status(row):
        error = row.Remarks is not ''
        RTO_DELIVERED ='RTO DELIVERED' in row['Shipment Status']
        delivered ='REMITTED' in row['Shipment Status'] or 'DELIVERED-PREPAID' in row['Shipment Status']
        Resolved = 'RESOLVED' in row.Tags
        Canceled = row['Cancel Reason'] == 'customer' or row['Cancel Reason'] == 'fraud'
        return ['background-color: #336657; color: #038771' if Resolved else ('background-color: #ff5d5d; color: #ffffff' if error else ('background-color: #336657' 
                if delivered else ('background-color: #012e26; color: #025f50' if Canceled else ('background-color: #01493d; color: #038771' if RTO_DELIVERED else '')))) for _ in row]

    # Apply the color coding function to the entire DataFrame
    styled_df = merged_df.sort_index(ascending=False).style.apply(color_delivery_status, axis=1)
    return styled_df