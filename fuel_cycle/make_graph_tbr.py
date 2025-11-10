import system_code as tsc


def run_system(TBR, initial_inventory) -> tsc.System:

    storage = tsc.Box("Storage", initial_inventory=initial_inventory)
    plasma = tsc.Box("Plasma", generation_term=-1, initial_inventory=0.1)
    breeder = tsc.Box("Breeder", generation_term=TBR)
    tes = tsc.Box("TES", generation_term=0)

    breeder.add_output(tes, 1)
    tes.add_output(storage, 5)
    storage.add_constant_output(plasma, 1)

    my_system = tsc.System([storage, plasma, breeder, tes])
    my_system.run(20)
    return my_system


import plotly.graph_objects as go
import numpy as np

# Create figure
fig = go.Figure()

startup_inventory = 1
# Add traces, one for each slider step
tbrs = np.linspace(1.05, 1.3, num=30)


for tbr_index, tbr in enumerate(tbrs):
    print(
        f"Running system with TBR = {tbr} and initial inventory = {startup_inventory}"
    )
    system = run_system(tbr, startup_inventory)

    for box in system.boxes:
        if box.name == "Storage":
            idx = np.where(np.array(box.inventories) < 0)
            print(f"Index for TBR = {tbr} is {idx}")
            if len(idx[0]) > 0:
                idx = idx[0][0]
            else:
                idx = len(system.t)
            break

    for box in system.boxes:
        fig.add_trace(
            go.Scatter(
                visible=False,
                line=dict(width=0.5),
                stackgroup=f"{tbr}-{startup_inventory}",
                name=box.name,
                x=system.t[:idx],
                y=box.inventories[:idx],
            )
        )

    # add a vertical line when storage inv is twice the startup
    fig.add_shape(
        dict(
            type="line",
            x0=0,
            y0=2 * startup_inventory,
            x1=20,
            y1=2 * startup_inventory,
            line=dict(color="black", width=1, dash="dash"),
        )
    )
    # add text
    fig.add_annotation(
        x=10,
        y=2 * startup_inventory,
        text="2x startup inventory",
        showarrow=False,
        yshift=10,
    )

fig.update_xaxes(range=[0, 20], title="Time (AU)")
fig.update_yaxes(range=[0, 7], title="Tritium Inventory (AU)")

# Make initial traces visible
for i, _ in enumerate(system.boxes):
    fig.data[i].visible = True

# Create and add sliders
steps_tbr = []

for tbr_index, tbr in enumerate(tbrs):
    step = dict(
        method="update",
        args=[
            {"visible": [False] * len(fig.data)},
            {"title": f"TBR: {tbr:.3f}"},
        ],  # layout attribute
        label=f"{tbr:.3f}",
    )
    for i in range(len(system.boxes)):
        trace_index = tbr_index * len(system.boxes) + i
        # Toggle traces for this TBR to "visible"
        step["args"][0]["visible"][trace_index] = True
    steps_tbr.append(step)


sliders = [
    dict(active=0, currentvalue={"prefix": "TBR: "}, pad={"t": 50}, steps=steps_tbr),
]
fig.update_layout(sliders=sliders)

template = "plotly_dark"
for template in ["plotly_dark", "plotly", "plotly_white"]:
    fig.update_layout(template=template)
    # export to html
    fig.write_html(f"fuel_cycle_{template}.html")
fig.show()
