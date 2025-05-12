from kubernetes import client, config
import os

class K8sClient:
    def __init__(self):
        pass

    def load_service_account(self):
        config.load_incluster_config()

        # get serviceAccount
        v1 = client.CoreV1Api()
        namespace = "default"
        pod_name = os.environ.get("HOSTNAME")

        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        print(pod.spec.service_account_name)



k8_cl = K8sClient()
