import os

from pymilvus import MilvusClient

# 默认使用项目内的相对路径，可用 MILVUS_URI 覆盖（原实现硬编码了本机绝对路径）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MILVUS_URI = os.getenv("MILVUS_URI", os.path.join(PROJECT_ROOT, "data", "milvus_lite.db"))

client = MilvusClient(uri=MILVUS_URI)
print(client.list_collections())