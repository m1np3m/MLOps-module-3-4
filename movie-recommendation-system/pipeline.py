import kfp
from kfp.components import load_component_from_file
from kfp import dsl
from kfp.dsl import ExitHandler, RUN_ID_PLACEHOLDER
from kubernetes.client.models import V1Volume
from utils.kfp_utils import *
from config.config import *
import argparse

# load components
data_downloading_op = load_component_from_file(
    f"{COMPONENTS_DIR}/data_downloading/component.yaml"
)
data_preprocessing_op = load_component_from_file(
    f"{COMPONENTS_DIR}/data_preprocessing/component.yaml"
)
model_training_op = load_component_from_file(
    f"{COMPONENTS_DIR}/model_training/component.yaml"
)
model_evaluation_op = load_component_from_file(
    f"{COMPONENTS_DIR}/model_evaluation/component.yaml"
)
feature_store_op = load_component_from_file(
    f"{COMPONENTS_DIR}/feature_store/component.yaml"
)

vop = dsl.VolumeOp(name="creds_volume", resource_name="mypvc", size="1Gi")


# Define a pipeline and create a task from above components:
@dsl.pipeline(name=PIPELINE_NAME, description=PIPELINE_DESCRIPTION)
def pipeline(url: str):
    # data_downloading_task = data_downloading_op(url=url)
    # data_preprocessing_task = data_preprocessing_op(
    #     input_df=data_downloading_task.outputs["data"]
    # )
    # model_training_task = model_training_op(df=data_preprocessing_task.outputs["df"])
    # model_evalution_task = model_evaluation_op(
    #     df=data_preprocessing_task.outputs["df"],
    #     matrix=model_training_task.outputs["matrix"],
    #     movie2idx=model_training_task.outputs["movie2idx"],
    # )
    feature_store_task = feature_store_op(url=url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true")
    args = parser.parse_args()
    pipeline_args = {}
    pipeline_args["url"] = DATA_URL.format(DRIVER_ORDERS_CSV)

    kf = KubeFlow(
        namespace=NAMESPACE,
        host=HOST,
        username=KF_USERNAME,
        password=KF_PASSWORD,
    )
    client = kf.client

    pipeline_package_path = f"./pipeline_{PIPELINE_VERSION}.yaml"

    # pipeline config
    pipeline_conf = kfp.dsl.PipelineConf()
    # each stage in pipeline will have env variable
    env = {
        "ENVIRONMENT": {
            "type": "string",
            "value": "production" if not args.dev else "staging",
        },
    }
    _pipeline_conf = PipelineConfig(env)
    pipeline_conf.add_op_transformer(_pipeline_conf.pipeline_env_variables)
    # each stage in pipeline will be specified k8s resource
    # pipeline_conf.add_op_transformer(_pipeline_conf.pipeline_k8s)
    # Configures the max number of total parallel pods that can execute at the same time in a workflow.
    pipeline_conf.set_parallelism(NUM_PODS_PARALLEL)
    # check whether exp existed or not
    kfp_experiment = kf.get_or_create_experiment(EXPERIMENT_NAME)
    if args.dev:
        run_result = client.create_run_from_pipeline_func(
            experiment_name=kfp_experiment.name,
            pipeline_func=pipeline,
            arguments=pipeline_args,
            pipeline_conf=pipeline_conf,
        )
        print(run_result)
    else:
        kfp.compiler.Compiler().compile(
            pipeline_func=pipeline,
            package_path=pipeline_package_path,
            pipeline_conf=pipeline_conf,
        )
        # check to consider to whether create new pipeline or update pipeline's version
        pipeline_version = kf.create_or_update_pipeline(
            pipeline_name=PIPELINE_NAME,
            pipeline_description=PIPELINE_DESCRIPTION,
            version=PIPELINE_VERSION,
            path=pipeline_package_path,
        )
        # if pipeline's version existed
        print("checking pipeline version whether exists or not...")
        if pipeline_version.id != None:
            print(f"pipeline's version is {pipeline_version.id}")
            print("checking jobs...")
            jobs = client.list_recurring_runs(
                page_size=100,
                sort_by="Created_at desc",
                experiment_id=kfp_experiment.id,
            ).jobs
            if not jobs == None:
                print("removing all out-dated jobs...")
                for j in jobs:
                    # remove all out-dated cron jobs
                    client.delete_job(j.id)

        # create a new cron job for the latest version of pipeline
        try:
            print("creating the latest job")
            cron = client.create_recurring_run(
                experiment_id=kfp_experiment.id,
                job_name=JOB_NAME,
                description=JOB_DESCRIPTION,
                cron_expression=JOB_EXPRESSION,
                max_concurrency=1,
                version_id=pipeline_version.id,
                no_catchup=True,
                params=pipeline_args,
                enabled=True,
                service_account="default-editor",
            )
            print(f"cronjob's id: {cron.id}")
        except:
            print("Error in creating job")
