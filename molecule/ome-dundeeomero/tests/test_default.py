import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

OMERO = '/opt/omero/server/OMERO.server/bin/omero'
OMERO_LOGIN = '-C -s localhost -u root -w omero'


@pytest.mark.parametrize("name", [
    'nginx',
    'omero-server',
    'postgresql-11',
    'prometheus-node-exporter',
    'prometheus-omero-exporter',
    'prometheus-postgres-exporter',
])
def test_service_running_and_enabled(host, name):
    service = host.service(name)
    assert service.is_running
    assert service.is_enabled


def test_omero_login(host):
    with host.sudo('omero-server'):
        host.check_output(
            '/opt/omero/server/OMERO.server/bin/omero '
            'login -C -s localhost -u root -w omero')


@pytest.mark.parametrize("curl", [
    'localhost:9449/metrics',
    '-u monitoring:monitoring -k https://localhost/metrics/9449',
])
def test_omero_metrics(host, curl):
    out = host.check_output('curl -f %s' % curl)
    assert 'omero_sessions_active' in out


def test_omero_metrics_auth_fail(host):
    out = host.run(
        'curl -f -u monitoring:incorrect -k https://localhost/metrics/9449')
    assert out.rc == 22
    assert '401' in out.stderr
