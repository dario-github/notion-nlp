# -*- encoding: utf-8 -*-
from pathlib import Path

from invoke import task

PROJECT_ROOT_DIR = Path(__file__).parent
MAIN_PATH = f"{PROJECT_ROOT_DIR / 'src'} {PROJECT_ROOT_DIR / 'tests'}"

@task()
def black(c):
    """执行 black 格式化命令"""
    print("=" * 5, "run black", "=" * 5)
    c.run(f"black {MAIN_PATH}")


@task()
def isort(c):
    """执行 isort 命令"""
    print("=" * 5, "run isort", "=" * 5)
    c.run(f"isort {MAIN_PATH}")


@task()
def flake(c):
    """执行 flake8 代码检查"""
    print("=" * 5, "run flake", "=" * 5)
    c.run(f"flake8 {MAIN_PATH}")


@task()
def pylint(c):
    """执行 pylint 代码检查"""
    print("=" * 5, "run pylint", "=" * 5)
    c.run(f"pylint {PROJECT_ROOT_DIR / 'src'} --exit-zero")


@task(black, isort, flake, default=True)
def check(c):
    print("~" * 5, "check finish!", "~" * 5)


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
        webbrowser.open(f"file:///{index.absolute()}")
