# Building a release

1. Test develop
2. Bump version in `setup.py` and `mailbagit/__init__.py`
3. Update [Spec compliance version](https://github.com/UAlbanyArchives/mailbagit/blob/develop/mailbagit/controller.py#L114) if neccessary.
4. Build and push dev Docker image
5. PR and merge to main
6. Build and test Windows executables
7. [Tag a release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
8. Write release notes
9. Upload Windows executables
10. Build and publish website
11. Build and push to pypi
12. Build and push prod Docker image

## Building and pushing dev Docker image

```
docker build --no-cache -t ualbanyarchives/mailbagit:dev .
docker push ualbanyarchives/mailbagit:dev
```

## Build Windows executables

```
pyinstaller mailbagit.spec
pyinstaller mailbagit-gui.spec
pyinstaller mailbagit-guided.spec
```

## Build and push to pypi
```
python -m build
twine upload dist/*.gz dist/*.whl
```

## Building and pushing prod Docker image

```
docker build --no-cache -t ualbanyarchives/mailbagit:latest -f Dockerfile.production .
docker push ualbanyarchives/mailbagit:latest
```