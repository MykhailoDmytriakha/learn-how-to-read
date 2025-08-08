from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

import streamlit as st

# Support both package and script imports
try:
    from ..domain.complexity import calculate_text_complexity_universal
except Exception:  # pragma: no cover - runtime import mode
    from domain.complexity import calculate_text_complexity_universal  # type: ignore

logger = logging.getLogger(__name__)

PHRASES_FILE = "phrases.json"
CONFIG_FILE = "config.json"


def load_config() -> dict[str, Any]:
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            config = json.load(f)
            logger.info("Configuration loaded from %s", CONFIG_FILE)
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Could not load config from %s: %s", CONFIG_FILE, e)
        default_config: dict[str, Any] = {
            "child_age": 8,
            "use_cognitive_load": True,
            "use_children_algorithm": True,
            "last_updated": datetime.now().isoformat(),
        }
        save_config(default_config)
        return default_config


def save_config(config: dict[str, Any]) -> None:
    try:
        config["last_updated"] = datetime.now().isoformat()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info("Configuration saved to %s", CONFIG_FILE)
    except Exception as e:  # noqa: BLE001 (broad-except is OK here: we log the error)
        logger.error("Could not save config to %s: %s", CONFIG_FILE, e)


def load_phrases() -> list[dict[str, Any]]:
    logger.info("Starting to load phrases from %s", PHRASES_FILE)
    if not os.path.exists(PHRASES_FILE):
        logger.error("File %s not found. Please create it with phrases data.", PHRASES_FILE)
        st.error(f"Файл {PHRASES_FILE} не найден. Пожалуйста, создайте его с данными фраз.")
        return []

    try:
        logger.info("Opening file %s for reading", PHRASES_FILE)
        with open(PHRASES_FILE, encoding="utf-8") as f:
            data: list[dict[str, Any]] = json.load(f)

        logger.info("Successfully loaded %d phrases from JSON file", len(data))

        read_count = 0
        unread_count = 0
        for i, phrase in enumerate(data):
            if "text" not in phrase:
                phrase["text"] = phrase.get("phrase", "")
                logger.debug("Phrase %s: Added missing 'text' field", i)

            if "is_read" not in phrase:
                phrase["is_read"] = False
                logger.debug("Phrase %s: Added missing 'is_read' field as False", i)

            if isinstance(phrase["is_read"], str):
                old_value = phrase["is_read"]
                phrase["is_read"] = phrase["is_read"].lower() == "true"
                logger.debug(
                    "Phrase %s: Converted 'is_read' from string '%s' to boolean %s",
                    i,
                    old_value,
                    phrase["is_read"],
                )

            if "read_date" not in phrase:
                phrase["read_date"] = datetime.now().isoformat() if phrase["is_read"] else None

            if phrase["is_read"]:
                read_count += 1
            else:
                unread_count += 1

            phrase["complexity"] = calculate_text_complexity_universal(
                phrase["text"],
                age=st.session_state.get("child_age", 8),
                include_cognitive_load=st.session_state.get("use_cognitive_load", True),
                use_children_algorithm=st.session_state.get("use_children_algorithm", True),
            )

        logger.info(
            "Processed %d phrases: %d read, %d unread",
            len(data),
            read_count,
            unread_count,
        )
        logger.info("Successfully loaded and processed phrases from %s (preserving original order)", PHRASES_FILE)
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error("Error reading %s: %s", PHRASES_FILE, e)
        st.error(f"Ошибка чтения файла {PHRASES_FILE}: {e}")
        return []


def save_phrases(phrases_data: list[dict[str, Any]]) -> None:
    logger.info("Starting to save %d phrases to %s", len(phrases_data), PHRASES_FILE)
    try:
        phrases_to_save: list[dict[str, Any]] = []
        read_count = 0
        unread_count = 0

        for _i, phrase in enumerate(phrases_data):
            phrase_copy = {k: v for k, v in phrase.items() if k != "complexity"}
            phrases_to_save.append(phrase_copy)
            if phrase.get("is_read", False):
                read_count += 1
            else:
                unread_count += 1

        logger.info(
            "Prepared %d phrases for saving: %d read, %d unread",
            len(phrases_to_save),
            read_count,
            unread_count,
        )

        logger.info("Opening file %s for writing", PHRASES_FILE)
        with open(PHRASES_FILE, "w", encoding="utf-8") as f:
            json.dump(phrases_to_save, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        logger.info("Successfully saved %d phrases to %s", len(phrases_to_save), PHRASES_FILE)
        logger.info("Saved data summary: %d read, %d unread phrases", read_count, unread_count)

        try:
            with open(PHRASES_FILE, encoding="utf-8") as f:
                _ = json.load(f)
        except Exception as verify_error:  # noqa: BLE001
            logger.warning("Could not verify save: %s", verify_error)
    except Exception as e:  # noqa: BLE001
        logger.error("Error saving phrases to %s: %s", PHRASES_FILE, e)
        logger.error("Exception type: %s", type(e).__name__)
        logger.error("Exception details: %s", str(e))
        st.error(f"Ошибка сохранения данных: {e}")
