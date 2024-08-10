import instaloader
import re
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import community
from tqdm import tqdm

# Initialize Instaloader
L = instaloader.Instaloader()

# Login
USER = ''
PASSWORD = ''
L.login(USER, PASSWORD)

# Load a post
POST_URL = 'https://www.instagram.com/p/CwqU44wuHzK/?img_index=1'
post = instaloader.Post.from_shortcode(L.context, POST_URL.split('/')[-2])

# Extract comments
comments = [comment.text for comment in tqdm(post.get_comments(), desc="Extracting comments", unit=" comments")]

# Function to extract tagged usernames from a comment
def extract_usernames(comment):
    return set(re.findall(r'@([A-Za-z0-9_.]+)', comment))

# Collect all tagged usernames
all_usernames = []
for comment in tqdm(comments, desc="Processing comments", unit=" comments"):
    all_usernames.extend(extract_usernames(comment))

# Build the graph
G = nx.Graph()

# Add nodes and edges based on co-occurrence
for usernames in all_usernames:
    usernames = list(usernames)  # Convert set to list to ensure ordering
    for i in range(len(usernames)):
        for j in range(i + 1, len(usernames)):
            user1, user2 = usernames[i], usernames[j]
            if G.has_edge(user1, user2):
                G[user1][user2]['weight'] += 1
            else:
                G.add_edge(user1, user2, weight=1)

# Basic information about the network
print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

# Print connections and their weights
print("\nConnections and their weights:")
for user in G.nodes():
    connections = list(G.neighbors(user))
    if connections:
        print(f"\nUser @{user} is connected to:")
        for neighbor in connections:
            weight = G[user][neighbor]['weight']
            print(f"  @{neighbor} (weight: {weight})")

# Compute centrality measures
centrality = nx.betweenness_centrality(G)
print("\nTop 5 users by Betweenness Centrality:")
for user, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"@{user}: Betweenness Centrality = {score:.4f}")

# Compute modularity and identify communities
partition = community.greedy_modularity_communities(G)
print("\nCommunities:")
for i, comm in enumerate(partition):
    print(f"Community {i+1}: {[f'@{user}' for user in comm]}")

# Draw the network
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes
plt.figure(figsize=(12, 12))

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=50, node_color='blue')
nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
nx.draw_networkx_labels(G, pos, labels={node: f'@{node}' for node in G.nodes()}, font_size=10, font_family="sans-serif")

plt.title("Instagram User Network")
plt.show()
