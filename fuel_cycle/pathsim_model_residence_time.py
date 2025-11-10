import pathsim
from pathsim import Simulation, Connection
import numpy as np
import matplotlib.pyplot as plt
import pathview


def make_system(tau=1):
    # Create blocks
    blocks, events = [], []

    storage_1 = pathview.custom_pathsim_blocks.Integrator(
        initial_value=2,
    )
    blocks.append(storage_1)

    tritium_burn_rate_2 = pathsim.blocks.sources.Constant()
    blocks.append(tritium_burn_rate_2)

    pumping_3 = pathsim.blocks.amplifier.Amplifier(gain=-1)
    blocks.append(pumping_3)

    adder_4_4 = pathsim.blocks.adder.Adder()
    blocks.append(adder_4_4)

    blanket_5 = pathview.custom_pathsim_blocks.Process(
        residence_time=tau,
    )
    blocks.append(blanket_5)

    tbr_6 = pathsim.blocks.amplifier.Amplifier(gain=1.1)
    blocks.append(tbr_6)

    tes_7 = pathview.custom_pathsim_blocks.Process(
        residence_time=0.1,
    )
    blocks.append(tes_7)

    scope_8_8 = pathsim.blocks.scope.Scope(
        labels=["Storage", "blanket (inv)", "TES (inv)"]
    )
    blocks.append(scope_8_8)

    # Create events

    # Create connections

    connections = [
        Connection(tritium_burn_rate_2[0], pumping_3[0]),
        Connection(pumping_3[0], adder_4_4[0]),
        Connection(adder_4_4[0], storage_1[0]),
        Connection(tritium_burn_rate_2[0], tbr_6[0]),
        Connection(tbr_6[0], blanket_5[0]),
        Connection(blanket_5["mass_flow_rate"], tes_7[0]),
        Connection(tes_7["mass_flow_rate"], adder_4_4[1]),
        Connection(storage_1[0], scope_8_8[0]),
        Connection(tes_7["inv"], scope_8_8[2]),
        Connection(blanket_5["inv"], scope_8_8[1]),
    ]

    # Create simulation
    my_simulation = Simulation(
        blocks,
        connections,
        events=events,
        Solver=pathsim.solvers.SSPRK22,
        dt=0.01,
        dt_min=1e-16,
        iterations_max=200,
        log=True,
        tolerance_fpi=1e-10,
        **{},
    )
    return my_simulation


if __name__ == "__main__":
    my_simulation = make_system(tau=1)
    my_simulation.run(10)

    # Optional: Plotting results
    blocks = my_simulation.blocks
    scopes = [block for block in blocks if isinstance(block, pathsim.blocks.Scope)]
    fig, axs = plt.subplots(
        nrows=len(scopes), sharex=True, figsize=(10, 5 * len(scopes))
    )
    for i, scope in enumerate(scopes):
        plt.sca(axs[i] if len(scopes) > 1 else axs)
        time, data = scope.read()
        # plot the recorded data
        for p, d in enumerate(data):
            lb = scope.labels[p] if p < len(scope.labels) else f"port {p}"
            plt.plot(time, d, label=lb)
        plt.legend()
    plt.xlabel("Time")
    plt.show()
