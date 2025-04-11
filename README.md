# CryptoMesh 

<p align="center">
<img src="images/logo.svg"/>
</p>
<div align=center>
<a href="https://test.pypi.org/project/mictlanx/"><img src="https://img.shields.io/badge/version-0.0.1--alpha.0-green" alt="build - 0.0.160-alpha.3"></a>
</div>
Crypto Mesh is a platform engineered to build secure service meshes specifically tailored for machine learning applications. By leveraging advanced cryptographic protocols alongside a robust, distributed mesh architecture, it ensures that data exchanged between machine learning services remains confidential and tamper-proof.



## ⚠️ Clone the repo and setup a remoto 🍴: 

1. You must clone the remote from the organization of Muyal: 
```bash
git clone git@github.com:muyal-research-group/CryptoMesh.git
```

2. You must create a fork (please check it up in the [Contribution](#contribution) section)

3. Add a new remote in your local git: 
   ```bash
   git remote add <remote_name> <ssh> 
   ```
You must select ```<remote_name>``` and you must copy the ```<ssh>``` uri in the github page of your 

<div align="center">
<img width=350 src="images/gitclone_ssh.png"/>
</div>

4. Remember to push all your commits to your ```<remote_name>``` to avoid github conflicts. 

Thats it!  let's get started 🚀

## Getting started

You must install the following software: 

- [Docker](https://github.com/pyenv/pyenv?tab=readme-ov-file#linuxunix)
- Poetry
    ```bash
    pip3 install poetry
    ```
- [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#linuxunix) (Optional)
    ```bash
    curl -fsSL https://pyenv.run | bash
    ```


Once you get all the software, please execute the following command to install the dependencies of the project: 

```bash
poetry install
```
### How to deploy database and broker

**Install docker and docker Compose:**

- Make sure Docker is installed on your system. See [Docker's installation guide](https://docs.docker.com/get-docker/) for instructions.
- Docker Compose is usually included with Docker Desktop. Otherwise, follow [Docker Compose installation instructions](https://docs.docker.com/compose/install/).

**Navigate to your project directory:**

- Open a terminal and change to the directory where your `docker-compose.yml` file is located.

**Start the services:**

- Run the following command to start both services in detached mode:
```bash
docker compose up -d
```

**Stopping the services:**
```bash
docker compose down
```


## Running the CryptoMesh Server with Poetry

Follow these steps to run the CryptoMesh server:

1. **Install Poetry (if not already installed):**
   - Follow the instructions at [Poetry Installation](https://python-poetry.org/docs/#installation).

2. **Install Project Dependencies(If not already installed):**
   - Open your terminal and navigate to the project directory (where your `pyproject.toml` file is located).
   - Run the following command to install all required dependencies:
     ```bash
     poetry install
     ```

3. **Run the Server:**
   - Start the server using Poetry's virtual environment with this command:
     ```bash
     poetry run python3 ./cryptomesh/server.py
     ```
   - This ensures that the server runs with the correct dependencies specified in your project.

4. **Access the API Endpoints:**
   - Once the server is running, you can access the API endpoints in your browser or via a tool like cURL/Postman:
     - `http://localhost:19000/api/v1/services`
     - `http://localhost:19000/api/v1/microservices`
     - `http://localhost:19000/api/v1/functions`

5. **Stopping the Server:**
   - To stop the server, press `Ctrl+C` in the terminal.

**Note:**  
Ensure that any other required services (like MongoDB) are running before starting the server.




## Running Tests

All tests for this project are located in the `tests/` folder at the root of the repository. We use [pytest](https://docs.pytest.org/) as our testing framework.

### How to Run the Tests

1. **Navigate to the project directory:**
   ```bash
   cd path/to/your/project

2. Run all tests:
    ```bash
    pytest
    ```
3. Run a specific test file: 
    ```bash
    pytest tests/test_policy_manager.py
    ```

## Contributing[](#contribution)

Please follow these steps to help improve the project:

1. **Fork the Repository:**
   - Click the "Fork" button at the top right of the repository page to create a copy under your GitHub account.

2. **Create a Feature Branch:**
   - Create a new branch from the `main` branch. Use a descriptive branch name (e.g., `feature/new-algorithm` or `bugfix/fix-issue`):
     ```bash
     git checkout -b feature/your-feature-name
     ```

3. **Make Your Changes:**
   - Implement your feature or fix the issue. Make sure to write or update tests located in the `tests/` folder as needed.

4. **Run the Tests:**
   - Verify that all tests pass by running:
     ```bash
     pytest
     ```
   - Ensure that your changes do not break any existing functionality.

5. **Commit and Push:**
   - Write clear and concise commit messages. Then push your branch to your fork:
     ```bash
     git push origin feature/your-feature-name
     ```

6. **Open a Pull Request:**
   - Navigate to the repository on GitHub and open a pull request against the `main` branch. Please include a detailed description of your changes and the motivation behind them.

7. **Review Process:**
   - Your pull request will be reviewed by the maintainers. Feedback and further changes may be requested.


## 1. Models and Entities

### a. ResourcesModel
- **Description:** Represents the computational resources allocated to system components.
- **Attributes:**
  - `cpu` (int): Number of CPU cores allocated.
  - `ram` (str): Amount of RAM allocated (e.g., `"2GB"`).

### b. StorageModel
- **Description:** Defines the storage configuration for a function.
- **Attributes:**
  - `storage_id` (str): Unique identifier.
  - `capacity` (str): Allocated storage capacity (e.g., `"10GB"`).
  - `source_path` (str): Source path.
  - `sink_path` (str): Destination path.
  - `created_at` (datetime): Creation timestamp (default: `datetime.utcnow`).

### c. RoleModel
- **Description:** Defines a role used in security policies.
- **Attributes:**
  - `role_id` (str): Unique identifier of the role.
  - `name` (str): Descriptive name of the role.
  - `description` (str): Description of the role.
  - `permissions` (List[str]): List of associated permissions.
  - `created_at` (datetime): Creation timestamp.

### d. SecurityPolicyModel
- **Description:** Establishes a security policy by referencing one or more roles.
- **Attributes:**
  - `sp_id` (str): Unique identifier for the policy.
  - `roles` (List[str]): List of role IDs corresponding to `RoleModel` records.
  - `requires_authentication` (bool): Indicates if authentication is required.
  - `created_at` (datetime): Creation timestamp.

### e. EndpointModel
- **Description:** Represents a container or execution server that deploys functions.
- **Attributes:**
  - `endpoint_id` (str): Unique identifier.
  - `name` (str): Descriptive name of the endpoint.
  - `image` (str): Container image to be used.
  - `resources` (ResourcesModel): Allocated resources.
  - `security_policy` (str): Reference to a security policy (using the `sp_id` from SecurityPolicyModel).
  - `created_at` (datetime): Creation timestamp.

### f. EndpointStateModel
- **Description:** Records the operational state of an endpoint (e.g., "warm", "cold") along with additional metadata.
- **Attributes:**
  - `state_id` (str): Unique state identifier.
  - `endpoint_id` (str): Reference to the related EndpointModel.
  - `state` (str): Current state of the endpoint.
  - `metadata` (Dict[str, str]): Additional metadata.
  - `timestamp` (datetime): Timestamp of the state record (default: `datetime.utcnow`).

### g. ServiceModel
- **Description:** Represents a service that groups microservices and has an associated security policy.
- **Attributes:**
  - `service_id` (str): Unique identifier.
  - `security_policy` (str): Reference to the security policy (`sp_id` from SecurityPolicyModel).
  - `microservices` (List[str]): List of microservice IDs that belong to this service.
  - `resources` (ResourcesModel): Allocated resources.
  - `created_at` (datetime): Creation timestamp.

### h. MicroserviceModel
- **Description:** Represents a microservice that belongs to a ServiceModel and groups multiple functions.
- **Attributes:**
  - `microservice_id` (str): Unique identifier.
  - `service_id` (str): The ServiceModel ID to which it belongs.
  - `functions` (List[str]): List of function IDs.
  - `resources` (ResourcesModel): Allocated resources.
  - `created_at` (datetime): Creation timestamp.

### i. FunctionModel
- **Description:** Represents a function (or task) that gets deployed and executed on an endpoint.
- **Attributes:**
  - `function_id` (str): Unique identifier.
  - `microservice_id` (str): Reference to the parent MicroserviceModel.
  - `image` (str): Container image used for the function.
  - `resources` (ResourcesModel): Allocated resources.
  - `storage` (str): Reference (ID) to a StorageModel.
  - `endpoint_id` (str): Reference to the EndpointModel where it is deployed.
  - `deployment_status` (str): Deployment status (e.g., "initiated", "completed", "failed").
  - `created_at` (datetime): Creation timestamp.

### j. FunctionStateModel
- **Description:** Records the real-time execution state of a function.
- **Attributes:**
  - `state_id` (str): Unique state identifier.
  - `function_id` (str): FunctionModel reference.
  - `state` (str): Current execution state (e.g., "running", "completed", "failed").
  - `metadata` (Dict[str, str]): Additional execution-related data.
  - `timestamp` (datetime): Timestamp (default: `datetime.utcnow`).

### k. FunctionResultModel
- **Description:** Stores the final result (and/or metadata) of a function's execution.
- **Attributes:**
  - `state_id` (str): Identifier used to associate with a FunctionStateModel.
  - `function_id` (str): Reference to the FunctionModel.
  - `metadata` (Dict[str, str]): Execution result and additional data.
  - `timestamp` (datetime): Timestamp (default: `datetime.utcnow`).

---

## 2. Entity Relationships

- **Security Policy and Roles:**  
  The `SecurityPolicyModel` contains a list of role IDs (in the `roles` field). These IDs refer to entries in the `RoleModel`, allowing policies to group multiple roles.

- **Endpoints and Security Policy:**  
  Each `EndpointModel` holds a `security_policy` field that contains the `sp_id` of a security policy. This links endpoints with specific security rules and restrictions.

- **Services, Microservices, and Functions:**  
  - A `ServiceModel` groups its microservices via the `microservices` field (a list of microservice IDs).
  - A `MicroserviceModel` holds a list of functions (by their `function_id`), establishing a hierarchy where services contain microservices and microservices group functions.

- **Functions and Endpoints:**  
  Each `FunctionModel` includes an `endpoint_id` field that references the EndpointModel where it is deployed, creating a direct link between functions and their operational environment.

- **State and Results Tracking:**  
  - The `EndpointStateModel` logs the operational state of endpoints.
  - The `FunctionStateModel` tracks the execution state of functions in real time.
  - The `FunctionResultModel` stores the final outcomes of function executions and can be related back to the function’s state through the `state_id`.

---



