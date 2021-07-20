//
// Created by Georgia Stuart on 5/3/21
//

#include <catch2/catch.hpp>
#include "PYOPATRA/cpp/mesh/mesh.h"

TEST_CASE("Mesh Tests", "[mesh-tests]") {
    TriangularMesh2D mesh(12, 12, {0, 3, 6, 9});

    REQUIRE(mesh.get_vertices().size() == 12);
    REQUIRE(mesh.get_water_columns().size() == 12);
    REQUIRE(mesh.get_water_column_pointer(1) != nullptr);
}