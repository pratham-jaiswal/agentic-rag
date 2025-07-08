#!/bin/bash
cd /path/to/script
export $(cat .env | xargs)
python3 source_indexing.py >> cron.log 2>&1
