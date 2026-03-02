using Test
using Pkg
Pkg.activate(joinpath(@__DIR__, "../.."))

include("../../src/julia/SPECTOR.jl")
using .SPECTOR

@testset "SPECTOR.jl Tests" begin

    @testset "SpectorGraph construction" begin
        g = SpectorGraph()
        @test isa(g, SpectorGraph)
        @test isempty(g.entities)
        @test isempty(g.relationships)
    end

    @testset "suppression_score (embedding_delta_norm)" begin
        a = [1.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0]
        score = suppression_score(a, b)
        @test isapprox(score, sqrt(2.0), atol=1e-8)
        # Same vectors -> zero divergence
        @test suppression_score(a, a) == 0.0
        # Scaling
        c = [2.0, 0.0, 0.0]
        @test suppression_score([0.0, 0.0, 0.0], c) == 2.0
    end

    @testset "bfs_expand base case" begin
        g = SpectorGraph()
        result = bfs_expand(g, ["Alice", "Bob"], max_depth=2)
        @test isa(result, SpectorGraph)
    end

    @testset "probe_extensions offline fallback" begin
        results = probe_extensions(
            "http://localhost:19999/doc.pdf",
            [".mp4", ".jpg"],
            timeout=1,
            delay_secs=0.0,
        )
        @test isa(results, Vector)
    end

end
