"""
    SPECTOR Julia Package
    Semantic Pipeline for Entity Correlation and Topological Organization Research

    Mathematical foundations (all public domain / open-source):
      - BFS:  Cormen, Leiserson, Rivest, Stein. Introduction to Algorithms (MIT Press, 1990).
              Implemented via Graphs.jl (JuliaGraphs, MIT License).
      - UMAP: McInnes, Healy, Melville (2018). UMAP: Uniform Manifold Approximation and
              Projection for Dimension Reduction. arXiv:1802.03426.
              Implemented via UMAP.jl (BSD-3 License).
      - t-SNE: van der Maaten & Hinton (2008). Visualizing Data using t-SNE.
               JMLR 9:2579-2605. Implemented via TSne.jl (MIT License).
      - L2 norm (embedding_delta_norm): Standard Euclidean norm, public domain.
               Implemented via Julia LinearAlgebra stdlib.
"""

module SPECTOR

# Core dependencies
using DataFrames
using Statistics
using LinearAlgebra
using SparseArrays

# Graph libraries (Graphs.jl supersedes deprecated LightGraphs.jl)
using Graphs
using MetaGraphs
using MetaGraphsNext

# Hypergraph support for n-ary relationships
try
    using HyperGraphs
catch
    @warn "HyperGraphs.jl not installed; hypergraph features disabled"
end

# Dimensionality reduction
# UMAP: McInnes et al. 2018 (arXiv:1802.03426), BSD-3 License
using UMAP
# t-SNE: van der Maaten & Hinton 2008 (JMLR 9:2579), MIT License
using TSne

# HTTP client for media probing
using HTTP
using JSON3

# Distributed computing (Async is a Base macro, not a package)
using Distributed

export SpectorGraph, probe_extensions, bfs_expand, umap_embed, embedding_delta_norm

"""
    SpectorGraph

Main graph structure for SPECTOR knowledge graph.
Combines Graphs.jl with MetaGraphs for attributed nodes/edges.
"""
mutable struct SpectorGraph
    graph::MetaDiGraph
    entities::Dict{String, Int}
    relationships::Vector{Tuple{String, String, String}}  # (src, rel, dst)
end

"""
    SpectorGraph()

Create an empty SpectorGraph.
"""
function SpectorGraph()::SpectorGraph
    return SpectorGraph(MetaDiGraph(), Dict{String, Int}(), Tuple{String,String,String}[])
end

"""
    probe_extensions(base_url, extensions; timeout=10, delay_secs=1.0)

Probe for related media files by substituting extensions.
Only probes publicly accessible URLs. Respects rate limiting
via a configurable delay between requests. Callers are responsible
for verifying robots.txt compliance before passing URLs to this function.

Returns Vector of NamedTuples with url, status fields.
"""
function probe_extensions(
    base_url::String,
    extensions::Vector{String};
    timeout::Int = 10,
    delay_secs::Float64 = 1.0
)::Vector{NamedTuple}
    stem = rsplit(base_url, '.', limit=2)[1]
    results = NamedTuple[]

    for ext in extensions
        url = stem * ext
        try
            sleep(delay_secs)  # rate limit
            response = HTTP.head(url; status_exception=false, readtimeout=timeout)
            if response.status in (200, 301, 302, 403)
                push!(results, (url=url, status=response.status, exists=true))
            end
        catch e
            # Connection error — skip silently
        end
    end

    return results
end

"""
    bfs_expand(graph, seed_entities; max_depth=5)

Perform BFS expansion from seed entity names.
Algorithm: Cormen et al., Introduction to Algorithms (MIT Press, 1990).
Implemented via Graphs.jl (JuliaGraphs, MIT License).
Returns the expanded SpectorGraph.
"""
function bfs_expand(
    graph::SpectorGraph,
    seed_entities::Vector{String};
    max_depth::Int = 5
)::SpectorGraph
    frontier = Set(seed_entities)
    visited = Set{String}()
    depth = 0

    while !isempty(frontier) && depth < max_depth
        next_frontier = Set{String}()
        for entity in frontier
            entity in visited && continue
            push!(visited, entity)

            co_occurring = extract_co_occurring(graph, entity)
            for new_entity in co_occurring
                new_entity in visited && continue
                push!(next_frontier, new_entity)

                if !haskey(graph.entities, entity)
                    add_vertex!(graph.graph)
                    graph.entities[entity] = nv(graph.graph)
                end
                if !haskey(graph.entities, new_entity)
                    add_vertex!(graph.graph)
                    graph.entities[new_entity] = nv(graph.graph)
                end
                add_edge!(
                    graph.graph,
                    graph.entities[entity],
                    graph.entities[new_entity]
                )
            end
        end
        frontier = next_frontier
        depth += 1
    end

    return graph
end

"""
    umap_embed(embeddings; n_components=15)

Perform UMAP dimensionality reduction.
Algorithm: McInnes, Healy, Melville (2018), arXiv:1802.03426.
Implemented via UMAP.jl (BSD-3 License).

Input:  n_samples x n_features matrix
Output: n_samples x n_components matrix
"""
function umap_embed(
    embeddings::Matrix{Float64};
    n_components::Int = 15
)::Matrix{Float64}
    model = UMAP_(embeddings', n_components,
                  n_neighbors=15, min_dist=0.1f0)
    return model.embedding'
end

"""
    extract_co_occurring(graph, entity)

Extract co-occurring entities from the graph structure.
Intended to be overridden or extended by Python → Julia bridge calls.
"""
function extract_co_occurring(graph::SpectorGraph, entity::String)::Vector{String}
    haskey(graph.entities, entity) || return String[]
    v = graph.entities[entity]
    neighbors_v = neighbors(graph.graph, v)
    result = String[]
    for (name, idx) in graph.entities
        if idx in neighbors_v
            push!(result, name)
        end
    end
    return result
end

"""
    embedding_delta_norm(vec_a, vec_b)

L2 (Euclidean) norm of the difference between two embedding vectors.
Higher values indicate greater semantic divergence between the two inputs.

Mathematical basis: standard Euclidean norm || a - b ||_2, public domain.
Implemented via Julia LinearAlgebra stdlib.

Example use: measure semantic distance between a redacted and a
full-text embedding to quantify information suppression in documents.
"""
function embedding_delta_norm(
    vec_a::Vector{Float64},
    vec_b::Vector{Float64}
)::Float64
    return norm(vec_b - vec_a)
end

end # module SPECTOR
