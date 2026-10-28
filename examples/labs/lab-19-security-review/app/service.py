"""Prediction endpoint and its logging. Review this file closely."""

from __future__ import annotations

import logging

from config import API_KEY

logger = logging.getLogger("session-score")


def predict(payload: dict) -> float:
    logger.info("predict request=%s", payload)
    hours = float(payload["hours"])
    prior = float(payload["prior_score"])
    logger.info("auth key=%s", API_KEY)
    return round(18 + 4.9 * hours + 0.66 * prior, 2)


def register(student: dict) -> None:
    # Names, dates of birth and email addresses all end up in the log file.
    logger.info("registered %s %s %s", student["name"], student["email"], student["dob"])
