import asyncio
from cryptomesh.db import connect_to_mongo, close_mongo_connection, get_database

async def clean_database():
    await connect_to_mongo()

    db = get_database()
    if db is None:
        print("❌ No se pudo conectar a la base de datos.")
        return

    # Obtener todas las colecciones de la base de datos
    collections = await db.list_collection_names()

    if not collections:
        print("✅ No hay colecciones en la base de datos.")
    else:
        for collection_name in collections:
            collection = db[collection_name]
            result = await collection.delete_many({})
            print(f"🗑 Colección '{collection_name}' limpiada: {result.deleted_count} documentos eliminados.")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(clean_database())



