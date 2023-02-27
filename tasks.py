# -*- encoding: utf-8 -*-
from pathlib import Path

from invoke import task

@task()
def black(c):
    """执行 black 格式化命令"""
    print("-" * 5, "black", "-" * 5)
    c.run("black ./src ./tests")


@task()
def isort(c):
    """执行 isort 命令"""
    print("-" * 5, "isort", "-" * 5)
    c.run("isort ./src ./tests")


@task()
def flake(c):
    """执行 flake8 代码检查"""
    print("-" * 5, "flake", "-" * 5)
    c.run("flake8 ./src ./tests")


@task()
def pylint(c):
    """执行 pylint 代码检查"""
    print("-" * 5, "pylint", "-" * 5)
    c.run("pylint ./src ./tests --exit-zero")


@task(black, isort, flake, default=True)
def check(c):
    print("-" * 5, "check finish!", "-" * 5)


@task()
def doc(c, no_browser=False):
    """构建 sphinx-doc"""
    print("=" * 5, "run doc", "=" * 5)
    with c.cd("docs"):
        c.run("make html")
    if not no_browser:
        import webbrowser

        index = Path(__file__).parent / "docs" / "_build" / "html" / "index.html"
        index.absolute()
        webbrowser.open(f"file:///{index.absolute()}", encoding="utf-8")
