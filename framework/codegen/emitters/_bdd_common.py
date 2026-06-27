"""
Shared, language-agnostic BDD helpers.

The Gherkin ``.feature`` file is the same regardless of which language the step
definitions are written in — that is the whole point of BDD. So feature
rendering and the friendly target/phrase logic live here and are reused by
every BDD emitter (pytest-bdd, Cucumber-JVM, Cucumber.js), guaranteeing
byte-identical feature files across languages.

Each language emitter only supplies its own step-definition template and its
own rendering of the LOCATORS registry (primary + ranked fallbacks).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from framework.codegen.ir import ActionType, AssertionType, Selector, Step, TestModel


def target_key(sel: Selector) -> str:
    """A friendly, human-facing handle for a selector — the Gherkin target name
    and the LOCATORS registry key. Stable and readable."""
    return sel.description or sel.value


# Which Gherkin clause an action belongs to. Consecutive steps in the same
# clause render as "And" for readability.
_CLAUSE = {
    ActionType.LAUNCH: "Given",
    ActionType.TAP: "When",
    ActionType.TYPE: "When",
    ActionType.SWIPE: "When",
    ActionType.WAIT: "When",
    ActionType.BACK: "When",
    ActionType.ASSERT: "Then",
}


def phrase(step: Step) -> str:
    """The canonical Gherkin step text — must match the step-def parser in every
    language (Cucumber expressions: {string}, {int})."""
    a = step.action
    if a is ActionType.LAUNCH:
        return "the app is launched"
    if a is ActionType.TYPE:
        return f'I enter "{step.text}" into "{target_key(step.selector)}"'
    if a is ActionType.TAP:
        return f'I tap "{target_key(step.selector)}"'
    if a is ActionType.WAIT:
        return f"I wait {int(step.timeout or 5)} seconds"
    if a is ActionType.BACK:
        return "I press back"
    if a is ActionType.ASSERT:
        key = target_key(step.selector)
        if step.assertion is AssertionType.VISIBLE:
            return f'"{key}" is visible'
        if step.assertion is AssertionType.TEXT_EQUALS:
            return f'"{key}" text is "{step.expected}"'
        if step.assertion is AssertionType.ENABLED:
            return f'"{key}" is enabled'
    raise ValueError(f"Unsupported step for BDD: {a} / {step.assertion}")


def scenario_lines(steps: List[Step]) -> List[Dict[str, str]]:
    """Assign Given/When/Then/And keywords to a case's steps."""
    lines: List[Dict[str, str]] = []
    prev_clause = None
    for step in steps:
        clause = _CLAUSE[step.action]
        keyword = "And" if clause == prev_clause else clause
        lines.append({"keyword": keyword, "phrase": phrase(step)})
        prev_clause = clause
    return lines


def collect_targets(model: TestModel) -> List[Tuple[str, Selector]]:
    """De-duplicated, ordered (target_key, selector) for every selector in the
    model. Each language emitter renders its own LOCATORS registry from this."""
    seen: Dict[str, Selector] = {}
    order: List[str] = []
    for case in model.cases:
        for step in case.steps:
            if step.selector is None:
                continue
            key = target_key(step.selector)
            if key not in seen:
                seen[key] = step.selector
                order.append(key)
    return [(k, seen[k]) for k in order]


def render_feature(model: TestModel) -> str:
    """Render the language-agnostic Gherkin feature file (one Scenario per
    TestCase). Identical bytes regardless of step-definition language."""
    out: List[str] = [f"Feature: {model.name}"]
    if model.description:
        out.append(f"  {model.description}")
    out.append("")
    for case in model.cases:
        out.append(f"  Scenario: {case.description or case.name}")
        for line in scenario_lines(case.steps):
            out.append(f"    {line['keyword']} {line['phrase']}")
        out.append("")
    return "\n".join(out) + "\n"
