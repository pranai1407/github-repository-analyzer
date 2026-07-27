from git import Repo
import os
import shutil


class RepositoryParser:

    def clone_repository(self, repo_url):
        repo_name = repo_url.split("/")[-1]

        clone_path = os.path.join("repositories", repo_name)

        # Delete existing folder if it already exists
        if os.path.exists(clone_path):
            shutil.rmtree(clone_path)

        Repo.clone_from(repo_url, clone_path)

        return clone_path
    def get_repository_info(self, clone_path):
        """
        Returns basic information about the cloned repository.
        """

        repo = Repo(clone_path)

        return {
            "repository_name": os.path.basename(clone_path),
            "default_branch": repo.active_branch.name,
            "total_branches": len(repo.branches),
            "readme_found": (
            os.path.exists(os.path.join(clone_path, "README.md"))
            or os.path.exists(os.path.join(clone_path, "readme.md"))
        )
    }
    def get_commit_count(self, clone_path):
        """
        Returns the total number of commits in the repository.
        """

        repo = Repo(clone_path)

        return sum(1 for _ in repo.iter_commits())
    def get_contributors_count(self, clone_path):
        """
        Returns the total number of unique contributors.
        """

        repo = Repo(clone_path)

        contributors = set()

        for commit in repo.iter_commits():
            if commit.author:
                contributors.add(commit.author.email) 

        return len(contributors)
    def get_hotspot_files(self, clone_path):
        """
        Returns the top 10 most frequently modified files.
        """

        repo = Repo(clone_path)

        file_counts = {}

        for commit in repo.iter_commits():
            for file in commit.stats.files:

                file_counts[file] = file_counts.get(file, 0) + 1

        sorted_files = sorted(
            file_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return sorted_files[:10]
    def get_readme_content(self, clone_path):
        """
        Returns the contents of the repository README file.
        """

        readme_files = [
                "README.md",
                "readme.md",
                "README.txt"
        ]

        for filename in readme_files:

             readme_path = os.path.join(clone_path, filename)

             if os.path.exists(readme_path):

                 with open(readme_path, "r", encoding="utf-8", errors="ignore") as file:
                    return file.read()

        return "README file not found."
    def get_languages(self, clone_path):
        """
        Returns the programming languages used in the repository.
        """

        extension_map = {
             ".py": "Python",
             ".js": "JavaScript",
             ".ts": "TypeScript",
            ".java": "Java",
             ".cpp": "C++",
             ".c": "C",
            ".cs": "C#",
             ".html": "HTML",
            ".css": "CSS",
            ".php": "PHP",
            ".go": "Go",
            ".rs": "Rust"
        }

        language_counts = {}

        for root, _, files in os.walk(clone_path):  

            for file in files:

                extension = os.path.splitext(file)[1]

                if extension in extension_map:
                    language = extension_map[extension]

                    language_counts[language] = (
                        language_counts.get(language, 0) + 1
                    )
        return language_counts
    def get_documentation_files(self, clone_path):
        """
        Returns important documentation files in the repository.
        """

        documentation_files = [
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md"
        ]

        found_files = []

        for root, _, files in os.walk(clone_path):

            for file in files:

                if file in documentation_files:
                    found_files.append(file)

        return found_files
    def get_documentation_files(self, clone_path):
        """
        Returns documentation files found in the repository.
        """

        documentation = []

        for root, _, files in os.walk(clone_path):

            for file in files:

                if file.lower().endswith(".md"):

                    relative_path = os.path.relpath(
                        os.path.join(root, file),
                        clone_path
                    )

                    documentation.append({
                        "name": file,
                        "path": relative_path
                    })

        return documentation
    def get_configuration_files(self, clone_path):
        """
        Returns important configuration files in the repository.
        """

        config_files = {
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "package-lock.json",
            "Dockerfile",
            "docker-compose.yml",
            ".gitignore",
            "pom.xml",
            "build.gradle",
            "Cargo.toml",
            "go.mod"
        }

        configurations = []

        for root, _, files in os.walk(clone_path):

            for file in files:

                if file in config_files:

                    relative_path = os.path.relpath(
                        os.path.join(root, file),
                        clone_path
                    )

                    configurations.append({
                        "name": file,
                        "path": relative_path
                    })

        return configurations
    def get_repository_structure(self, clone_path):
        """
        Returns the top-level structure of the repository.
        """

        structure = {
                "folders": [],
                "files": []
         }

        for item in os.listdir(clone_path):

            item_path = os.path.join(clone_path, item)

            if os.path.isdir(item_path):
                structure["folders"].append(item)

            elif os.path.isfile(item_path):
                structure["files"].append(item)

        structure["folders"].sort()
        structure["files"].sort()

        return structure
    def get_dependencies(self, clone_path):
        """
        Returns dependencies from requirements.txt if present.
        """

        requirements_path = os.path.join(clone_path, "requirements.txt")

        if not os.path.exists(requirements_path):
            return []

        dependencies = []

        with open(requirements_path, "r", encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if line and not line.startswith("#"):
                    dependencies.append(line)

        return dependencies
    def get_file_statistics(self, clone_path):
        """
        Returns basic file statistics for the repository.
        """

        stats = {
            "total_files": 0,
            "total_directories": 0
        }

        for root, dirs, files in os.walk(clone_path):

            stats["total_directories"] += len(dirs)
            stats["total_files"] += len(files)

        return stats
