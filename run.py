#!/usr/local/bin/python

import dynclipy
task = dynclipy.main()

import pandas as pd
import numpy as np
import json

import pcreode

import time
checkpoints = {}

#   ____________________________________________________________________________
#   Load data                                                               ####
expression = task["expression"]
params = task["params"]

checkpoints["method_afterpreproc"] = time.time()

#   ____________________________________________________________________________
#   Infer trajectory                                                        ####
# pCreode using https://github.com/KenLauLab/pCreode/blob/master/notebooks/pCreode_tutorial.ipynb

# preprocess using pca
data_pca = pcreode.PCA(expression)
data_pca.get_pca()

pca_reduced_data = data_pca.pca_set_components(min(params["n_pca_components"],expression.shape[1]))

# calculate density
dens = pcreode.Density(pca_reduced_data)
best_guess = dens.radius_best_guess()
density = dens.get_density(radius = best_guess, mute=True)

# get downsampling parameters
noise, target = pcreode.get_thresholds( pca_reduced_data)

# run pCreode
out_graph, out_ids = pcreode.pCreode(
  data = pca_reduced_data,
  density = density,
  noise = noise,
  target = target,
  file_path = "/ti/workspace/.",
  num_runs = params["num_runs"],
  mute = True
)

# score graphs, returns a vector of ranks by similarity
graph_ranks = pcreode.pCreode_Scoring(data = pca_reduced_data, file_path = "/ti/workspace/.", num_graphs = params["num_runs"], mute=True)
# select most representative graph
gid = graph_ranks[0]

# extract cell graph
# Wrapper's note: This is actually a cluster graph and a grouping, but none of the objects contain this grouping
# the only thing that is available is a cell graph of only a subset of cells
# so we use this cell graph as milestone network, and then project all cells onto this
analysis = pcreode.Analysis(
  file_path = "/ti/workspace/.",
  graph_id = gid,
  data = pca_reduced_data,
  density = density,
  noise = noise
)

checkpoints["method_aftermethod"] = time.time()

#   ____________________________________________________________________________
#   Save output                                                             ####
dataset = dynclipy.wrap_data(cell_ids = expression.index)

# save dimred
dimred = pd.DataFrame(pca_reduced_data)
dimred["cell_id"] = expression.index
dataset.add_dimred(dimred = dimred)

# get milestone network based on cell_graph
# get the upper triangle of the adjacency, and use it to construct the network
cell_graph = pd.DataFrame(
  pcreode.return_weighted_adj(pca_reduced_data, "/ti/workspace/.", gid),
  index = expression.index[analysis.node_data_indices],
  columns = expression.index[analysis.node_data_indices],
)
cell_graph = cell_graph.where(np.triu(np.ones(cell_graph.shape)).astype(np.bool))
milestone_network = cell_graph.stack().reset_index()
milestone_network.columns = ["from", "to", "weight"]
milestone_network = milestone_network.query("weight > 0").drop("weight", 1)
milestone_network["length"] = 1
milestone_network["directed"] = False

cell_milestones = list(set(milestone_network["from"]) | set(milestone_network["to"]))

# get dimred_milestones
dimred_milestones = dimred.ix[[cell_id in cell_milestones for cell_id in dimred.cell_id]]
dimred_milestones = dimred_milestones.rename(columns={"cell_id":"milestone_id"})

# rename cells to milestones and save
dimred_milestones["milestone_id"] = ["MILESTONE_" + cell_id for cell_id in dimred_milestones["milestone_id"]]

milestone_network["from"] = ["MILESTONE_" + cell_id for cell_id in milestone_network["from"]]
milestone_network["to"] = ["MILESTONE_" + cell_id for cell_id in milestone_network["to"]]

dataset.add_dimred_projection(
  milestone_network = milestone_network,
  dimred_milestones = dimred_milestones
)

# timings
dataset.add_timings(timings = checkpoints)

dataset.write_output(task["output"])
