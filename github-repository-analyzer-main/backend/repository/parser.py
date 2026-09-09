import json
import os
import shutil
import stat
import time
import uuid

from git import Repo


class RepositoryParser:
    """
    Handles GitHub repository cloning and repository analysis.

    Designed to work reliably on Windows by:
    - Avoiding reuse of old Git clone directories
    - Ignoring the .git directory during analysis
    - Handling read-only Git files
    - Retrying cleanup operations
    - Supporting common programming languages and dependency files
    """

    REPOSITORIES_DIR = "repositories"

    # ---------------------------------------------------------
    # Windows-safe file deletion
    # ---------------------------------------------------------

    @staticmethod
    def _remove_readonly(func, path, exc_info):
        """
        Remove read-only protection from a Windows file and retry
        the failed filesystem operation.
        """

        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except FileNotFoundError:
            pass

    @classmethod
    def _safe_remove_directory(cls, path, retries=5, delay=0.5):
        """
        Safely remove a directory on Windows.

        Git's .git/objects/pack files can occasionally be locked
        by Windows, antivirus software, or Git processes.
        """

        if not os.path.exists(path):
            return True

        for attempt in range(retries):
            try:
                shutil.rmtree(
                    path,
                    onerror=cls._remove_readonly
                )

                if not os.path.exists(path):
                    return True

            except Exception:
                pass

            time.sleep(delay)

        return not os.path.exists(path)

    # ---------------------------------------------------------
    # Clone repository
    # ---------------------------------------------------------

    def clone_repository(self, repo_url):
        """
        Clone a GitHub repository into a unique local directory.

        A unique directory is intentionally used for every analysis.
        This prevents Windows file-lock problems caused by reusing
        an existing .git directory.
        """

        repo_url = repo_url.strip().rstrip("/")

        # Extract repository name
        repo_name = repo_url.split("/")[-1]

        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        # Sanitize repository name
        safe_repo_name = "".join(
            character
            for character in repo_name
            if character.isalnum() or character in ("-", "_", ".")
        )

        if not safe_repo_name:
            safe_repo_name = "repository"

        # Make sure repositories directory exists
        os.makedirs(
            self.REPOSITORIES_DIR,
            exist_ok=True
        )

        # -----------------------------------------------------
        # IMPORTANT:
        # Use a unique directory for every clone.
        # -----------------------------------------------------

        unique_id = uuid.uuid4().hex[:8]

        clone_folder_name = (
            f"{safe_repo_name}_{unique_id}"
        )

        clone_path = os.path.abspath(
            os.path.join(
                self.REPOSITORIES_DIR,
                clone_folder_name
            )
        )

        try:
            Repo.clone_from(
                repo_url,
                clone_path
            )

        except Exception as exc:

            # Clean up partially-created repository
            self._safe_remove_directory(
                clone_path
            )

            raise RuntimeError(
                f"Unable to clone repository: {exc}"
            ) from exc

        return clone_path

    # ---------------------------------------------------------
    # Repository traversal
    # ---------------------------------------------------------

    def _walk_repository(self, clone_path):
        """
        Walk repository files while excluding .git.

        Git's internal database can contain thousands of files
        and Windows can lock some of them. It should never be
        included in normal repository analysis.
        """

        for root, dirs, files in os.walk(
            clone_path,
            topdown=True
        ):

            # Never enter .git
            dirs[:] = [
                directory
                for directory in dirs
                if directory != ".git"
            ]

            yield root, dirs, files

    # ---------------------------------------------------------
    # Basic repository information
    # ---------------------------------------------------------

    def get_repository_info(self, clone_path):
        """
        Returns basic information about the cloned repository.
        """

        repo = Repo(clone_path)

        try:
            default_branch = repo.active_branch.name

        except TypeError:
            default_branch = "unknown"

        except Exception:
            default_branch = "unknown"

        return {
            "repository_name": os.path.basename(
                clone_path
            ),

            "default_branch": default_branch,

            "total_branches": len(
                repo.branches
            ),

            "readme_found": any(
                os.path.exists(
                    os.path.join(
                        clone_path,
                        filename
                    )
                )
                for filename in [
                    "README.md",
                    "readme.md",
                    "README.txt"
                ]
            )
        }

    # ---------------------------------------------------------
    # Commit count
    # ---------------------------------------------------------

    def get_commit_count(self, clone_path):
        """
        Returns the total number of commits.
        """

        repo = Repo(clone_path)

        try:
            return sum(
                1
                for _ in repo.iter_commits()
            )

        except Exception:
            return 0

    # ---------------------------------------------------------
    # Contributors
    # ---------------------------------------------------------

    def get_contributors_count(self, clone_path):
        """
        Returns the number of unique contributors.
        """

        repo = Repo(clone_path)

        contributors = set()

        try:

            for commit in repo.iter_commits():

                if commit.author:

                    email = commit.author.email

                    if email:
                        contributors.add(
                            email.lower()
                        )

        except Exception:
            return 0

        return len(contributors)

    # ---------------------------------------------------------
    # Hotspot files
    # ---------------------------------------------------------

    def get_hotspot_files(self, clone_path):
        """
        Returns the top 10 most frequently modified files.
        """

        repo = Repo(clone_path)

        file_counts = {}

        try:

            for commit in repo.iter_commits():

                for file_name in commit.stats.files:

                    file_counts[file_name] = (
                        file_counts.get(
                            file_name,
                            0
                        ) + 1
                    )

        except Exception:
            return []

        sorted_files = sorted(
            file_counts.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return sorted_files[:10]

    # ---------------------------------------------------------
    # README
    # ---------------------------------------------------------

    def get_readme_content(self, clone_path):
        """
        Returns the contents of the repository README.
        """

        readme_files = [
            "README.md",
            "readme.md",
            "README.txt"
        ]

        for filename in readme_files:

            readme_path = os.path.join(
                clone_path,
                filename
            )

            if os.path.isfile(readme_path):

                try:

                    with open(
                        readme_path,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as file:

                        return file.read()

                except OSError:
                    continue

        return "README file not found."

    # ---------------------------------------------------------
    # Programming languages
    # ---------------------------------------------------------

    def get_languages(self, clone_path):
        """
        Returns programming languages detected by file extension.
        """

        extension_map = {

            ".py": "Python",

            ".js": "JavaScript",
            ".jsx": "JavaScript",

            ".ts": "TypeScript",
            ".tsx": "TypeScript",

            ".java": "Java",

            ".cpp": "C++",
            ".cc": "C++",
            ".cxx": "C++",

            ".c": "C",

            ".h": "C/C++",
            ".hpp": "C++",

            ".cs": "C#",

            ".html": "HTML",

            ".css": "CSS",
            ".scss": "SCSS",

            ".php": "PHP",

            ".go": "Go",

            ".rs": "Rust",

            ".rb": "Ruby",

            ".kt": "Kotlin",

            ".swift": "Swift",

            ".dart": "Dart",

            ".sql": "SQL"
        }

        language_counts = {}

        for root, _, files in self._walk_repository(
            clone_path
        ):

            for file_name in files:

                extension = os.path.splitext(
                    file_name
                )[1].lower()

                if extension in extension_map:

                    language = extension_map[
                        extension
                    ]

                    language_counts[language] = (
                        language_counts.get(
                            language,
                            0
                        ) + 1
                    )

        return dict(
            sorted(
                language_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    # ---------------------------------------------------------
    # Documentation files
    # ---------------------------------------------------------

    def get_documentation_files(self, clone_path):
        """
        Returns documentation files found in the repository.
        """

        documentation = []

        important_docs = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "SECURITY.md"
        }

        for root, _, files in self._walk_repository(
            clone_path
        ):

            for file_name in files:

                if (
                    file_name in important_docs
                    or file_name.lower().endswith(".md")
                ):

                    full_path = os.path.join(
                        root,
                        file_name
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        clone_path
                    )

                    documentation.append({
                        "name": file_name,
                        "path": relative_path
                    })

        return documentation

    # ---------------------------------------------------------
    # Configuration files
    # ---------------------------------------------------------

    def get_configuration_files(self, clone_path):
        """
        Returns important configuration files.
        """

        config_files = {

            "requirements.txt",
            "requirements-dev.txt",

            "pyproject.toml",

            "package.json",
            "package-lock.json",

            "yarn.lock",
            "pnpm-lock.yaml",

            "Dockerfile",
            "docker-compose.yml",

            ".gitignore",

            "pom.xml",
            "build.gradle",

            "Cargo.toml",

            "go.mod",

            "Gemfile",

            "composer.json"
        }

        configurations = []

        for root, _, files in self._walk_repository(
            clone_path
        ):

            for file_name in files:

                if file_name in config_files:

                    full_path = os.path.join(
                        root,
                        file_name
                    )

                    relative_path = os.path.relpath(
                        full_path,
                        clone_path
                    )

                    configurations.append({
                        "name": file_name,
                        "path": relative_path
                    })

        return configurations

    # ---------------------------------------------------------
    # Repository structure
    # ---------------------------------------------------------

    def get_repository_structure(self, clone_path):
        """
        Returns the top-level repository structure.
        """

        structure = {
            "folders": [],
            "files": []
        }

        try:

            for item in os.listdir(
                clone_path
            ):

                # Never expose .git
                if item == ".git":
                    continue

                item_path = os.path.join(
                    clone_path,
                    item
                )

                if os.path.isdir(item_path):

                    structure["folders"].append(
                        item
                    )

                elif os.path.isfile(item_path):

                    structure["files"].append(
                        item
                    )

        except OSError:
            pass

        structure["folders"].sort()
        structure["files"].sort()

        return structure

    # ---------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------

    def get_dependencies(self, clone_path):
        """
        Returns dependencies from common dependency files.
        """

        dependencies = []

        # -----------------------------------------------------
        # Python requirements
        # -----------------------------------------------------

        requirements_files = [
            "requirements.txt",
            "requirements-dev.txt"
        ]

        for filename in requirements_files:

            requirements_path = os.path.join(
                clone_path,
                filename
            )

            if not os.path.isfile(
                requirements_path
            ):
                continue

            try:

                with open(
                    requirements_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    for line in file:

                        line = line.strip()

                        if (
                            line
                            and not line.startswith("#")
                            and not line.startswith("-")
                        ):

                            dependencies.append(
                                line
                            )

            except OSError:
                continue

        # -----------------------------------------------------
        # Node.js package.json
        # -----------------------------------------------------

        package_json = os.path.join(
            clone_path,
            "package.json"
        )

        if os.path.isfile(package_json):

            try:

                with open(
                    package_json,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    package_data = json.load(file)

                for section in [
                    "dependencies",
                    "devDependencies"
                ]:

                    for name, version in package_data.get(
                        section,
                        {}
                    ).items():

                        dependencies.append(
                            f"{name}: {version}"
                        )

            except (
                json.JSONDecodeError,
                OSError
            ):
                pass

        return sorted(
            set(dependencies)
        )

    # ---------------------------------------------------------
    # File statistics
    # ---------------------------------------------------------

    def get_file_statistics(self, clone_path):
        """
        Returns basic repository file statistics.
        """

        stats = {
            "total_files": 0,
            "total_directories": 0
        }

        for root, dirs, files in self._walk_repository(
            clone_path
        ):

            stats["total_directories"] += len(
                dirs
            )

            stats["total_files"] += len(
                files
            )

        return stats