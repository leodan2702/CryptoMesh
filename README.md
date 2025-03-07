# CryptoMesh 

<p align="center">
<img src="images/logo.svg"/>
</p>

Crypto Mesh is a platform engineered to build secure service meshes specifically tailored for machine learning applications. By leveraging advanced cryptographic protocols alongside a robust, distributed mesh architecture, it ensures that data exchanged between machine learning services remains confidential and tamper-proof.

## Getting started

You must install the following software: 

- [Docker](https://github.com/pyenv/pyenv?tab=readme-ov-file#linuxunix)
- Poetry
    ```bash
    pip3 install poetry
    ```
- [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#linuxunix)
    ```bash
    curl -fsSL https://pyenv.run | bash
    ```


Once you get all the software, please execute the following command to install the dependencies of the project: 

```bash
poetry install
```


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

## Contributing

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
