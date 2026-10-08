from pymilvus import MilvusClient

client = MilvusClient(uri="/home/t/data/llm/myrag/data/content.db")
print(client.list_collections())