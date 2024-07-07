#!/bin/bash

read -p "Enter your username: " username
read -sp "Enter your password: " password

curl -X POST http://localhost:13337/register \
  -H "Content-Type: application/json" \
  -d '{"username": "'"$username"'", "password": "'"$password"'"}'

# Example output
# ➜  api git:(main) ✗ ./register_user.sh 
# Enter your username: admin
# Enter your password: {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIn0.IHvgsgwORcDBvvsx4OuOOiLE7ZNEe-ZFuakg97ooARo"
# }

# ➜  api git:(main) ✗ ./register_user.sh
# Enter your username: test
# Enter your password: {
#   "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InRlc3QifQ.Hh77MMePhLjWYQ_kmohEDGRkirXmjifvTBB40op5zwk"