#!/bin/bash
read -p "Commit message (Algos): " desc
git add .
git commit -m "$desc"
git push
