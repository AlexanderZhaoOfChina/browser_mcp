try:
    import modelcontextprotocol
    print(f"成功导入modelcontextprotocol模块，位置：{modelcontextprotocol.__file__}")
    
    try:
        from modelcontextprotocol.client import ClientSession
        print("成功导入ClientSession类")
    except ImportError as e:
        print(f"无法导入ClientSession类：{e}")
        
except ImportError as e:
    print(f"无法导入modelcontextprotocol模块：{e}")
    
import sys
print(f"Python搜索路径: {sys.path}") 