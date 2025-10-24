import streamlit as st
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient

# Authenticate globally
credential = DefaultAzureCredential()

@st.cache_data(show_spinner=False)
def list_subscriptions():
    sub_client = SubscriptionClient(credential)
    # Return list of (name, id)
    return [(sub.display_name, sub.subscription_id) for sub in sub_client.subscriptions.list()]

def extract_resource_group(resource_id):
    parts = resource_id.split('/')
    try:
        rg_index = parts.index('resourceGroups') + 1
        return parts[rg_index]
    except (ValueError, IndexError):
        return None

def get_resources_by_tags(subscription_id, tags):
    resource_client = ResourceManagementClient(credential, subscription_id)
    filters = []
    for k, v in tags.items():
        if v:
            filters.append(f"tagName eq '{k}' and tagValue eq '{v}'")
    filter_query = " and ".join(filters) if filters else ""
    resources = resource_client.resources.list(filter=filter_query)
    return list(resources)

def get_resource_tags(subscription_id, resource_id):
    resource_client = ResourceManagementClient(credential, subscription_id)
    tag_response = resource_client.tags.get_at_scope(resource_id)
    return tag_response.properties.tags

st.title("Azure Tenant-wide Resource Tag Lookup Bot")

# Load subscriptions and let user select subset or all
subscriptions = list_subscriptions()
subscription_names = [name for name, _ in subscriptions]

selected_subscription_names = st.multiselect(
    "Select Azure Subscriptions (leave empty to select all)",
    options=subscription_names,
)

# Map selected sub names back to IDs
selected_subscription_ids = [
    sub_id for (name, sub_id) in subscriptions if not selected_subscription_names or name in selected_subscription_names
]

# Enter tags for filtering
st.header("Search Resources by Tag Values")
cost_id = st.text_input("CostCenter-or-OrderNumber")
owner_email = st.text_input("OwnerEmail")
service = st.text_input("Service")
sponsor = st.text_input("Sponsor")

tags = {
    "CostCenter-or-OrderNumber": cost_id,
    "OwnerEmail": owner_email,
    "service": service,
    "sponsor": sponsor,
}

# Search button triggers the resource search
if st.button("Search Resources"):
    if all(v == "" for v in tags.values()):
        st.warning("Please enter at least one tag to search")
    else:
        all_resources = []
        for sub_id in selected_subscription_ids:
            try:
                resources = get_resources_by_tags(sub_id, tags)
                for r in resources:
                    r.subscription_id = sub_id
                all_resources.extend(resources)
            except Exception as e:
                st.error(f"Error fetching resources for subscription {sub_id}: {e}")

        if not all_resources:
            st.info("No resources found with the specified tags.")
        else:
            # Group resources by resource group using extracted resource group name
            rg_dict = {}
            for r in all_resources:
                rg_name = extract_resource_group(r.id)
                rg_dict.setdefault(rg_name if rg_name else "Unknown", []).append(r)

            # Display resources grouped by resource group with expanders
            for rg, res_list in rg_dict.items():
                with st.expander(f"Resource Group: {rg}"):
                    for res in res_list:
                        st.write(f"**Resource Name:** {res.name}  ({res.type})")
                        if st.button(f"Show Tags for {res.name}", key=res.id):
                            try:
                                tags = get_resource_tags(res.subscription_id, res.id)
                                st.json(tags)
                            except Exception as e:
                                st.error(f"Failed to get tags for resource '{res.name}': {e}")

# Resource name lookup section
st.header("Lookup Resource Tags by Resource Name")
resource_name_search = st.text_input("Enter Resource Name")

if resource_name_search:
    found = False
    for sub_id in selected_subscription_ids:
        try:
            client = ResourceManagementClient(credential, sub_id)
            resources = list(client.resources.list())
            for res in resources:
                if res.name.lower() == resource_name_search.lower():
                    tags = get_resource_tags(sub_id, res.id)
                    st.write(f"Resource: {res.name} (Subscription ID: {sub_id}, Resource Group: {extract_resource_group(res.id)})")
                    st.json(tags)
                    found = True
        except Exception as e:
            st.error(f"Error during resource lookup: {e}")

    if not found:
        st.info("Resource not found.")
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")