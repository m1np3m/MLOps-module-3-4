from pathlib import Path
import subprocess
import sys, os
from git import Repo


class Git:
    def __init__(self) -> None:
        self._set_up_ssh()
        return None

    def _set_up_ssh(
        self,
    ):
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

    def clone(self, url, local_path) -> bool:
        self.repo = Repo.clone_from(url, local_path)
        print(f"\n--- Cloning {self.repo.git_dir} to {local_path} ---")
        return os.path.exists(self.repo.git_dir)

    def diff(self) -> list[str]:
        diffs = self.repo.index.diff()
        files = []
        for d in diffs:
            files.append(d.a_path)
        return files

    def add_changes(self, files):
        """
        files: from diff()
        """
        # Git add
        print(f"\n--- Adding changes to git---")
        self.repo.index.add(files)

    def commit(self, message):
        self.repo.index.commit(message)

    def push(self, branch: str):
        subprocess.run(["git", "push", "origin", branch])
