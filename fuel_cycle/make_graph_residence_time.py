from pathsim_model_residence_time import make_system
from pathsim.blocks import Scope

import plotly.graph_objects as go
import numpy as np

# Create figure
fig = go.Figure()

taus = np.linspace(0.1, 3, num=20)


for tau_index, tau in enumerate(taus):
    print(f"Running system with tau = {tau}")
    system = make_system(tau=tau)
    system.run(10)

    scope = [block for block in system.blocks if isinstance(block, Scope)][0]
    time, data = scope.read()

    for p, d in enumerate(data):
        if scope.labels[p] == "Storage":
            idx = np.where(np.array(d) < 0)
            print(f"Index for tau = {tau} is {idx}")
            if len(idx[0]) > 0:
                idx = idx[0][0]
            else:
                idx = data.shape[1]
            break

    for p, d in enumerate(data):
        lb = scope.labels[p] if p < len(scope.labels) else f"port {p}"
        fig.add_trace(
            go.Scatter(
                visible=False,
                line=dict(width=0.5),
                stackgroup=f"{tau}",
                name=lb,
                x=time[:idx],
                y=d[:idx],
            )
        )

fig.update_xaxes(range=[0, 10], title="Time (AU)")
fig.update_yaxes(range=[0, 4], title="Tritium Inventory (AU)")

# Make initial traces visible
for i, _ in enumerate(data):
    fig.data[i].visible = True

# Create and add sliders
steps_tau = []


for tau_index, tau in enumerate(taus):
    step = dict(
        method="update",
        args=[
            {"visible": [False] * len(fig.data)},
            {"title": f"Tau: {tau:.3f} AU"},
        ],  # layout attribute
        label=f"{tau:.3f}",
    )
    for i, _ in enumerate(data):
        trace_index = tau_index * len(data) + i
        # Toggle traces for this tau to "visible"
        step["args"][0]["visible"][trace_index] = True
    steps_tau.append(step)


sliders = [
    dict(
        active=0,
        currentvalue={"prefix": "Tau: "},
        pad={"t": 50},
        steps=steps_tau,
    ),
]
fig.update_layout(sliders=sliders)

template = "plotly_dark"
for template in ["plotly_dark", "plotly", "plotly_white"]:
    fig.update_layout(template=template)
    # export to html
    fig.write_html(f"fuel_cycle_residence_time_{template}.html")
fig.show()
