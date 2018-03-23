import json

from tests.framework.cli_testcase import CliTestCase


class EndpointServerTests(CliTestCase):
    def setUp(self):
        """
        Creates a list for tracking assets for cleanup
        """
        super(EndpointServerTests, self).setUp()
        self.gcs_id, self.gcp_id = None, None

    def tearDown(self):
        """
        Deletes all endpoints created during testing
        """
        super(EndpointServerTests, self).tearDown()
        for x in (self.gcs_id, self.gcp_id):
            if x:
                self.tc.delete_endpoint(x)

    def _mk_gcs(self):
        output = self.run_line("globus endpoint create endpointservertest_gcs "
                               "--server -F json")
        res = json.loads(output)
        self.gcs_id = res['id']

    def _mk_gcp(self):
        output = self.run_line("globus endpoint create endpointservertest_gcs "
                               "--personal -F json")
        res = json.loads(output)
        self.gcp_id = res['id']

    def _add_server(self, epid, use_json=False):
        return self.run_line(
            "globus endpoint server add {} --hostname foo.com{}"
            .format(epid, '' if not use_json else ' -Fjson'))

    def test_gcs_server_add(self):
        self._mk_gcs()
        output = self._add_server(self.gcs_id)
        self.assertIn('Server added to endpoint successfully', output)

    def test_gcs_server_list(self):
        self._mk_gcs()
        self._add_server(self.gcs_id)
        output = self.run_line(
            "globus endpoint server list {}"
            .format(self.gcs_id))
        self.assertIn('gsiftp://foo.com:2811', output)

    def test_gcp_server_list(self):
        self._mk_gcs()
        self._add_server(self.gcs_id)
        output = self.run_line(
            "globus endpoint server list {}"
            .format(self.gcs_id))
        self.assertIn('gsiftp://foo.com:2811', output)

    def _create_and_delete_server(self, mode):
        assert mode in ('id', 'hostname', 'hostname_port', 'uri')

        self._mk_gcs()
        add_server_out = json.loads(
            self._add_server(self.gcs_id, use_json=True))

        if mode == 'id':
            server = add_server_out['id']
        elif mode == 'hostname':
            server = 'foo.com'
        elif mode == 'hostname_port':
            server = 'foo.com:2811'
        elif mode == 'uri':
            server = 'gsiftp://foo.com:2811'
        else:
            raise NotImplementedError

        output = self.run_line(
            "globus endpoint server delete {} {}"
            .format(self.gcs_id, server))
        self.assertIn('Server deleted successfully', output)
        output = self.run_line(
            "globus endpoint server list {}"
            .format(self.gcs_id))
        self.assertNotIn('gsiftp://foo.com:2811', output)

    def test_server_delete_by_id(self):
        self._create_and_delete_server('id')

    def test_server_delete_by_hostname(self):
        self._create_and_delete_server('hostname')

    def test_server_delete_by_hostname_port(self):
        self._create_and_delete_server('hostname_port')

    def test_server_delete_by_uri(self):
        self._create_and_delete_server('uri')
