# RELEASE
This is a MCDR plugin repository, so use git tags to mark plugin versions.

## What's should I do

1. Make sure there's no issues with the source code and any other files in git system.

2. Commit and push (better push them) the changes of the repository.

> e.g. `feat: new features` or `fix: something`

3. Update the version informations in plugin meta file, maybe also in Python project configurations (something like pyproject.toml).

4. Commit the version changes with a `release: v<version>` message.

> e.g. If the new version is `1.0.0`, run `git commit -m "release: v1.0.0"`

5. **DO NOT PUSH NOW**, record the head 7 strings of the SHA of the release commit. Then, create a new git tag named with the version, and add a `commit <SHA>` message for it.

> e.g. If the SHA is `abc1234`, the new version is `1.0.0`, run `git tag -a 1.0.0 -m "commit abc1234"`

6. Push the version commit and the new tag to remote (GitHub).
> e.g. Run `git push origin main 1.0.0`

## What should I pay attention to

- There's no "v" in the git tag names. If you want to publish a new version release, use `1.0.0` but not `v1.0.0`.

- Before push, make sure the SHA in the message in the tag, matches the release commit's SHA.

- If something wrong happens, you may need re-push the tag, the release commit's SHA may change also, you should sync the change before push again.

- Create or remove a empty `.release` file if nothing to commit when release.

## How CI do
It will be triggered whenever any new qualifying commit is pushed to GitHub, and build artifacts then.

> Build command is very simple. After uv environment is set up, just run `mcdreforged pack` in the repository root, then the *.mcdr file is the artifact.

A qualifying commit which can trigger CI should match one of the following conditions:

- Compliant with the feat and fix types in semantic commit messages.

- Commit message include the specific mark: `[#build_this]`

- With a valid version tag like `1.0.0`, and the commit message is like `release: v1.0.0`

> It will publish a release after build.

When release is triggered, the CI should set the release title to v<version> (like `v1.0.0`) and parse the change log from [CHANGELOG](CHANGELOG.md), and replace `**#full_changelog**` with `**Full changelog**: <url>`.
> Shouldn't change the content or add extra informations to the release note!

> For `<url>`, use this [script](.github/scripts/get_link.py) to get the compare link, usage is `.github/scripts/get_link.py --compare <old_tag> <new_tag>`, or provide `<old_tag>` only for the first release version.
