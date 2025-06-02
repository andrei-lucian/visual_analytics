# Replace 'your_file.json' with your actual file path
with open("mc1.json", "r") as f:
    data = json.load(f)

# Extract the nodes list
nodes = data["nodes"]
links = data["links"]

# Create a DataFrame from nodes
df_nodes = pd.DataFrame(nodes)
df_links = pd.DataFrame(links)
