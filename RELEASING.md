# Releasing

**Alpha:** versions use PEP 440 pre-releases, e.g. `0.1.0a1`, `0.1.0a2`. Git tags use a `v` prefix: `v0.1.0a1`.

## Steps

1. Bump **`pyproject.toml`** `[project] version` (single source for packages built with Hatch).
2. Align **`glama.json`** `"version"` and **`web_sota/package.json`** `"version"` (npm semver: `0.1.0-alpha.N`).
3. Update **`CHANGELOG.md`**.
4. Commit and push to `main`.
5. Tag and push:

   ```powershell
   git tag v0.1.0a1
   git push origin v0.1.0a1
   ```

6. **GitHub Actions** (`.github/workflows/release.yml`) runs tests, `uv build`, and attaches **`dist/*`** to the release with generated notes.

Runtime **`openmanus_mcp.__version__`** comes from installed metadata (`importlib.metadata.version("openmanus-mcp")`), so it matches the wheel/sdist after `uv sync` or install.

## Notes

- Tag name should match the release you intend (e.g. `v0.1.0a1` for alpha 1).
- PyPI publish is **not** automated here; add a trusted publisher or `uv publish` job when you are ready for public index uploads.
