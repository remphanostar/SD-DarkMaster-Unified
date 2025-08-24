import plotly.graph_objects as go
import numpy as np

# Define layers with correct colors from data
layers = [
    {"name": "Original SD-Dark App", "y": 4, "color": "#2E86AB", "components": ["Model Browser", "Download Mgr", "WebUI Integ", "Session State", "Activity Logs"]},
    {"name": "Vast.ai Enhance", "y": 3, "color": "#00D4AA", "components": ["GPU Monitor", "Resource Track", "CUDA Optim", "Instance Det", "Perf Tuning"]},
    {"name": "Docker Container", "y": 2, "color": "#F24236", "components": ["NVIDIA CUDA", "Python Deps", "Port 8501", "Port 7860", "Volume Map"]},
    {"name": "Vast.ai Infra", "y": 1, "color": "#A23B72", "components": ["GPU Instance", "SSD Storage", "High Bandwidth", "Public IP", "Cloud Mgmt"]}
]

# Create figure
fig = go.Figure()

# Add layer boxes and components
for i, layer in enumerate(layers):
    # Add layer background rectangle
    fig.add_shape(
        type="rect",
        x0=0, y0=layer["y"]-0.35,
        x1=10, y1=layer["y"]+0.35,
        fillcolor=layer["color"],
        opacity=0.2,
        line=dict(color=layer["color"], width=2)
    )
    
    # Add layer title with better positioning
    fig.add_annotation(
        x=0.5, y=layer["y"],
        text=f"<b>{layer['name']}</b>",
        showarrow=False,
        font=dict(size=16, color=layer["color"]),
        xanchor="left"
    )
    
    # Add components as rectangles with text
    for j, component in enumerate(layer["components"]):
        x_pos = 2.5 + j * 1.5
        
        # Component rectangle
        fig.add_shape(
            type="rect",
            x0=x_pos-0.6, y0=layer["y"]-0.15,
            x1=x_pos+0.6, y1=layer["y"]+0.15,
            fillcolor=layer["color"],
            opacity=0.8,
            line=dict(color="white", width=1)
        )
        
        # Component text
        fig.add_annotation(
            x=x_pos, y=layer["y"],
            text=component[:11],
            showarrow=False,
            font=dict(size=11, color="white"),
            xanchor="center"
        )

# Add connection arrows with labels
connections = [
    {"from": 4, "to": 3, "label": "Enhancement", "x": 1.5},
    {"from": 3, "to": 2, "label": "Container", "x": 1.5},
    {"from": 2, "to": 1, "label": "Deploy", "x": 1.5},
]

for conn in connections:
    # Arrow line
    fig.add_annotation(
        x=conn["x"], y=(conn["from"] + conn["to"]) / 2,
        ax=conn["x"], ay=conn["from"] - 0.35,
        axref="x", ayref="y",
        xref="x", yref="y",
        arrowhead=2, arrowsize=1.5, arrowwidth=2,
        arrowcolor="#666666",
        showarrow=True,
        text=""
    )
    
    # Connection label
    fig.add_annotation(
        x=conn["x"] - 0.3, y=(conn["from"] + conn["to"]) / 2,
        text=conn["label"],
        showarrow=False,
        font=dict(size=10, color="#666666"),
        textangle=-90
    )

# Add runtime feedback arrow (curved back)
fig.add_annotation(
    x=9.5, y=2.5,
    ax=9.5, ay=1.35,
    axref="x", ayref="y",
    xref="x", yref="y",
    arrowhead=2, arrowsize=1.5, arrowwidth=2,
    arrowcolor="#666666",
    showarrow=True,
    text=""
)

fig.add_annotation(
    x=9.5, y=3.65,
    ax=9.5, ay=2.5,
    axref="x", ayref="y", 
    xref="x", yref="y",
    arrowhead=2, arrowsize=1.5, arrowwidth=2,
    arrowcolor="#666666",
    showarrow=True,
    text=""
)

# Runtime label
fig.add_annotation(
    x=9.8, y=2.5,
    text="Runtime<br>Feedback",
    showarrow=False,
    font=dict(size=10, color="#666666"),
    xanchor="left"
)

# Add key features as callouts
features = [
    {"text": "Ports: 8501, 7860", "x": 8.5, "y": 2, "color": "#F24236"},
    {"text": "GPU Monitor", "x": 8.5, "y": 3, "color": "#00D4AA"},
    {"text": "CUDA Setup", "x": 8.5, "y": 3.2, "color": "#00D4AA"}
]

for feature in features:
    fig.add_annotation(
        x=feature["x"], y=feature["y"],
        text=feature["text"],
        showarrow=True,
        arrowhead=1,
        arrowsize=1,
        arrowcolor=feature["color"],
        font=dict(size=9, color=feature["color"]),
        bordercolor=feature["color"],
        borderwidth=1,
        bgcolor="white",
        opacity=0.8
    )

# Update layout
fig.update_layout(
    title="SD-Dark Vast.ai Integration Flow",
    xaxis=dict(range=[0, 11], showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(range=[0.5, 4.5], showgrid=False, showticklabels=False, zeroline=False),
    plot_bgcolor="white",
    showlegend=False
)

# Save the chart
fig.write_image("integration_diagram.png", width=1200, height=800)