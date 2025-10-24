import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import datetime

@st.cache_resource
def get_tenants(_credential):
    subscription_client = SubscriptionClient(_credential)
    return list(subscription_client.tenants.list())

@st.cache_resource
def get_subscriptions(_credential):
    subscription_client = SubscriptionClient(_credential)
    return list(subscription_client.subscriptions.list())

@st.cache_resource
def get_resource_groups(_credential, subscription_id):
    client = ResourceManagementClient(_credential, subscription_id)
    return list(client.resource_groups.list())

@st.cache_resource
def get_vms(_credential, subscription_id, resource_group):
    compute_client = ComputeManagementClient(_credential, subscription_id)
    return list(compute_client.virtual_machines.list(resource_group))

def get_vm_power_state(compute_client, rg, vm_name):
    vm_instance = compute_client.virtual_machines.get(rg, vm_name, expand="instanceView")
    statuses = vm_instance.instance_view.statuses
    return next((s.display_status for s in statuses if s.code.startswith("PowerState")), "Unknown")

def get_vm_tags(compute_client, rg, vm_name):
    vm = compute_client.virtual_machines.get(rg, vm_name)
    return vm.tags if vm.tags else {}

def get_cpu_and_memory_metrics(monitor_client, resource_id):
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=30)

    metrics_data = monitor_client.metrics.list(
        resource_id,
        timespan=f"{start_time}/{end_time}",
        interval="PT5M",
        metricnames="Percentage CPU,Available Memory Percentage",
        aggregation="Average"
    )

    cpu_values, mem_values = [], []
    for item in metrics_data.value:
        for ts in item.timeseries:
            for data in ts.data:
                if item.name.value == "Percentage CPU" and data.average is not None:
                    cpu_values.append(data.average)
                if item.name.value == "Available Memory Percentage" and data.average is not None:
                    mem_values.append(data.average)

    return cpu_values, mem_values

def vm_start(compute_client, rg, vm_name):
    op = compute_client.virtual_machines.begin_start(rg, vm_name)
    op.wait()

def vm_stop(compute_client, rg, vm_name):
    op = compute_client.virtual_machines.begin_power_off(rg, vm_name)
    op.wait()

def vm_restart(compute_client, rg, vm_name):
    op = compute_client.virtual_machines.begin_restart(rg, vm_name)
    op.wait()

st.title("Azure VM Monitor and Control")

credential = DefaultAzureCredential()

tenants = get_tenants(credential)
tenant_ids = [t.tenant_id for t in tenants]
tenant_id = st.selectbox("Select Tenant ID", options=tenant_ids)

subscriptions = get_subscriptions(credential)
sub_name_to_id = {sub.display_name: sub.subscription_id for sub in subscriptions}
subscription_name = st.selectbox("Select Subscription", options=list(sub_name_to_id.keys()))

if subscription_name:
    subscription_id = sub_name_to_id[subscription_name]

    resource_groups = get_resource_groups(credential, subscription_id)
    rg_names = [rg.name for rg in resource_groups]
    resource_group = st.selectbox("Select Resource Group", rg_names)

    if resource_group:
        vms = get_vms(credential, subscription_id, resource_group)
        vm_names = [vm.name for vm in vms]
        vm_name = st.selectbox("Select VM", vm_names)

        if vm_name:
            compute_client = ComputeManagementClient(credential, subscription_id)
            monitor_client = MonitorManagementClient(credential, subscription_id)

            power_state = get_vm_power_state(compute_client, resource_group, vm_name)
            tags = get_vm_tags(compute_client, resource_group, vm_name)
            st.markdown(f"### VM Power State: **{power_state}**")
            st.markdown("### VM Tags:")
            if tags:
                for k, v in tags.items():
                    st.write(f"- **{k}**: {v}")
            else:
                st.write("No tags available.")

            col1, col2, col3 = st.columns(3)
            if col1.button("Start VM"):
                vm_start(compute_client, resource_group, vm_name)
                st.success("Start command sent!")

            if col2.button("Stop VM"):
                vm_stop(compute_client, resource_group, vm_name)
                st.success("Stop command sent!")

            if col3.button("Restart VM"):
                vm_restart(compute_client, resource_group, vm_name)
                st.success("Restart command sent!")

            if st.button("Refresh CPU and Memory Metrics"):
                resource_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"
                cpu_data, mem_data = get_cpu_and_memory_metrics(monitor_client, resource_id)
                if cpu_data:
                    st.subheader("CPU Usage (%) Last 30 mins")
                    st.line_chart(cpu_data)
                    st.write(f"Average CPU Usage: {sum(cpu_data)/len(cpu_data):.2f}%")
                else:
                    st.warning("No CPU data found.")

                if mem_data:
                    st.subheader("Available Memory (%) Last 30 mins")
                    st.line_chart(mem_data)
                    st.write(f"Average Available Memory: {sum(mem_data)/len(mem_data):.2f}%")
                else:
                    st.warning("No Memory data found.")
        else:
            st.info("Please select a VM to see details and controls.")
    else:
        st.info("Please select a Resource Group to proceed.")
else:
    st.info("Please select a Subscription to proceed.")
    
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")