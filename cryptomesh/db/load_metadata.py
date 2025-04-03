# cryptomesh/db/load_metadata.py

import asyncio
from cryptomesh.policies import CMPolicyManager
from cryptomesh.db import connect_to_mongo, get_collection, close_mongo_connection

async def main():
    await connect_to_mongo()

    services_collection = get_collection("services")
    microservices_collection = get_collection("microservices")
    functions_collection = get_collection("functions")

    manager = CMPolicyManager()
    policy = manager.interpret()

    for service_id, service in policy.services.items():
        service_dict = service.model_dump(exclude_unset=True)
        service_dict["id"] = service_id

        # Insertar servicio con microservicios anidados
        service_result = await services_collection.insert_one(service_dict)
        service_db_id = str(service_result.inserted_id)
        print(f"✅ Servicio '{service_id}' insertado con ID: {service_db_id}")

        for ms_name, micro in service.microservices.items():
            micro_dict = micro.model_dump(exclude_unset=True)
            micro_dict["name"] = ms_name
            micro_dict["service_id"] = service_id
            micro_dict["microservice_id"] = f"{service_id}_{ms_name}"

            ms_result = await microservices_collection.insert_one(micro_dict)
            micro_id = str(ms_result.inserted_id)
            print(f"  📦 Microservicio '{ms_name}' insertado con ID: {micro_id}")

            for fn_name, fn in micro.functions.items():
                fn_dict = fn.model_dump(exclude_unset=True)
                fn_dict["function_id"] = f"{micro_dict['microservice_id']}_{fn_name}"
                fn_dict["microservice_id"] = micro_dict["microservice_id"]
                fn_dict["service_id"] = service_id

                await functions_collection.insert_one(fn_dict)
                print(f"    🔧 Función '{fn_name}' insertada con ID: {fn_dict['function_id']}")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())


