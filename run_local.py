from mcp_server import mcp

if __name__ == "__main__":
    # Run the MCP server using standard input/output
    # This is used for local integration with Claude Desktop, Cursor, etc.
    mcp.run(transport='stdio')
