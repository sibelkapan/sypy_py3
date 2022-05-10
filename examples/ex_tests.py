#    SyPy: A Python framework for evaluating graph-based Sybil detection
#    algorithms in social and information networks.
#
#    Copyright (C) 2013  Yazan Boshmaf
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
sys.path.append("../")

import sypy

GLOBAL_SEED="SyPyIsCool!"

if __name__ == "__main__":

    sybil_region = sypy.Region(
        graph = sypy.PowerLawGraph(
            num_nodes=5000,
            node_degree=4,
            prob_triad=0.5,
            seed=GLOBAL_SEED
        ),
        name = "SybilCompleteGraph",
        is_sybil=True
    )
    sybil_stats = sybil_region.get_region_stats()
    assert sybil_stats.is_connected == True

    honest_region = sypy.Region(
        graph=sypy.PowerLawGraph(
            num_nodes=10000,
            node_degree=4,
            prob_triad=0.5,
            seed=GLOBAL_SEED
        ),
        name="HonestPowerLawGraph",
        seed=GLOBAL_SEED
    )

    max_degree = 0
    max_node = 0
    for node in honest_region.graph.nodes():
        degree = honest_region.graph.structure.degree(node)
        if degree > max_degree:
            max_degree = degree
            max_node = node

    honest_region.pick_random_honest_nodes(num_nodes=49)
    if max_node in honest_region.known_honests:
        raise Exception("Max degree node already exists")
    honest_region.known_honests += [max_node]

    honest_stats = honest_region.get_region_stats()
    assert honest_stats.is_connected == True

    social_network = sypy.Network(
        left_region=honest_region,
        right_region=sybil_region,
        name="OnlineSocialNetwork",
        seed=GLOBAL_SEED
    )

    multi_benchmark = sypy.MultipleDetectorsBenchmark(
        detectors = [
            sypy.SybilRankDetector,
            sypy.SybilPredictDetector
        ],
        network=social_network,
        thresholds=["pivot", "pivot"],
        kwargs=[
            {
                "total_trust": social_network.graph.order(),
                "num_iterations_scaler": 1.0,
                "seed": GLOBAL_SEED
            },
            {
                "total_trust": social_network.graph.order(),
                "num_iterations_scaler": 1.0,
                "operation_mode": "best",
                "seed": GLOBAL_SEED
            }
        ]
    )

    edges_benchmark = sypy.AttackEdgesDetectorsBenchmark(
        multi_benchmark=multi_benchmark,
        values=[1] + [i*100 for i in range(1,21)]
    )
    edges_benchmark.run()
    edges_benchmark.plot_curve(file_name="attack_edge_vs_auc")

    answer = input("Visualize [y/n]: ")
    if answer == "y":
        print("This will take some time...")
        social_network.visualize()
