# cryptomesh/db/reset_db.py

import asyncio
from cryptomesh.db import connect_to_mongo, get_collection, close_mongo_connection

async def clear_all():
    await connect_to_mongo()

    for name in ["services", "microservices", "functions"]:
        collection = get_collection(name)
        result = await collection.delete_many({})
        print(f"🧹 Colección '{name}' limpiada ({result.deleted_count} documentos eliminados)")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(clear_all())
