#!/bin/bash

# Define the maximum depth to crawl upwards
max_depth=5

# Define the regex pattern to find environment variables
env_var_pattern='^[A-Z_][A-Z0-9_]*=.*$'

# Function to search for environment variable patterns in a file
search_file() {
    local file_path=$1
    while IFS= read -r line; do
        if [[ $line =~ $env_var_pattern ]]; then
            echo "  Match: $line"
        fi
    done < "$file_path"
}

# Function to search in each directory
search_directory() {
    local dir_path=$1
    find "$dir_path" -type f -name "*.py" | while read -r file; do
        echo "Checking file: $file"
        if grep -qE "$env_var_pattern" "$file"; then
            echo "Found a probable match in $file"
            search_file "$file"
        fi
    done
}

# Traverse upwards and search in each directory up to max_depth
current_dir=$(pwd)
current_depth=0

while [ "$current_depth" -le "$max_depth" ]; do
    echo "Searching in directory: $current_dir"
    search_directory "$current_dir"
    if [ "$current_dir" == "/" ]; then
        break
    fi
    current_dir=$(dirname "$current_dir")
    current_depth=$((current_depth + 1))
done

echo -e "\nAll probable matches found."
