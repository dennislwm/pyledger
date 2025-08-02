# Read the tool call data from stdin
tool_data=$(cat)

# Extract file path from the tool data (for Write and Edit tools)
file_path=$(echo "$tool_data" | grep -o '"file_path":"[^"]*"' | sed 's/"file_path":"//g' | sed 's/"//g')

# Only process if we have a file path
if [ -n "$file_path" ] && [ -f "$file_path" ]; then
    # Remove trailing whitespace from the file
    sed -i 's/[[:space:]]*$//' "$file_path"
    echo "Removed trailing spaces from: $file_path" >&2
fi