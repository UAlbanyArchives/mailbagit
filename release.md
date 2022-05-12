# Building a release

1. Test develop
2. Bump version in `setup.py` and `mailbagit/__init__.py`
3. Build and push dev Docker image
4. PR and merge to main
5. Build and publish website
6. Build and push to pypi
7. Build and push prod Docker image

## Building and pushing dev Docker image

```
docker build -t ualbanyarchives/mailbagit:dev .
docker push ualbanyarchives/mailbagit:dev
```

## Build and push to pypi
```
python -m build
twine upload dist/*
```

## Building and pushing prod Docker image

```
docker build -t ualbanyarchives/mailbagit:latest -f Dockerfile.production .
docker push ualbanyarchives/mailbagit:latest
```