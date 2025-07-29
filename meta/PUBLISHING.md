# Publishing Aditi to PyPI

## Quick Steps

1. **Install publishing tools** (if not already installed):
   ```bash
   pip install -r requirements-publish.txt
   ```

2. **Set up PyPI credentials**:
   - Create an account at https://pypi.org
   - Generate an API token at https://pypi.org/manage/account/token/
   - Copy `.pypirc.template` to `~/.pypirc` and add your token
   - Secure the file: `chmod 600 ~/.pypirc`

3. **Run the publishing script**:
   ```bash
   ./scripts/publish-to-pypi.sh
   ```

## Manual Steps

If you prefer to publish manually:

1. **Build the package**:
   ```bash
   rm -rf dist/ build/ src/*.egg-info
   python -m build
   ```

2. **Test locally** (optional):
   ```bash
   ./scripts/test-package-install.sh
   ```

3. **Upload to TestPyPI** (recommended):
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```
   
   Test installation:
   ```bash
   pip install -i https://test.pypi.org/simple/ aditi
   ```

4. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

## Post-Publishing

1. **Verify installation**:
   ```bash
   pip install --upgrade aditi
   aditi --version
   ```

2. **Create GitHub release**:
   - Tag: `v0.1.0`
   - Title: "Aditi v0.1.0 - Initial Release"
   - Attach the wheel and source distribution from `dist/`
   - Include CHANGELOG content in release notes

3. **Update version** for next release in `pyproject.toml`

## Current Package Status

- **Package Name**: aditi
- **Version**: 0.1.0
- **Python Support**: 3.11+
- **License**: MIT
- **Homepage**: https://rolfedh.github.io/aditi/
- **Repository**: https://github.com/rolfedh/aditi