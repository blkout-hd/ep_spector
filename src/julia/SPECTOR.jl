# SPECTOR Julia Package
# Semantic Pipeline for Entity Correlation and Topological Organization Research
# Fixed: removed deprecated LightGraphs, non-existent Async pkg, wrong TSNE casing

module SPECTOR

# Core dependencies
using DataFrames
using Statistics
using LinearAlgebra
using SparseArrays

# Graph libraries (Graphs.jl supersedes LightGraphs.jl)
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
using UMAP
using TSne  # correct registered package name (not TSNE)

# HTTP client for media probing
using HTTP
using JSON3

# Distributed computing (Async is a Base macro, not a package)
using Distributed

export SpectorGraph, probe_extensions, bfs_expand, umap_embed, suppression_score

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
    probe_extensions(base_url, extensions; timeout=10)

Probe for related media files by substituting extensions.
Only probes publicly accessible URLs. Respects rate limiting
via a configurable delay between requests.

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

                # Add nodes if not present
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
Input: n_samples x n_features matrix
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
    suppression_score(redacted, recovered)

L2 norm of embedding delta. Higher = more semantic divergence
between visible (redacted) and hidden (recovered) text layers.
"""
function suppression_score(
    redacted::Vector{Float64},
    recovered::Vector{Float64}
)::Float64
    return norm(recovered - redacted)
end

end # module SPECTOR
