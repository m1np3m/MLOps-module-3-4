import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from common.git_common import Git


def materialize_feature_store():
    import os, sys
    import joblib
    import feast
    import subprocess
    import subprocess
    from datetime import datetime
    import time

    git = Git()

    repo_url = "git@github.com:m1np3m/MLOps-module-3-4.git"
    local_path = "feature_store/"
    FORMAT_STRING = "%Y-%m-%dT%H:%M:%S"

    try:
        now = datetime.now()
        now = now.strftime(FORMAT_STRING)

        clone_success = git.clone(repo_url, local_path)
        if clone_success:
            print(f"\n--- Cloned to {local_path}---")
        else:
            sys.exit(1)

        # Materialize feature store
        print(f"\n--- Materializing feature store---")
        os.chdir(local_path + "movie-recommendation-system/feast/feature_repo")
        # Replace subprocess by sdk
        # repo_config = RepoConfig(
        #     registry=RegistryConfig(path="s3://[YOUR BUCKET]/registry.pb"),
        #     project="feast_demo_aws",
        #     provider="aws",
        #     offline_store="file",
        #     online_store=DynamoDBOnlineStoreConfig(region="us-west-2")
        # )
        # store = FeatureStore(config=repo_config)
        # store.materialize_incremental(datetime.datetime.now())
        subprocess.run(["feast", "materialize-incremental", now])
        # Diffs
        diffs = git.diff()
        print(f"Changes files: {diffs}")

        # Git add
        print(f"\n--- Adding changes to git---")
        git.add_changes(diffs)
        subprocess.run(["git", "status"])
        # Git commit
        # $ git commit -m <message>
        print(f"\n--- Commit changes to git---")
        git.commit("Update registry.db by python")
        print(f"\n--- Pusing changes to git---")
        git.push("main")
        print("Done")
    except Exception as e:
        print(e)

    # while True:
    #     time.sleep(1)


if __name__ == "__main__":
    print("building materializing component...")
    materialize_feature_store_op = func_to_container_op(
        func=materialize_feature_store,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=["config.config", "utils.feast_utils", "common.git_common"],
        packages_to_install=[
            "joblib",
            "cloudpickle",
            "kfp==1.8.22",
            "feast[postgres]",
            "feast[redis]",
            "GitPython",
            "psycopg2",
        ],
        use_code_pickling=True,
        base_image="manpham1999/kubeflow-feast:latest",
    )
