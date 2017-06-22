#!/bin/bash
curl -sS $1 | json_reformat | pygmentize -l javascript
