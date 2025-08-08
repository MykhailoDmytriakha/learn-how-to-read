from __future__ import annotations

import logging

import streamlit as st

# Support both package and script imports
try:
    from .files import load_config, load_phrases
except Exception:  # pragma: no cover - runtime import mode
    from services.files import load_config, load_phrases  # type: ignore

logger = logging.getLogger(__name__)


def init_session_state() -> None:
    logger.info("Initializing session state")

    if "current_text" not in st.session_state:
        st.session_state.current_text = None

    if "reading_state" not in st.session_state:
        st.session_state.reading_state = None

    if "processed_result" not in st.session_state:
        st.session_state.processed_result = None

    if "need_rerun" not in st.session_state:
        st.session_state.need_rerun = False

    if (
        "child_age" not in st.session_state
        or "use_cognitive_load" not in st.session_state
        or "use_children_algorithm" not in st.session_state
    ):
        config = load_config()
        st.session_state.child_age = config.get("child_age", 8)
        st.session_state.use_cognitive_load = config.get("use_cognitive_load", True)
        st.session_state.use_children_algorithm = config.get("use_children_algorithm", True)
        logger.info(
            "Initialized settings from config: age=%s, cognitive_load=%s, children_algorithm=%s",
            st.session_state.child_age,
            st.session_state.use_cognitive_load,
            st.session_state.use_children_algorithm,
        )
    else:
        logger.debug(
            "Session settings already exist: age=%s, cognitive_load=%s, children_algorithm=%s",
            st.session_state.child_age,
            st.session_state.use_cognitive_load,
            st.session_state.use_children_algorithm,
        )

    # Ensure phrases_data is initialized once
    if "phrases_data" not in st.session_state:
        logger.info("Loading phrases_data for the first time")
        st.session_state.phrases_data = load_phrases()
        logger.info("Loaded %d phrases into session state", len(st.session_state.phrases_data))
    elif not st.session_state.phrases_data:
        logger.info("phrases_data is empty, reloading")
        st.session_state.phrases_data = load_phrases()
        logger.info("Reloaded %d phrases into session state", len(st.session_state.phrases_data))
    else:
        logger.debug(
            "phrases_data already exists with %d phrases; keeping existing state",
            len(st.session_state.phrases_data),
        )
