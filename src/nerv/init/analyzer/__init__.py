"""Project analyzer orchestrator — runs all detectors and produces a ProjectProfile."""

from __future__ import annotations

import logging
from pathlib import Path

from nerv.init.analyzer.frameworks import FrameworkDetector
from nerv.init.analyzer.profile import ProjectProfile
from nerv.init.analyzer.structure import StructureDetector
from nerv.init.analyzer.tools import ToolDetector
from nerv.init.context import ProjectContext

logger = logging.getLogger("nerv.init.analyzer")


def analyze_project(root: Path, context: ProjectContext) -> ProjectProfile:
    """Run all detectors and build a ProjectProfile.

    Each detector is isolated — failure in one does not affect others.
    """
    stack = context.stack

    try:
        frameworks = FrameworkDetector().detect(root, stack)
    except Exception as exc:
        logger.debug("Framework detector failed: %s", exc)
        frameworks = []

    try:
        tools = ToolDetector().detect(root, stack)
    except Exception as exc:
        logger.debug("Tool detector failed: %s", exc)
        tools = []

    try:
        structure = StructureDetector().detect(root, stack)
    except Exception as exc:
        logger.debug("Structure detector failed: %s", exc)
        from nerv.init.analyzer.profile import StructureInfo as _SI

        structure = _SI()

    return ProjectProfile(
        stack=stack,
        project_name=context.project_name,
        frameworks=frameworks,
        tools=tools,
        structure=structure,
    )
