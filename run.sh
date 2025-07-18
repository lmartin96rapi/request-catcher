#!/bin/bash
set -e

docker run --rm -it -p 8086:8086 --name request-catcher request-catcher:latest 