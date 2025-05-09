from kubernetes import client, config

class K8sClient:
    def __init__(self):
        pass

    def load_service_account(self):
        config.load_incluster_config()


k8_cl = K8sClient()
