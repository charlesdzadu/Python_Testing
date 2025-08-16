import os
import sys
import json
import pytest
from unittest.mock import patch


# Ensure project root is on sys.path for `import server`
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


@pytest.fixture(autouse=True)
def mock_save_functions():
    """Mock the save functions to prevent file modifications during tests"""
    with patch('server.saveClubs') as mock_save_clubs, \
         patch('server.saveCompetitions') as mock_save_comps:
        yield mock_save_clubs, mock_save_comps


@pytest.fixture(autouse=True)
def reset_data():
    """Reset server data to original state before each test"""
    import server
    with open('clubs.json') as c:
        server.clubs = json.load(c)['clubs']
    with open('competitions.json') as comps:
        server.competitions = json.load(comps)['competitions']
