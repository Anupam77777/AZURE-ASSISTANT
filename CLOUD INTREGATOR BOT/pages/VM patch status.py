import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource.subscriptions import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from datetime import timedelta

@st.cache_resource
def get_subscriptions(_credential):
    client = SubscriptionClient(_credential)
    return list(client.subscriptions.list())

@st.cache_resource
def get_resource_groups(_credential, subscription_id):
    client = ResourceManagementClient(_credential, subscription_id)
    return list(client.resource_groups.list())

@st.cache_resource
def get_vms(_credential, subscription_id, resource_group):
    client = ComputeManagementClient(_credential, subscription_id)
    return list(client.virtual_machines.list(resource_group))

def get_vm_patch_status(compute_client, rg, vm_name):
    try:
        patch_result = compute_client.virtual_machines.begin_assess_patches(
            resource_group_name=rg, vm_name=vm_name).result()
    except Exception as e:
        return f"Error fetching patch status: {e}"

    text = f"Patch Assessment Started At: {patch_result.start_date_time}\n"
    text += f"Critical and Security Patches Pending: {patch_result.critical_and_security_patch_count}\n"
    text += f"Other Patches Pending: {patch_result.other_patch_count}\n"
    text += f"Reboot Pending: {patch_result.reboot_pending}\n"
    text += f"Operation Status: {patch_result.status}\n\n"

    if patch_result.available_patches:
        text += "Available Patches:\n"
        for patch in patch_result.available_patches:
            name = patch.name or "Unknown"
            classification = ", ".join(patch.classifications) if patch.classifications else "None"
            published = patch.published_date or "Unknown"
            text += f"- {name} | Classifications: {classification} | Published: {published}\n"
    else:
        text += "No available patches found.\n"
    return text


st.title("Azure VM Patch Status")

credential = DefaultAzureCredential()
subscriptions = get_subscriptions(credential)
sub_name_to_id = {sub.display_name: sub.subscription_id for sub in subscriptions}
subscription_name = st.selectbox("Select Subscription", options=list(sub_name_to_id.keys()))

if subscription_name:
    subscription_id = sub_name_to_id[subscription_name]
    resource_groups = get_resource_groups(credential, subscription_id)
    if resource_groups:
        rg_names = [rg.name for rg in resource_groups]
        resource_group = st.selectbox("Select Resource Group", rg_names)
        if resource_group:
            vms = get_vms(credential, subscription_id, resource_group)
            if vms:
                vm_names = [vm.name for vm in vms]
                vm_name = st.selectbox("Select VM", vm_names)
                if vm_name:
                    compute_client = ComputeManagementClient(credential, subscription_id)

                    st.header("Patch Status")
                    patch_status = get_vm_patch_status(compute_client, resource_group, vm_name)
                    st.text(patch_status)

            else:
                st.warning("No VMs found in the selected Resource Group.")
        else:
            st.warning("Please select a Resource Group.")
    else:
        st.warning("No Resource Groups found.")
else:
    st.warning("Please select a Subscription.")
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")