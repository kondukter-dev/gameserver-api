from kubernetes import client, config
from kubernetes.client import V1ObjectMeta
# configmap
from kubernetes.client import V1ConfigMap
# deployment
from kubernetes.client import V1Deployment, V1DeploymentSpec, V1LabelSelector, V1PodTemplateSpec, V1PodSpec, V1Container, \
    V1ResourceRequirements, V1EnvFromSource,V1ConfigMapEnvSource, V1ContainerPort
# service
from kubernetes.client import V1Service, V1ServiceSpec, V1ServicePort

class K8sClient:
    def __init__(self):
        pass

        self.v1_api = None
        self.v1_app_api = None
        self.crd_api = None

        self.namespace = "gs"

    def load_service_account(self):
        # config.load_incluster_config()

        contexts, active_context = config.list_kube_config_contexts()
        config.load_kube_config(context=active_context["name"])

        # get serviceAccount
        self.v1_api = client.CoreV1Api()
        self.v1_app_api = client.AppsV1Api()
        self.crd_api = client.CustomObjectsApi()

    # ========== GAMESERVER CRUD OPERATIONS ==========

    def create_gameserver(self, server_id: str, game_name: str, user_id: str, image: str, 
                         requests_memory: str, requests_cpu: str,
                         limits_memory: str, limits_cpu: str,
                         game_port: int, config_data: dict):
        """Create a complete gameserver with configmap, deployment, service, and traefik route."""
        
        # Create all components
        self.create_gameserver_config_map(server_id, user_id, config_data)
        self.create_gameserver_deployment(server_id, game_name, user_id, image, requests_memory, requests_cpu, 
                                        limits_memory, limits_cpu, game_port)
        self.create_gameserver_service(server_id, user_id, game_port)
        self.create_gameserver_traefik_route(server_id, user_id)
        
        return {"server_id": server_id, "status": "created"}

    def get_gameserver(self, server_id: str):
        """Get a single gameserver by server_id."""
        try:
            # Get deployment (main resource)
            deployment = self.v1_app_api.read_namespaced_deployment(
                name=f"gameserver-{server_id}",
                namespace=self.namespace
            )
            
            # Get service
            service = self.v1_api.read_namespaced_service(
                name=f"gameserver-{server_id}",
                namespace=self.namespace
            )
            
            # Get configmap
            config_map = self.v1_api.read_namespaced_config_map(
                name=f"config-{server_id}",
                namespace=self.namespace
            )
            
            # Get pods
            pods = self.v1_api.list_namespaced_pod(
                namespace=self.namespace,
                label_selector=f"server-id={server_id}"
            )
            
            return {
                "server_id": server_id,
                "deployment": deployment.to_dict(),
                "service": service.to_dict(),
                "config_map": config_map.to_dict(),
                "pods": pods.to_dict()
            }
            
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return None
            raise e

    def list_gameservers(self):
        """List all gameservers."""
        deployments = self.v1_app_api.list_namespaced_deployment(
            namespace=self.namespace,
            label_selector="app=gameserver"
        )
        
        gameservers = []
        for deployment in deployments.items:
            server_id = deployment.metadata.labels.get("server-id")
            if server_id:
                gameserver_info = {
                    "server_id": server_id,
                    "username": deployment.metadata.labels.get("owner"),
                    "name": deployment.metadata.name,
                    "status": deployment.status.ready_replicas or 0,
                    "replicas": deployment.spec.replicas,
                    "created_at": deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None
                }
                gameservers.append(gameserver_info)
        
        return gameservers

    def delete_gameserver(self, server_id: str):
        """Delete a complete gameserver and all its resources."""
        try:
            # Delete in reverse order
            self.delete_gameserver_traefik_route(server_id)
            self.delete_gameserver_service(server_id)
            self.delete_gameserver_deployment(server_id)
            self.delete_gameserver_config_map(server_id)
            
            return {"server_id": server_id, "status": "deleted"}
            
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return {"server_id": server_id, "status": "not_found"}
            raise e

    # ========== INDIVIDUAL RESOURCE METHODS ==========

    def create_gameserver_config_map(self, server_id: str, user_id: str, data: dict):
        """Create configmap for gameserver."""
        metadata = V1ObjectMeta(
            name=f"config-{server_id}",
            labels={
                "app": "gameserver",
                "owner": user_id,
                "server-id": server_id
            }
        )

        config_map = V1ConfigMap(
            api_version="v1",
            metadata=metadata,
            data=data
        )

        self.v1_api.create_namespaced_config_map(
            namespace=self.namespace,
            body=config_map,
        )

    def create_gameserver_deployment(self, server_id: str, game_name: str, user_id: str, image: str,
                                   requests_memory: str, requests_cpu: str,
                                   limits_memory: str, limits_cpu: str, game_port: int):
        """Create deployment for gameserver."""
        metadata = V1ObjectMeta(
            name=f"gameserver-{server_id}",
            labels={
                "app": "gameserver",
                "game": game_name,
                "owner": user_id,
                "server-id": server_id
            }
        )

        spec = V1DeploymentSpec(
            selector=V1LabelSelector(
                match_labels={
                    "app": "gameserver",
                    "server-id": server_id
                }
            ),
            template=V1PodTemplateSpec(
                metadata=V1ObjectMeta(
                    labels={
                        "app": "gameserver",
                        "game": game_name,
                        "owner": user_id,
                        "server-id": server_id
                    }
                ),
                spec=V1PodSpec(
                    containers=[
                        V1Container(
                            name="gameserver",
                            image=image,
                            resources=V1ResourceRequirements(
                                requests={
                                    "memory": requests_memory,
                                    "cpu": requests_cpu,
                                },
                                limits={
                                    "memory": limits_memory,
                                    "cpu": limits_cpu,
                                },
                            ),
                            env_from=[V1EnvFromSource(
                                config_map_ref=V1ConfigMapEnvSource(
                                    name=f"config-{server_id}"
                                )
                            )],
                            ports=[V1ContainerPort(
                                container_port=game_port,
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

        self.v1_app_api.create_namespaced_deployment(
            namespace=self.namespace,
            body=deployment
        )

    def create_gameserver_service(self, server_id: str, user_id: str, game_port: int):
        """Create service for gameserver."""
        metadata = V1ObjectMeta(
            name=f"gameserver-{server_id}",
            labels={
                "app": "gameserver",
                "owner": user_id,
                "server-id": server_id
            }
        )

        spec = V1ServiceSpec(
            selector={
                "app": "gameserver",
                "server-id": server_id
            },
            ports=[
                V1ServicePort(
                    name="game-port",
                    app_protocol="TCP",
                    protocol="TCP",
                    target_port="game-port",
                    port=game_port
                )
            ]
        )

        service = V1Service(
            api_version="v1",
            metadata=metadata,
            spec=spec
        )

        self.v1_api.create_namespaced_service(
            namespace=self.namespace,
            body=service
        )

    def create_gameserver_traefik_route(self, server_id: str, user_id: str):
        """Create Traefik TCP IngressRoute for gameserver."""
        group = "traefik.io"
        version = "v1alpha1"
        plural = "ingressroutetcps"
        kind = "IngressRouteTCP"

        body = {
            "apiVersion": f"{group}/{version}",
            "kind": f"{kind}",
            "metadata": {
                "name": f"gameserver-{server_id}-route",
                "labels": {
                    "app": "gameserver",
                    "owner": user_id,
                    "server-id": server_id
                }
            },
            "spec": {
                "entryPoints": [
                    "web"
                ],
                "routes": [
                    {
                        "match": f"HostSNI(`*`)",
                        "services": [
                            {
                                "name": f"gameserver-{server_id}",
                                "port": "game-port"
                            }
                        ]
                    }
                ]
            }
        }

        self.crd_api.create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=self.namespace,
            plural=plural,
            body=body
        )

    # ========== DELETE METHODS ==========

    def delete_gameserver_config_map(self, server_id: str):
        """Delete configmap for gameserver."""
        self.v1_api.delete_namespaced_config_map(
            name=f"config-{server_id}",
            namespace=self.namespace
        )

    def delete_gameserver_deployment(self, server_id: str):
        """Delete deployment for gameserver."""
        self.v1_app_api.delete_namespaced_deployment(
            name=f"gameserver-{server_id}",
            namespace=self.namespace
        )

    def delete_gameserver_service(self, server_id: str):
        """Delete service for gameserver."""
        self.v1_api.delete_namespaced_service(
            name=f"gameserver-{server_id}",
            namespace=self.namespace
        )

    def delete_gameserver_traefik_route(self, server_id: str):
        """Delete Traefik route for gameserver."""
        self.crd_api.delete_namespaced_custom_object(
            group="traefik.io",
            version="v1alpha1",
            namespace=self.namespace,
            plural="ingressroutetcps",
            name=f"gameserver-{server_id}-route"
        )

    

k8_cl = K8sClient()
