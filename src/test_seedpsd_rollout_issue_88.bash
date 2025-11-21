#!/usr/bin/env bash

source lib/nodes-tester.bash

for node in $NODE_DEFINITIONS; do
    eval $(parse_yaml "$node")
    if http -F -q --check-status "$endpoint/eidaws/psd/1/" >/dev/null 2>&1; then
        echo "- [x] $node"
    else
        echo "- [ ] $node"
    fi
done
