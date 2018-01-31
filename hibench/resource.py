import logging
import os

from Crypto.PublicKey import RSA
import keystoneauth1.loading
import keystoneauth1.session
import novaclient.client
#from heatclient.common import template_utils
#from heatclient.exc import HTTPNotFound

from scotty.utils import ResourceUtils, HeatClient

logger = logging.getLogger(__name__)


class HiBenchResource(object):
    TEMPLATE_PATH = '../template/stack-name.yaml'

    def __init__(self, context):
        resource = context.v1.resource
        self.resource_utils = ResourceUtils(context)
        self.resource = resource
        self._init_clients()

    def _init_clients(self):
        keystone_password_loader = keystoneauth1.loading.get_plugin_loader('password')
        auth = keystone_password_loader.load_from_options(
            auth_url = self.resource.params['auth_url'],
            username = self.resource.params['username'],
            password = self.resource.params['password'],
            project_name = self.resource.params['project_name']
        )
        keystone_session = keystoneauth1.session.Session(auth=auth)
        self._nova = novaclient.client.Client('2', session=keystone_session)
        self._heat = HeatClient(session=keystone_session)

    @classmethod
    def reduce_logging(cls):
        reduce_loggers = {
            'keystoneauth.identity.v2',
            'keystoneauth.identity.v2.base',
            'keystoneauth.session',
            'urllib3.connectionpool',
            'stevedore.extension',
            'novaclient.v2.client'
        }
        for logger in reduce_loggers:
            logging.getLogger(logger).setLevel(logging.WARNING)

    def _get_tpl_path(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        tpl_path = os.path.join(script_dir, self.TEMPLATE_PATH)
        tpl_path = os.path.normpath(tpl_path)
        return tpl_path

    def deploy(self):
        #self._delete_stack()
        logger.info("Create heat stack ({})".format(self.resource.name))
        return {}
        self._prepare_keypair()
        self._create_stack()
        stack = self._heat.get_stack(self.resource.name)
        endpoint = self._create_endpoint(stack)
        #exec own ssh common with paramiko see workload 
        #self._exec_bla(endpoint)
        logger.debug('Endpoint: {}'.format(endpoint))
        return endpoint

    def _create_stack(self):
        stack_params = self._parse_stack_params()
        stack_tpl_path = self._get_tpl_path()
        self._heat.create_stack(
            stack_tpl_path,
            self.resource.name,
            stack_params)
        self._heat.wait_for_stack(self.resource.name)

    def _create_endpoint(self, stack):
        stack_outputs = self._heat.parse_outputs(stack)
        stressors_public_ip = stack_outputs['stressors_public_ip']
        endpoints = []
        for stressor_public_ip in stressors_public_ip:
            endpoint = {
                'ip':stressor_public_ip,
                'user':'cloud',
                'private_key':self.key_name,
            }
            endpoints.append(endpoint)
        return endpoints

    def clean(self):
        logger.info("Clean heat stack ({})".format(self.resource.name))
        return {}
        debug_mode = self.resource.params.get('debug', False)
        if not debug_mode:
            self._delete_key()
            self._delete_stack()

    def _delete_key(self):
        key_path = self.resource_utils.experiment_workspace.path
        key_manager = KeyManager(self.key_name, key_path)
        try:
            key_manager.delete_key()
            self._nova.keypairs.delete(self.key_name)
        except:
            pass

    def _delete_stack(self):
        try:
            self._heat.delete_stack(self.resource.name)
            self._heat.wait_for_stack(self.resource.name, 'DELETE_COMPLETE', 'DELETE_FAILED')
        except HTTPNotFound:
            logger.warning('Stack not found: {}'.format(self.resource.name))

    @property
    def key_name(self):
        key_name = "{}_{}".format(self.resource_utils.experiment_uuid, self.resource.name)
        return key_name

    def _prepare_keypair(self):
        key_path = self.resource_utils.experiment_workspace.path
        key_manager = KeyManager(self.key_name, key_path)
        key_manager.create_key()
        key_manager.save_key()
        self._nova.keypairs.create(self.key_name, key_manager.key_public)

    def _parse_stack_params(self):
        stack_params = {
            'key_name': self.key_name,
            'private_net_id': 'private-1a03e53738ad4854b9610273945c2b6b',
            'private_subnet_id': '30e4947e-6479-419c-8f85-a20c993bb939',
            'public_net_id': 'public',
            'instance_number': self.resource.params['instances'],
            'stressor_flavor': self.resource.params['flavor'],
        }
        return stack_params

class KeyManager(object):
    def __init__(self, key_name, key_path):
        self.key = None
        self.key_private = None
        self.key_public = None
        self.public_key_name = "{}.pub".format(key_name)
        self.private_key_name = "{}.key".format(key_name)
        self.key_path = key_path

    def create_key(self):
        self.key = RSA.generate(2048)
        self.key_private = self.key.exportKey('PEM')
        self.key_public = self.key.exportKey('OpenSSH')

    @property
    def key_path_public(self):
        key_path_public = os.path.join(self.key_path, self.public_key_name)
        return key_path_public

    @property
    def key_path_private(self):
        key_path_private = os.path.join(self.key_path, self.private_key_name)
        return key_path_private

    def save_key(self):
        with open(self.key_path_public, 'w') as f:
            f.write(self.key_public)
        with open(self.key_path_private, 'w') as f:
            f.write(self.key_private)
        os.chmod(self.key_path_private, 0600)

    def delete_key(self):
        os.remove(self.key_path_public)
        os.remove(self.key_path_private)
