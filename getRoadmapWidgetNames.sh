#!/bin/bash

result=$(cat forms/roadmap* | grep widget | grep class | \
	grep _ | grep -v label | grep -v groupBox | \
	grep -v _2 | grep -v _3 | grep -v _4 | grep -v _5)

echo $result
