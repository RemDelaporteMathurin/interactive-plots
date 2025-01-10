import system_code as tsc


def run_system(TBR, initial_inventory) -> tsc.System:

    storage = tsc.Box("Storage", initial_inventory=initial_inventory)
    plasma = tsc.Box("Plasma", generation_term=-1)
    breeder = tsc.Box("Breeder", generation_term=TBR)

    breeder.add_output(storage, 1)
    storage.add_constant_output(plasma, 1)

    my_system = tsc.System([storage, plasma, breeder])
    my_system.run(20)
    return my_system


import plotly.graph_objects as go
import numpy as np

# Create figure
fig = go.Figure()

# Add traces, one for each slider step
tbrs = np.arange(1, 1.3, 0.02)
startup_inventory = np.arange(1, 10, 1)
for tbr in tbrs:
    print(f"Running system with TBR = {tbr}")
    system = run_system(tbr, 1)

    for box in system.boxes:
        fig.add_trace(
            go.Scatter(
                visible=False,
                line=dict(width=0.5),
                stackgroup=f"{tbr}",
                name=box.name,
                x=system.t,
                y=box.inventories,
            )
        )

# Make 2 system visible
for i, _ in enumerate(system.boxes):
    fig.data[len(system.boxes) + i].visible = True

# Create and add slider
steps = []
for tbr_index, tbr in enumerate(tbrs):
    step = dict(
        method="update",
        args=[
            {"visible": [False] * len(fig.data)},
            {"title": f"TBR: {tbr:.2f}"},
        ],  # layout attribute
        label=f"{tbr:.2f}",
    )
    for i in range(len(system.boxes)):
        step["args"][0]["visible"][
            tbr_index * len(system.boxes) + i
        ] = True  # Toggle traces for this TBR to "visible"
    steps.append(step)

sliders = [dict(active=1, currentvalue={"prefix": "TBR: "}, pad={"t": 50}, steps=steps)]

fig.update_layout(sliders=sliders)

# export to html
# fig.write_html("index.html")
fig.show()
