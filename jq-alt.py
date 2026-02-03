#!/usr/bin/env python3
"""
jq alternative for JSON parsing - Sebastian's Task Hub
Usage: python3 jq-alt.py 'query' file.json
"""

import json
import sys
import re

def jq_alt(query, data):
    """Simple jq alternative for basic JSON queries"""
    try:
        # Handle different query patterns
        if query == '.':
            return data
        elif query.startswith('.'):
            # Simple dot notation
            keys = query[1:].split('.')
            result = data
            for key in keys:
                if isinstance(result, dict) and key in result:
                    result = result[key]
                elif isinstance(result, list) and key.isdigit():
                    result = result[int(key)]
                else:
                    return None
            return result
        elif '[' in query and ']' in query:
            # Array access
            match = re.match(r'(.+)\[(\d+)\]', query)
            if match:
                base_query = match.group(1)
                index = int(match.group(2))
                base_data = jq_alt(base_query, data)
                if isinstance(base_data, list) and index < len(base_data):
                    return base_data[index]
        
        return None
    except Exception as e:
        print(f"Error in query '{query}': {e}", file=sys.stderr)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 jq-alt.py 'query' [file.json]", file=sys.stderr)
        sys.exit(1)
    
    query = sys.argv[1]
    
    try:
        # Read JSON from file or stdin
        if len(sys.argv) > 2:
            with open(sys.argv[2], 'r') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
        
        result = jq_alt(query, data)
        
        if result is not None:
            print(json.dumps(result, indent=2))
        else:
            print("null")
            
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {sys.argv[2]}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()