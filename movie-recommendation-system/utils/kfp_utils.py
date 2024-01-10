import logging
import kfp
import requests
from kubernetes.client.models import (
    V1EnvVar,
    V1NodeAffinity,
    V1NodeSelector,
    V1NodeSelectorTerm,
    V1NodeSelectorRequirement,
    V1Volume,
)
from kfp.dsl import ExitHandler
from kubernetes.client import (
    V1Affinity,
    V1SecretVolumeSource,
    V1EnvVarSource,
    V1SecretKeySelector,
)
from kubernetes.client.models.v1_toleration import V1Toleration
from kubernetes.client import V1Affinity, V1EnvVarSource, V1SecretKeySelector
import os, sys
import datetime


class KubeFlow:
    """A class used for connecting to Kubeflow cluster"""

    def __init__(self, namespace: str, host: str, username: str, password: str) -> None:
        self.namespace = namespace
        self.host = host
        self.username = username
        self.password = password
        self.cookies = get_session_cookie(self.host, self.username, self.password)
        self.client = kfp_client(self.cookies, self.namespace, self.host)

    def create_or_update_pipeline(
        self, pipeline_name: str, pipeline_description: str, version: str, path: str
    ):
        pipeline_id = self.client.get_pipeline_id(pipeline_name)
        # If no pipeline found by name, create a new pipeline
        # Else get the latest pipeline version
        if pipeline_id is None:
            logging.info(f"Creating a new pipeline: {pipeline_name}")
            pipeline = self.client.upload_pipeline(
                pipeline_package_path=path,
                pipeline_name=pipeline_name,
                description=pipeline_description,
            )
            pipeline_id = pipeline.id
        else:
            pipeline = self.client.get_pipeline(pipeline_id)
            pipeline_id = pipeline.id

        # Always try to upload a pipeline version.
        pipeline_version = self.client.upload_pipeline_version(
            pipeline_package_path=path,
            pipeline_version_name=f"{pipeline_name} {version}",
            pipeline_id=pipeline_id,
        )

        return pipeline_version

    def get_or_create_experiment(self, name: str):
        try:
            experiment = self.client.get_experiment(experiment_name=name)
        except Exception:
            print(f"Creating new experiment: {name}")
            experiment = self.client.create_experiment(name)

        return experiment


def kfp_client(session_cookie, namespace, host):
    """
    Kubeflow pipelines client. Requires portforwarding to call from localhost.
    """
    client = kfp.Client(
        host=f"{host}/pipeline",
        cookies=f"authservice_session={session_cookie}",
        namespace=namespace,
    )
    client._context_setting["namespace"] = namespace

    return client


def get_session_cookie(host, username, password):
    session = requests.Session()
    response = session.get(host)
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"login": username, "password": password}
    session.post(response.url, headers=headers, data=data)
    session_cookie = session.cookies.get_dict()["authservice_session"]

    return session_cookie


class PipelineConfig:
    def __init__(self, env_var: dict):
        self.env_var = env_var

    def pipeline_env_variables(self, op):
        # add environment variables
        for name, value in self.env_var.items():
            try:
                if value.get("type") == "secret":
                    op = op.add_env_variable(
                        V1EnvVar(
                            name=name,
                            value_from=V1EnvVarSource(
                                secret_key_ref=V1SecretKeySelector(
                                    name="jenkins-token", key=value.get("value")
                                )
                            ),
                        )
                    )
                else:
                    op = op.add_env_variable(V1EnvVar(name, value.get("value")))
            except:
                pass
        return op

    def pipeline_k8s(self, op):
        op.add_affinity(
            V1Affinity(
                node_affinity=V1NodeAffinity(
                    required_during_scheduling_ignored_during_execution=V1NodeSelector(
                        node_selector_terms=[
                            V1NodeSelectorTerm(
                                match_expressions=[
                                    V1NodeSelectorRequirement(
                                        key="lifecycle",
                                        operator="In",
                                        values=["training-pipeline"],
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
        )

        op.add_toleration(
            tolerations=V1Toleration(
                key="training-pipeline",
                value="true",
                effect="NoSchedule",
            )
        )
        op.set_cpu_request("3")
        op.set_memory_request("28000Mi")
        op.set_retry(num_retries=3)
        return op
