#!/bin/bash

# Function to process each file
process_file() {
    local file="$1"
    local indent="$2"

    # Skip .lock files
    if [[ "${file##*.}" == "lock" ]]; then
        return
    fi

    # Print file path
    echo "${indent}File: $file"

    # Print file content with additional indentation
    echo "${indent}Content:"
    sed "s/^/${indent}  /" "$file"
    echo # Add a blank line after file content
}

# Function to process directories recursively
process_directory() {
    local dir="$1"
    local indent="$2"

    # Print directory name
    echo "${indent}Directory: $dir"

    # Process all items in the directory
    for item in "$dir"/*; do
        # Skip .git, .venv, and __pycache__ directories
        if [[ "$(basename "$item")" == ".git" ||
              "$(basename "$item")" == ".venv" ||
              "$(basename "$item")" == "__pycache__" ]]; then
            continue
        fi

        if [ -d "$item" ]; then
            # Recursively process subdirectories
            process_directory "$item" "$indent  "
        elif [ -f "$item" ]; then
            # Process files
            process_file "$item" "$indent  "
        fi
    done
}

# Main script
output_file="folder_structure_with_content.txt"
start_dir="."

# Redirect output to the file
{
    echo "Folder Structure with File Contents"
    echo "===================================="
    echo
    process_directory "$start_dir" ""
} > "$output_file"

echo "Folder structure with file contents has been saved to $output_file"