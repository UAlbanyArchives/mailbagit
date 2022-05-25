# Building a release

1. Test develop
2. Bump version in `setup.py` and `mailbagit/__init__.py`
3. Build and push dev Docker image
4. PR and merge to main
5. Build and test Windows executables
6. [Tag a release](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
7. Write release notes
8. Upload Windows executables
9. Build and publish website
10. Build and push to pypi
11. Build and push prod Docker image

## Building and pushing dev Docker image

```
docker build -t ualbanyarchives/mailbagit:dev .
docker push ualbanyarchives/mailbagit:dev
```

## Build Windows executables

```
pyinstaller --onefile mailbagit.py
pyinstaller --onefile mailbagit-gui.py
```

## Build and push to pypi
```
python -m build
twine upload dist/*.gz dist/*.whl
```

## Building and pushing prod Docker image

```
docker build -t ualbanyarchives/mailbagit:latest -f Dockerfile.production .
docker push ualbanyarchives/mailbagit:latest
```