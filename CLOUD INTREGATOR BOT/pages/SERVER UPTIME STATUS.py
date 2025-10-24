import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Azure VM Availability Bot", layout="wide")
st.title("Azure VM Availability")

# ----------- Input Fields -----------
subscription_name = st.text_input("Enter Azure Subscription Name:")
resource_group = st.text_input("Enter Resource Group Name:")
vm_name = st.text_input("Enter Virtual Machine Name:")

custom_range = st.checkbox("Use Custom Time Range")
if custom_range:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.now())
else:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

# ----------- Function to get subscription ID by name -----------
def get_subscription_id_by_name(credential, sub_name):
    subscription_client = SubscriptionClient(credential)
    for sub in subscription_client.subscriptions.list():
        if sub.display_name.lower() == sub_name.lower().strip():
            return sub.subscription_id
    return None

# ----------- Metric Query Execution -----------
if st.button("Generate Availability Report"):
    if not subscription_name or not vm_name or not resource_group:
        st.warning("Please fill Subscription Name, Resource Group, and VM Name.")
    else:
        try:
            credential = DefaultAzureCredential()
            subscription_id = get_subscription_id_by_name(credential, subscription_name)
            
            if not subscription_id:
                st.error(f"Subscription '{subscription_name}' not found or inaccessible.")
            else:
                monitor_client = MonitorManagementClient(credential, subscription_id)

                resource_id = (
                    f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/"
                    f"Microsoft.Compute/virtualMachines/{vm_name}"
                )

                metrics_data = monitor_client.metrics.list(
                    resource_id,
                    timespan=f"{start_date}/{end_date}",
                    interval="PT1H",
                    metricnames="VmAvailabilityMetric",
                    aggregation="Average"
                )

                records = []
                for metric in metrics_data.value:
                    for ts in metric.timeseries:
                        for point in ts.data:
                            if point.average is not None:
                                records.append({
                                    "Timestamp": point.time_stamp,
                                    "Availability": round(point.average * 100, 2)
                                })

                df = pd.DataFrame(records)

                if df.empty:
                    st.warning("No VM availability data found (VmAvailabilityMetric not emitted yet).")
                else:
                    avg_avail = df["Availability"].mean()
                    st.metric("Average Availability (%)", round(avg_avail, 2))

                    st.line_chart(df.set_index("Timestamp")["Availability"])

        except Exception as e:
            st.error(f"Error fetching data: {e}")
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")