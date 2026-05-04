from __future__ import annotations

from pathlib import Path


from nerv.init import run_init
from nerv.init.update import run_update


def _write_fastapi_pyproject(root: Path) -> None:
    content = """[project]
name = "fastapp"
version = "0.1.0"
dependencies = [
    "fastapi>=0.100.0",
    "sqlalchemy>=2.0",
    "pytest>=7.0",
]

[project.scripts]
test = "pytest"
lint = "ruff check ."
"""
    (root / "pyproject.toml").write_text(content, encoding="utf-8")
    (root / "src").mkdir(exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)


def _write_generic_pyproject(root: Path) -> None:
    content = """[project]
name = "genericapp"
version = "0.1.0"
dependencies = [
    "some-lib>=1.0",
    "another-lib>=2.0",
]
"""
    (root / "pyproject.toml").write_text(content, encoding="utf-8")


class TestInit:
    def test_init_fastapi_project(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        result = run_init(tmp_path, project_name=None, stack_override=None, force=True)
        assert result == 0

        agents_md = tmp_path / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text(encoding="utf-8")
        assert "FastAPI" in content
        assert "SQLAlchemy" in content
        assert "pytest" in content
        assert "pytest" in content  # tool command

    def test_init_generic_project(self, tmp_path: Path) -> None:
        _write_generic_pyproject(tmp_path)
        result = run_init(tmp_path, project_name=None, stack_override=None, force=True)
        assert result == 0

        agents_md = tmp_path / "AGENTS.md"
        content = agents_md.read_text(encoding="utf-8")
        assert "some-lib" not in content.lower()  # unknown libs not listed
        assert "Project Structure" not in content  # no structure detected

    def test_nerv_agent_created(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        nerv_agent = tmp_path / ".opencode" / "agents" / "nerv.md"
        assert nerv_agent.exists()
        agent_content = nerv_agent.read_text(encoding="utf-8")
        assert "mode: primary" in agent_content
        assert "hidden: false" in agent_content
        assert "sdd-explorer" in agent_content
        assert "sdd-proposer" in agent_content
        assert "sdd-designer" in agent_content
        assert "git-ops" in agent_content
        assert "github-ops" in agent_content

    def test_commands_created_for_detected_tools(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        test_cmd = tmp_path / ".opencode" / "commands" / "test.md"
        lint_cmd = tmp_path / ".opencode" / "commands" / "lint.md"

        assert test_cmd.exists()
        test_content = test_cmd.read_text(encoding="utf-8")
        assert "pytest" in test_content

        assert lint_cmd.exists()
        lint_content = lint_cmd.read_text(encoding="utf-8")
        assert "ruff" in lint_content

    def test_no_typecheck_command_without_typechecker(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        typecheck_cmd = tmp_path / ".opencode" / "commands" / "typecheck.md"
        assert not typecheck_cmd.exists()

    def test_init_idempotent(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)
        # Second run without force should skip
        result = run_init(tmp_path, project_name=None, stack_override=None, force=False)
        assert result == 0  # no error, things were skipped

    def test_init_with_stack_override(self, tmp_path: Path) -> None:
        run_init(tmp_path, project_name="testproj", stack_override="python", force=True)
        agents_md = tmp_path / "AGENTS.md"
        assert agents_md.exists()
        content = agents_md.read_text(encoding="utf-8")
        assert "testproj" in content

    def test_code_skill_has_framework_guidance(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        code_skill = tmp_path / ".opencode" / "skills" / "code" / "SKILL.md"
        content = code_skill.read_text(encoding="utf-8")
        assert "FastAPI" in content
        assert "Depends()" in content

    def test_code_skill_no_frameworks_generic(self, tmp_path: Path) -> None:
        _write_generic_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        code_skill = tmp_path / ".opencode" / "skills" / "code" / "SKILL.md"
        content = code_skill.read_text(encoding="utf-8")
        assert "FastAPI" not in content


class TestUpdate:
    def test_markers_preserved_on_update(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        agents_md = tmp_path / "AGENTS.md"
        # Add custom user content after markers
        agents_md.write_text(
            agents_md.read_text(encoding="utf-8")
            + "\n\n// My custom project notes\n// Team conventions here\n",
            encoding="utf-8",
        )

        run_update(tmp_path)

        updated_content = agents_md.read_text(encoding="utf-8")
        assert "My custom project notes" in updated_content
        assert "Team conventions here" in updated_content
        assert "FastAPI" in updated_content  # regenerated marker section

    def test_update_dry_run(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        agents_md_before = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        run_update(tmp_path, dry_run=True)
        agents_md_after = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

        # AGENTS.md should not have been modified during dry run
        assert agents_md_before == agents_md_after

    def test_update_creates_missing_nerv_agent(self, tmp_path: Path) -> None:
        _write_fastapi_pyproject(tmp_path)
        run_init(tmp_path, project_name=None, stack_override=None, force=True)

        nerv_agent = tmp_path / ".opencode" / "agents" / "nerv.md"
        nerv_agent.unlink()
        assert not nerv_agent.exists()

        run_update(tmp_path, force_commands=True)

        assert nerv_agent.exists()
