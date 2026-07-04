"""End-to-end test (Selenium): a user fills the form in a real browser and
gets a real prediction back from the real backend.

Unlike the unit/integration tests, this does NOT start the app itself: it
drives whatever is already running at FRONTEND_URL against BACKEND_URL,
exactly like a human tester would. In CI (.github/workflows/dev-to-staging.yml)
both services are started as background steps before this test runs; locally
you can do the same:

    # terminal 1
    cd backend && MLFLOW_TRACKING_URI=<uri> MLFLOW_MODEL_STAGE=Production \
        python -m flask --app wsgi:app run --port 5000
    # terminal 2
    cd frontend && NEXT_PUBLIC_API_URL=http://localhost:5000 npm run dev
    # terminal 3
    pytest tests/e2e -v
"""

from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")


@pytest.fixture()
def browser():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 900)
    yield driver
    driver.quit()


def test_user_can_submit_match_stats_and_see_a_prediction(browser):
    browser.get(FRONTEND_URL)

    wait = WebDriverWait(browser, 15)
    gold_diff_input = wait.until(EC.presence_of_element_located((By.ID, "blueGoldDiff")))
    gold_diff_input.clear()
    gold_diff_input.send_keys("6000")

    kills_input = browser.find_element(By.ID, "blueKills")
    kills_input.clear()
    kills_input.send_keys("12")

    submit_button = browser.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    result = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "result-title")))

    assert "team" in result.text.lower()
    assert browser.find_elements(By.CLASS_NAME, "bar-blue")
