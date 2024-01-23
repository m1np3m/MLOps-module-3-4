import kfp
from kfp.components import InputPath, OutputPath
from kfp.components import func_to_container_op
import sys, os


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.config import *
from utils.feast_utils import FEAST


def materialize_feature_store():
    import os, sys
    import joblib
    import feast
    import subprocess
    from git import Repo
    import subprocess
    from datetime import datetime
    import time
    from pathlib import Path
    from feast import RepoConfig, FeatureStore
    from feast.infra.registry.contrib.postgres.postgres_registry_store import (
        PostgresRegistryConfig,
    )
    from feast.infra.offline_stores.contrib.postgres_offline_store.postgres import (
        PostgreSQLOfflineStoreConfig,
    )
    from feast.infra.online_stores.redis import RedisOnlineStoreConfig

    ssh_path = "/root/.ssh/"
    Path(ssh_path).mkdir(parents=True, exist_ok=True)

    print("\n--- Set up ssh keys and hosts ---")
    config_file = open(f"{ssh_path}config", "w")
    config_file.write(
        f"""Host github.com
                StrictHostKeyChecking no"""
    )
    config_file.close()

    subprocess.run(
        ["ssh-keyscan", "-t", "rsa", "github.com", ">>", f"{ssh_path}known_hosts"]
    )

    SSH_PRIVATE_KEY = os.getenv("SSH_PRIVATE_KEY")
    private_file = open(f"{ssh_path}id_rsa", "w")
    private_file.write(f"""{SSH_PRIVATE_KEY}""")
    private_file.close()

    subprocess.run(["chmod", "400", f"{ssh_path}id_rsa"])

    SSH_PUBLIC_KEY = os.getenv("SSH_PUBLIC_KEY")
    public_file = open(f"{ssh_path}id_rsa.pub", "w")
    public_file.write(f"""{SSH_PUBLIC_KEY}""")
    public_file.close()

    repo_url = "git@github.com:m1np3m/MLOps-module-3-4.git"
    local_path = "feature_store/"
    FORMAT_STRING = "%Y-%m-%dT%H:%M:%S"

    try:
        now = datetime.now()
        now = now.strftime(FORMAT_STRING)

        repo = Repo.clone_from(repo_url, local_path)
        print(f"\n--- Cloning {repo}---")

        # Materialize feature store
        print(f"\n--- Materialize feature store---")
        subprocess.run("pwd")
        os.chdir(local_path + "movie-recommendation-system/feast/feature_repo")
        subprocess.run("pwd")
        subprocess.run("ls")

        subprocess.run(["feast", "materialize-incremental", now])
        # Diffs
        diffs = repo.index.diff(None)
        files = []
        for d in diffs:
            files.append(d.a_path)
            print(d.a_path)

        # Git add
        print(f"\n--- Adding changes to git---")
        repo.index.add(files)
        subprocess.run(["git", "status"])

        # Git commit
        # $ git commit -m <message>
        print(f"\n--- Commit changes to git---")
        repo.index.commit("Update registry.db by python")
        # Git push
        origin = repo.remote(name="origin")

        print(f"\n--- Pusing changes to git---")

        origin.push("main")
        # subprocess.run(["git", "push", "origin", "main"])
        print("Done")
    except Exception as e:
        print(e)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    print("building materializing component...")
    materialize_feature_store_op = func_to_container_op(
        func=materialize_feature_store,
        output_component_file=__file__.replace(".py", ".yaml"),
        modules_to_capture=[
            "config.config",
            "utils.feast_utils",
        ],
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
