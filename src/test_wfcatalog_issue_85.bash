#!/bin/env bash

source lib/nodes-tester.bash

for node in $NODE_DEFINITIONS; do
    eval $(parse_yaml "$node")
    POST_DATA="$onlineCheck_net $onlineCheck_sta $onlineCheck_loc $onlineCheck_cha $onlineCheck_start $onlineCheck_end"
    if http -F -q --check-status "$endpoint/eidaws/wfcatalog/1/query" <<<$POST_DATA >/dev/null 2>&1; then
        echo "- [x] $node"
    else
        echo "- [ ] $node"
    fi
done
