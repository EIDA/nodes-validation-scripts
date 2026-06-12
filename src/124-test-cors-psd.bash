#!/bin/env bash

source lib/nodes-tester.bash

for node in $NODE_DEFINITIONS; do
    eval $(parse_yaml "$node")
    if curl --header "origin: orfeus-eu.org" -v "https://$endpoint/eidaws/psd/1/" -o /dev/null 2>&1 | grep -q "access-control-allow-origin: *"; then
        echo "- [x] $node"
    else
        echo "- [ ] $node"
    fi
done
