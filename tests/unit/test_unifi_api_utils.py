
import pytest
from unittest.mock import MagicMock, patch
from plugins.module_utils.unifi_api import UnifiAPI

@pytest.fixture
def mock_session():
    with patch('requests.Session') as mock:
        session = mock.return_value
        yield session

def test_unifi_api_init():
    api = UnifiAPI("192.168.1.1", "admin", "password")
    assert api.host == "192.168.1.1"
    assert api.username == "admin"
    assert api.base_url == "https://192.168.1.1:443/proxy/network/api/s/default"

def test_unifi_api_login_success(mock_session):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_session.post.return_value = mock_response
    
    api = UnifiAPI("192.168.1.1", "admin", "password")
    assert api.login() is True
    assert api.logged_in is True
    mock_session.post.assert_called_once()

def test_unifi_api_login_fail(mock_session):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_session.post.return_value = mock_response
    
    api = UnifiAPI("192.168.1.1", "admin", "password")
    assert api.login() is False
    assert api.logged_in is False

def test_unifi_api_get_devices(mock_session):
    api = UnifiAPI("192.168.1.1", "admin", "password")
    api.logged_in = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': [{'name': 'AP-West'}]}
    mock_session.get.return_value = mock_response
    
    devices = api.get_devices()
    assert len(devices) == 1
    assert devices[0]['name'] == 'AP-West'
    mock_session.get.assert_called_with("https://192.168.1.1:443/proxy/network/api/s/default/stat/device", verify=False)

def test_unifi_api_get_clients(mock_session):
    api = UnifiAPI("192.168.1.1", "admin", "password")
    api.logged_in = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {'data': [{'hostname': 'iPhone'}]}
    mock_session.get.return_value = mock_response
    
    clients = api.get_clients()
    assert len(clients) == 1
    assert clients[0]['hostname'] == 'iPhone'

def test_unifi_api_update_device(mock_session):
    api = UnifiAPI("192.168.1.1", "admin", "password")
    api.logged_in = True
    
    mock_response = MagicMock()
    mock_response.json.return_value = {'meta': {'rc': 'ok'}}
    mock_session.put.return_value = mock_response
    
    result = api.update_device("device_id_123", {"name": "New Name"})
    assert result['meta']['rc'] == 'ok'
    mock_session.put.assert_called_with("https://192.168.1.1:443/proxy/network/api/s/default/rest/device/device_id_123", json={"name": "New Name"}, verify=False)
