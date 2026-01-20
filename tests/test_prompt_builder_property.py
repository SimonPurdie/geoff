from hypothesis import given, settings, strategies as st
from geoff.config import PromptConfig
from geoff.prompt_builder import build_prompt


def filepath_strategy(min_size=1, max_size=50):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


def text_strategy(min_size=1, max_size=100):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,!?\n"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


@given(
    study_docs=st.lists(filepath_strategy(), max_size=5),
    breadcrumbs_file=filepath_strategy(),
    tasklist_file=filepath_strategy(),
    oneoff_prompt=text_strategy(),
    backpressure_enabled=st.booleans(),
    breadcrumb_enabled=st.booleans(),
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=100)
def test_prompt_always_returns_string(
    study_docs,
    breadcrumbs_file,
    tasklist_file,
    oneoff_prompt,
    backpressure_enabled,
    breadcrumb_enabled,
    task_mode,
):
    config = PromptConfig(
        study_docs=study_docs,
        breadcrumbs_file=breadcrumbs_file,
        tasklist_file=tasklist_file,
        oneoff_prompt=oneoff_prompt,
        backpressure_enabled=backpressure_enabled,
        breadcrumb_enabled=breadcrumb_enabled,
        task_mode=task_mode,
    )
    result = build_prompt(config)
    assert isinstance(result, str)


@given(
    study_docs=st.lists(filepath_strategy(), max_size=5),
)
@settings(max_examples=50)
def test_study_docs_order_preserved(study_docs):
    config = PromptConfig(
        study_docs=study_docs,
        task_mode="oneoff",
        oneoff_prompt="test prompt",
    )
    prompt = build_prompt(config)
    lines = prompt.splitlines()

    study_doc_lines = [
        line
        for line in lines
        if line.startswith("study ") and "pick the most important" not in line
    ]
    extracted_docs = [line.replace("study ", "", 1) for line in study_doc_lines]

    assert extracted_docs == study_docs


@given(
    backpressure_enabled=st.booleans(),
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=100)
def test_backpressure_content_when_enabled(backpressure_enabled, task_mode):
    config = PromptConfig(
        backpressure_enabled=backpressure_enabled,
        task_mode=task_mode,
    )
    prompt = build_prompt(config)

    if backpressure_enabled:
        assert "IMPORTANT:" in prompt
        assert (
            "- author property based tests or unit tests (whichever is best)" in prompt
        )
        assert "- after performing your task run the tests" in prompt
        assert "- when tests pass, commit to deploy changes" in prompt
    else:
        assert "IMPORTANT:" not in prompt


@given(
    breadcrumb_enabled=st.booleans(),
    breadcrumbs_file=filepath_strategy(),
)
@settings(max_examples=100)
def test_breadcrumb_check_line(breadcrumb_enabled, breadcrumbs_file):
    config = PromptConfig(
        breadcrumb_enabled=breadcrumb_enabled,
        breadcrumbs_file=breadcrumbs_file,
    )
    prompt = build_prompt(config)

    if breadcrumb_enabled and breadcrumbs_file:
        assert f"check {breadcrumbs_file}" in prompt
        assert "if you ran into difficulties" in prompt
        assert breadcrumbs_file in prompt
    else:
        assert "check " not in prompt


@given(
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
    tasklist_file=filepath_strategy(),
    oneoff_prompt=text_strategy(),
)
@settings(max_examples=100)
def test_task_mode_exclusivity(task_mode, tasklist_file, oneoff_prompt):
    config = PromptConfig(
        task_mode=task_mode,
        tasklist_file=tasklist_file,
        oneoff_prompt=oneoff_prompt,
    )
    prompt = build_prompt(config)

    has_tasklist_line = "pick the most important thing to do" in prompt
    has_update_line = "update " in prompt

    if task_mode == "tasklist":
        assert has_tasklist_line, "Tasklist mode should include tasklist study line"
        assert has_update_line, "Tasklist mode should include update line"
    else:
        assert not has_tasklist_line, (
            "Non-tasklist mode should not include tasklist study line"
        )
        assert not has_update_line, "Non-tasklist mode should not include update line"


@given(
    study_docs=st.lists(filepath_strategy(), max_size=10),
    backpressure_enabled=st.booleans(),
    breadcrumb_enabled=st.booleans(),
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=50)
def test_no_empty_lines_in_output(
    study_docs,
    backpressure_enabled,
    breadcrumb_enabled,
    task_mode,
):
    config = PromptConfig(
        study_docs=study_docs,
        backpressure_enabled=backpressure_enabled,
        breadcrumb_enabled=breadcrumb_enabled,
        task_mode=task_mode,
    )
    prompt = build_prompt(config)
    lines = prompt.splitlines()

    for line in lines:
        assert line.strip(), "Prompt should not contain empty lines"


@given(
    tasklist_file=filepath_strategy(),
    breadcrumbs_file=filepath_strategy(),
)
@settings(max_examples=50)
def test_tasklist_and_breadcrumb_order(tasklist_file, breadcrumbs_file):
    config = PromptConfig(
        tasklist_file=tasklist_file,
        breadcrumbs_file=breadcrumbs_file,
    )
    prompt = build_prompt(config)
    lines = prompt.splitlines()

    check_idx = None
    study_tasklist_idx = None

    for i, line in enumerate(lines):
        if line.startswith(f"check {breadcrumbs_file}"):
            check_idx = i
        if "pick the most important thing to do" in line:
            study_tasklist_idx = i

    if check_idx is not None and study_tasklist_idx is not None:
        assert check_idx < study_tasklist_idx, (
            "Breadcrumb check must come before tasklist study"
        )


@given(
    study_docs=st.lists(filepath_strategy(), max_size=3),
    breadcrumbs_file=filepath_strategy(),
    tasklist_file=filepath_strategy(),
)
@settings(max_examples=50)
def test_prompt_starts_with_study_docs(
    study_docs,
    breadcrumbs_file,
    tasklist_file,
):
    config = PromptConfig(
        study_docs=study_docs,
        breadcrumbs_file=breadcrumbs_file,
        tasklist_file=tasklist_file,
    )
    prompt = build_prompt(config)
    lines = prompt.splitlines()

    if study_docs:
        assert lines[0].startswith("study "), "First line should be a study doc"


@given(
    study_docs=st.lists(filepath_strategy(), max_size=5),
    breadcrumbs_file=filepath_strategy(),
    tasklist_file=filepath_strategy(),
    backpressure_enabled=st.booleans(),
    breadcrumb_enabled=st.booleans(),
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=50)
def test_no_crashes_on_any_inputs(
    study_docs,
    breadcrumbs_file,
    tasklist_file,
    backpressure_enabled,
    breadcrumb_enabled,
    task_mode,
):
    config = PromptConfig(
        study_docs=study_docs,
        breadcrumbs_file=breadcrumbs_file,
        tasklist_file=tasklist_file,
        backpressure_enabled=backpressure_enabled,
        breadcrumb_enabled=breadcrumb_enabled,
        task_mode=task_mode,
    )
    result = build_prompt(config)
    assert len(result) >= 0


@given(
    oneoff_prompt=text_strategy(max_size=500),
)
@settings(max_examples=30)
def test_oneoff_prompt_preserved(oneoff_prompt):
    config = PromptConfig(
        task_mode="oneoff",
        oneoff_prompt=oneoff_prompt,
    )
    prompt = build_prompt(config)

    assert oneoff_prompt.strip() in prompt


@given(
    max_iterations=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=20)
def test_max_iterations_does_not_affect_prompt(max_iterations):
    config1 = PromptConfig(max_iterations=max_iterations)
    config2 = PromptConfig(max_iterations=0)

    prompt1 = build_prompt(config1)
    prompt2 = build_prompt(config2)

    assert prompt1 == prompt2
