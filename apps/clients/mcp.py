from django_mcp import mcp_app as mcp  
  
@mcp.tool()  
def add(a: int, b: int) -> int:  
    """Add two numbers"""  
    return a + b  
  
@mcp.resource("greeting://{name}")  
def get_greeting(name: str) -> str:  
    """Get a personalized greeting"""  
    return f"Hello, {name}!"