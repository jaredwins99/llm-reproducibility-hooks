#!/usr/bin/env bash
# Tree 04: Team Topology
# Determines solo vs team project.

tree_04_walk() {
    forest_header "Team Topology"

    local topology
    topology=$(forest_select_one "Who works on this project?" \
        "solo:Just me" \
        "team:Team (2+ people)")

    SELECTIONS[team_topology]="$topology"
}
