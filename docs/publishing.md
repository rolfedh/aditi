# Publishing Aditi to PyPI

This document describes how to publish Aditi to the Python Package Index (PyPI).

## Prerequisites

1. **PyPI Account**: Create an account at [https://pypi.org](https://pypi.org)
2. **API Token**: Generate an API token at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
3. **Build Tools**: Install the required tools:
   ```bash
   pip install -r requirements-publish.txt
   ```

## Configuration

1. Create `~/.pypirc` file based on `.pypirc.template`:
   ```bash
   cp .pypirc.template ~/.pypirc
   chmod 600 ~/.pypirc
   ```

2. Edit `~/.pypirc` and replace `YOUR_API_TOKEN_HERE` with your actual PyPI API token.

## Publishing Process

### Automated Publishing

Use the provided script for a guided publishing process:

```bash
./scripts/publish-to-pypi.sh
```

This script will:
- Clean previous builds
- Run tests
- Check code quality
- Build the package
- Optionally upload to TestPyPI first
- Upload to PyPI

### Manual Publishing

1. **Clean previous builds**:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   ```

2. **Build the package**:
   ```bash
   python -m build
   ```

3. **Upload to TestPyPI** (optional but recommended):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

4. **Test the package**:
   ```bash
   pip install -i https://test.pypi.org/simple/ aditi
   ```

5. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

## Post-Publishing

After publishing:

1. **Create a GitHub Release**:
   - Tag: `v0.1.0` (match the version in pyproject.toml)
   - Title: "Aditi v0.1.0"
   - Include the CHANGELOG content

2. **Update Version**: Bump the version in `pyproject.toml` for the next release

3. **Announce**: Consider announcing the release on relevant channels

## Troubleshooting

- **Authentication Error**: Ensure your API token starts with `pypi-` and is correctly set in `~/.pypirc`
- **Package Name Conflict**: If the name is taken, you'll need to choose a different name in `pyproject.toml`
- **Missing Files**: Check `MANIFEST.in` to ensure all necessary files are included