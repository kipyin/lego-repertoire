from invoke import task


@task
def format(c):
    c.run("poetry run isort -rc .")
    c.run("poetry run black .")


@task
def serve(c):
    c.run("cd docs", hide=True)
    c.run("bundle exec jekyll serve")


@task
def feature(c, name):
    """Start a new feature."""
    if c.run(f"git branch | grep feature/{name}", hide=True):
        c.run(f"git flow feature finish {name}")
    else:
        c.run(f"git flow feature start {name}")


@task(help={"version": "Version of the next release."})
def release(c, version, site_config_path="docs/_config.yml"):
    """Automatically create a release branch, bump the version, and
    finish the release.
    """
    if c.run(f"git branch | grep release/{version}", hide=True).failed:

        from yaml import safe_load, dump

        c.run(f"git flow release start {version}")
        c.run(f"poetry version {version}")

        site_config = safe_load(open(site_config_path, "r"))
        site_config["version"] = version
        dump(site_config, open(site_config_path, "w"))
        print(f"The site is bumped to {version}.")

        c.run("poetry lock")

        print("Testing the package...")
        c.run("poetry run tox -q")

    if c.run("git status", hide=True).failed:
        c.run(f"git commit -a -m 'Bump version to {version}'")

    c.run(f"git flow release finish {version} -m 'v{version}'")
