from kubernetes import config, client
from kubernetes.client import V1ObjectMeta

# configmap
from kubernetes.client import V1ConfigMap
# deployment
from kubernetes.client import V1Deployment, V1DeploymentSpec, V1LabelSelector, V1PodTemplateSpec, V1PodSpec, V1Container, \
    V1ResourceRequirements, V1EnvFromSource,V1ConfigMapEnvSource, V1ContainerPort
# service
from kubernetes.client import V1Service, V1ServiceSpec, V1ServicePort


# config.load_incluster_config()
contexts, active_context = config.list_kube_config_contexts()
config.load_kube_config(context=active_context["name"])


v1 = client.CoreV1Api()
v1_apps = client.AppsV1Api()
crd = client.CustomObjectsApi()
namespace = "default"

def create_config_map(client: client.CoreV1Api):
    metadata = V1ObjectMeta(
        name="mc-server-config"
    )

    config_map = V1ConfigMap(
        api_version="v1",
        metadata=metadata,
        data={
            "EULA": "true"
        }
    )

    client.create_namespaced_config_map(
        namespace=namespace,
        body=config_map,
    )


def delete_config_map(client: client.CoreV1Api):
    client.delete_namespaced_config_map(
        name="mc-server-config",
        namespace=namespace
    )


def create_deployment(client: client.AppsV1Api):
    metadata =  V1ObjectMeta(
        name="mc-server",
        labels={
            "app": "gameserver",
            "server-id": "mc-server",
            "owner": "123"
        }
    )

    spec = V1DeploymentSpec(
        selector=V1LabelSelector(
            match_labels={
                "app": "mc-server"
            }
        ),
        template=V1PodTemplateSpec(
            metadata=V1ObjectMeta(
                labels={
                    "app": "mc-server"
                }
            ),
            spec=V1PodSpec(
                containers=[
                    V1Container(
                        name="mc-server",
                        image="itzg/minecraft-server",
                        resources=V1ResourceRequirements(
                            requests={
                                "memory": "3Gi",
                                "cpu": "4000m",
                            },
                            limits={
                                "memory": "4Gi",
                                "cpu": "5500m",
                            },
                        ),
                        env_from=[V1EnvFromSource(
                            config_map_ref=V1ConfigMapEnvSource(
                                name="mc-server-config"
                            )
                        )],
                        ports=[V1ContainerPort(
                            container_port=25565,
                            name="game-port"
                        )]
                    )
                ]
            )
        )
    )

    deployment = V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=metadata,
        spec=spec,
    )

    client.create_namespaced_deployment(
        namespace=namespace,
        body=deployment
    )


def delete_deployment(client: client.AppsV1Api):
    client.delete_namespaced_deployment(
        name="mc-server",
        namespace=namespace
    )


def create_service(client: client.CoreV1Api):
    metadata = V1ObjectMeta(
        name="mc-server"
    )

    spec = V1ServiceSpec(
        selector={
            "app": "mc-server"
        },
        ports=[
            V1ServicePort(
                name="game-port",
                app_protocol="TCP",
                protocol="TCP",
                target_port="game-port",
                port=5000
            )
        ]
    )

    service = V1Service(
        api_version="v1",
        metadata=metadata,
        spec=spec
    )

    client.create_namespaced_service(
        namespace=namespace,
        body=service
    )


def delete_service(client: client.CoreV1Api):
    client.delete_namespaced_service(
        name="mc-server",
        namespace=namespace
    )


def create_traefik_tcp_ingressroute(client: client.CustomObjectsApi):
    group = "traefik.io"
    version = "v1alpha1"
    plural = "ingressroutetcps"
    kind = "IngressRouteTCP"


    name = "mc-server-route"
    match_host_SNI = "*"
    service_name = "mc-server"
    service_port = "game-port"

    body = {
        "apiVersion": f"{group}/{version}",
        "kind": f"{kind}",
        "metadata": {
            "name": f"{name}"
        },
        "spec": {
            "entryPoints": [
                "web"
            ],
            "routes": [
                {
                    "match": f"HostSNI(`{match_host_SNI}`)",
                    "services": [
                        {
                            "name": f"{service_name}",
                            "port": f"{service_port}"
                        }
                    ]
                }
            ]
        }
    }

    client.create_namespaced_custom_object(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        body=body
    )
    

def delete_traefik_tcp_ingressroute(client: client.CustomObjectsApi):
    client.delete_cluster_custom_object(
        group="traefik.io",
        version="v1alpha1",
        plural="ingressroutetcps",
        name="mc-server-route"
    )


if __name__ == "__main__":
    pass
    # UP
    # create_config_map(v1)
    # create_deployment(v1_apps)
    # create_service(v1)
    # create_traefik_tcp_ingressroute(crd)

    # DOWN
    delete_config_map(v1)
    delete_deployment(v1_apps)
    delete_service(v1)
    delete_traefik_tcp_ingressroute(crd)
