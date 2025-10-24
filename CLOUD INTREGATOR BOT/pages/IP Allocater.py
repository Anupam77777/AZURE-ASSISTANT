import streamlit as st
import ipaddress
import os

# Define base IP ranges for each region
REGION_IP_RANGES = {
    "west europe": ipaddress.IPv4Network("10.0.0.0/16"),
    "east us": ipaddress.IPv4Network("10.1.0.0/16"),
}

# Folder to store allocation data
DATA_FOLDER = "ip_data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Retrieve all allocated subnets for a region
def get_allocated_subnets(region: str) -> list[ipaddress.IPv4Network]:
    path = f"{DATA_FOLDER}/{region}_allocated.txt"
    subnets = []
    if os.path.exists(path):
        with open(path, "r") as file:
            for line in file:
                try:
                    subnets.append(ipaddress.IPv4Network(line.strip()))
                except ValueError:
                    continue
    return subnets

# Save a newly allocated subnet
def save_allocated_subnet(region: str, subnet: ipaddress.IPv4Network):
    path = f"{DATA_FOLDER}/{region}_allocated.txt"
    with open(path, "a") as file:
        file.write(str(subnet) + "\n")

# Allocate the next available subnet of the requested prefix
def allocate_next_subnet(region: str, prefix: int) -> ipaddress.IPv4Network | None:
    base_network = REGION_IP_RANGES[region]
    allocated = get_allocated_subnets(region)

    for subnet in base_network.subnets(new_prefix=prefix):
        if all(not subnet.overlaps(existing) for existing in allocated):
            save_allocated_subnet(region, subnet)
            return subnet

    st.error("No available subnet found within base IP range for requested prefix.")
    return None

# Streamlit UI
def main():
    st.title("Azure Region IP Subnet Allocator")

    # Show all allocated subnets
    st.header("Allocated IP Ranges by Region:")
    for region in REGION_IP_RANGES.keys():
        allocated = get_allocated_subnets(region)
        if allocated:
            for subnet in allocated:
                st.write(f"{region.title()}: {subnet}")
        else:
            st.write(f"{region.title()}: No allocations yet")

    st.markdown("---")

    region = st.selectbox("Select Azure Region", options=list(REGION_IP_RANGES.keys()))
    prefix_input = st.text_input("Enter subnet prefix length (e.g. 26 or 28)", value="28")

    if st.button("Allocate Next Subnet"):
        try:
            prefix = int(prefix_input)
            if prefix < 1 or prefix > 32:
                st.error("Subnet prefix must be between 1 and 32.")
                return
        except ValueError:
            st.error("Please enter a valid integer for subnet prefix.")
            return

        next_subnet = allocate_next_subnet(region, prefix)
        if next_subnet:
            st.success(f"Allocated IP Range: {next_subnet}")
            
st.markdown("---")
st.caption("Powered by TCS | Developed by Cloud Exponence")

if __name__ == "__main__":
    main()