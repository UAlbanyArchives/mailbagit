# Mailbagit Branching Workflow

## Find an Issue

* Review the [project](https://github.com/UAlbanyArchives/mailbagit/projects/1)
* Select an [issue](https://github.com/UAlbanyArchives/mailbagit/issues)
* Identify the Issue number

<img src="persona_images/issue_number.png" alt="Screenshot showing where the issue number is on Github" width="500px"/>

## Viewing Branches

* View local branches

```bash
git branch
```

* View local and remote branches

```bash
git branch -a
```

## Creating a new feature to address the issue

1. Move the issue to "in progress" in the [project](https://github.com/UAlbanyArchives/mailbagit/projects/1)
2. Create a new branch named `feature-[issue number]`

```bash
git checkout -b feature-[issue number]
```

3. Edit the branch locally
4. Run local tests

```bash
black .
pytest
```

5. Push branch to remote

```bash
git push origin feature-[issue number]
```

6. [Create a Pull Request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) from your branch to develop
7. Move the Issue in the [project](https://github.com/UAlbanyArchives/mailbagit/projects/1) to "Ready for Review"

## Reviewing 

1. View the "Ready for Review" column in the [project](https://github.com/UAlbanyArchives/mailbagit/projects/1) and identify the issue number
2. View the original [issue](https://github.com/UAlbanyArchives/mailbagit/issues) and the [pull request](https://github.com/UAlbanyArchives/mailbagit/pulls)
3. Checkout the 

```bash
git fetch
git checkout feature-[issue number]
```

4. Review the code and ensure it effectively addresses the issue
5. Run local tests

```bash
black .
pytest
```

6. Merge the branch to develop

```bash
git checkout develop
git merge feature-[issue number]
```

7. Move Move the Issue in the [project](https://github.com/UAlbanyArchives/mailbagit/projects/1) to "Reviewer Approved"