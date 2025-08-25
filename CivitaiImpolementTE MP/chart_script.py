import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Parse the data with corrected names and better positioning
components = [
    {"name": "CivitAI API", "type": "external", "position": {"x": 1, "y": 3.5}},
    {"name": "HuggingFace API", "type": "external", "position": {"x": 1, "y": 3.5}},  # Aligned horizontally
    {"name": "Model Browser", "type": "core", "position": {"x": 2.5, "y": 4}},
    {"name": "Image Browser", "type": "core", "position": {"x": 2.5, "y": 3}},
    {"name": "Search Engine", "type": "core", "position": {"x": 2.5, "y": 2}},
    {"name": "Multi-Cat Parse", "type": "processing", "position": {"x": 4, "y": 4}},
    {"name": "Batch Download", "type": "processing", "position": {"x": 4, "y": 3}},
    {"name": "Analytics Dash", "type": "processing", "position": {"x": 4, "y": 2}},
    {"name": "Google Colab", "type": "deployment", "position": {"x": 5.5, "y": 4.2}},
    {"name": "Lightning AI", "type": "deployment", "position": {"x": 5.5, "y": 3.6}},
    {"name": "Vast.ai", "type": "deployment", "position": {"x": 5.5, "y": 3}},
    {"name": "HF Spaces", "type": "deployment", "position": {"x": 5.5, "y": 2.4}},
    {"name": "Model Files", "type": "output", "position": {"x": 7, "y": 4}},
    {"name": "Metadata", "type": "output", "position": {"x": 7, "y": 3.4}},
    {"name": "Prompt Files", "type": "output", "position": {"x": 7, "y": 2.8}},
    {"name": "Analytics Rpts", "type": "output", "position": {"x": 7, "y": 2.2}}
]

connections = [
    {"from": "CivitAI API", "to": "Model Browser"},
    {"from": "CivitAI API", "to": "Image Browser"},
    {"from": "HuggingFace API", "to": "Model Browser"},
    {"from": "Model Browser", "to": "Multi-Cat Parse"},
    {"from": "Image Browser", "to": "Batch Download"},
    {"from": "Search Engine", "to": "Analytics Dash"},
    {"from": "Multi-Cat Parse", "to": "Model Files"},
    {"from": "Batch Download", "to": "Metadata"},
    {"from": "Batch Download", "to": "Prompt Files"},  # Added missing connection
    {"from": "Analytics Dash", "to": "Analytics Rpts"},
    {"from": "Multi-Cat Parse", "to": "Google Colab"},
    {"from": "Batch Download", "to": "Lightning AI"},
    {"from": "Analytics Dash", "to": "Vast.ai"},
    {"from": "Search Engine", "to": "HF Spaces"}
]

# Adjust API positions to be horizontally aligned but offset
api_components = []
for i, comp in enumerate(components):
    if comp['type'] == 'external':
        if comp['name'] == 'CivitAI API':
            comp['position']['y'] = 3.7
        else:  # HuggingFace API
            comp['position']['y'] = 3.3
    api_components.append(comp)

components = api_components

# Create DataFrame for components
df = pd.DataFrame(components)
df['x'] = [comp['position']['x'] for comp in components]
df['y'] = [comp['position']['y'] for comp in components]

# Color mapping for different types
color_map = {
    'external': '#1FB8CD',    # Strong cyan
    'core': '#DB4545',        # Bright red  
    'processing': '#2E8B57',  # Sea green
    'deployment': '#5D878F',  # Cyan
    'output': '#D2BA4C'       # Moderate yellow
}

# Create figure
fig = go.Figure()

# Add connection lines first
component_pos = {comp['name']: (comp['position']['x'], comp['position']['y']) for comp in components}

for conn in connections:
    from_pos = component_pos[conn['from']]
    to_pos = component_pos[conn['to']]
    
    # Add connection line
    fig.add_trace(go.Scatter(
        x=[from_pos[0], to_pos[0]],
        y=[from_pos[1], to_pos[1]],
        mode='lines',
        line=dict(color='#888888', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add arrow markers at the end of each connection
for conn in connections:
    from_pos = component_pos[conn['from']]
    to_pos = component_pos[conn['to']]
    
    # Calculate direction vector
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    length = np.sqrt(dx**2 + dy**2)
    
    # Normalize and scale back from target position
    if length > 0:
        unit_x = dx / length
        unit_y = dy / length
        arrow_x = to_pos[0] - 0.15 * unit_x
        arrow_y = to_pos[1] - 0.15 * unit_y
        
        fig.add_trace(go.Scatter(
            x=[arrow_x],
            y=[arrow_y],
            mode='markers',
            marker=dict(
                symbol='triangle-right',
                size=8,
                color='#888888',
                angle=np.degrees(np.arctan2(dy, dx))
            ),
            showlegend=False,
            hoverinfo='skip'
        ))

# Add components as scatter points grouped by type
for comp_type in ['external', 'core', 'processing', 'deployment', 'output']:
    type_df = df[df['type'] == comp_type]
    if not type_df.empty:
        fig.add_trace(go.Scatter(
            x=type_df['x'],
            y=type_df['y'],
            mode='markers+text',
            marker=dict(
                color=color_map[comp_type],
                size=90,
                symbol='square',
                line=dict(width=2, color='white')
            ),
            text=type_df['name'],
            textposition='middle center',
            textfont=dict(size=11, color='white', family='Arial'),
            name=comp_type.title(),
            showlegend=True,
            cliponaxis=False,
            hovertemplate='%{text}<extra></extra>'
        ))

# Update layout
fig.update_layout(
    title='CivitAI Browser System Architecture',
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[0.5, 7.5]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[1.8, 4.5]
    ),
    legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='center', x=0.5),
    plot_bgcolor='white'
)

fig.write_image('civitai_architecture.png')