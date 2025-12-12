#!/bin/env bash

source lib/nodes-tester.bash

for node in $NODE_DEFINITIONS; do
    eval $(parse_yaml "$node")
    echo "=== $node ==="
    echo "===== stations ====="
    time (wget -qO- "$endpoint/fdsnws/station/1/query?level=station&format=text" | wc -l)
    echo "===== channels ====="
    time (wget -qO- "$endpoint/fdsnws/station/1/query?level=channel&format=text" | wc -l)
done
