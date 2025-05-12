try:
    from mcp.client import ClientSession
    print("成功导入 mcp.client.ClientSession")
except ImportError as e:
    print(f"导入失败: {e}")