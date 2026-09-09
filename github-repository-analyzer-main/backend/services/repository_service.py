from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from backend.ai.gemini_client import GeminiClient
from backend.ai.prompt_builder import PromptBuilder
from backend.report.pdf_generator import PDFGenerator
from backend.repository.parser import RepositoryParser


class RepositoryService:
    """
    Main service responsible for:

    - GitHub repository validation
    - Repository cloning
    - Repository analysis
    - Gemini AI summaries
    - Gemini recommendations
    - Repository questions
    - PDF report generation
    """

    def __init__(self):
        self.parser = RepositoryParser()
        self.prompt_builder = PromptBuilder()
        self.gemini = GeminiClient()
        self.pdf_generator = PDFGenerator()

        # Stores repository URL -> local clone path.
        # This prevents unnecessary re-cloning during the same
        # application session.
        self._repository_cache = {}

    # ------------------------------------------------------------------
    # URL VALIDATION
    # ------------------------------------------------------------------

    def validate_repository_url(self, repo_url: str) -> bool:
        """
        Validate that the supplied URL points to a GitHub repository.

        Accepted examples:

            https://github.com/user/repository
            https://github.com/user/repository.git
            https://www.github.com/user/repository

        The application expects a public GitHub repository.
        """

        if not isinstance(repo_url, str):
            return False

        repo_url = repo_url.strip()

        if not repo_url:
            return False

        try:
            parsed_url = urlparse(repo_url)
        except Exception:
            return False

        if parsed_url.scheme not in ("http", "https"):
            return False

        hostname = (parsed_url.hostname or "").lower()

        if hostname not in ("github.com", "www.github.com"):
            return False

        path_parts = [
            part
            for part in parsed_url.path.strip("/").split("/")
            if part
        ]

        # GitHub repository URLs have:
        #
        # /owner/repository
        #
        if len(path_parts) != 2:
            return False

        owner = path_parts[0].strip()
        repository = path_parts[1].strip()

        if not owner or not repository:
            return False

        return True

    # ------------------------------------------------------------------
    # REPOSITORY MANAGEMENT
    # ------------------------------------------------------------------

    def _get_repository_key(self, repo_url: str) -> str:
        """
        Create a normalized key for repository caching.
        """

        repo_url = repo_url.strip().rstrip("/")

        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        return repo_url.lower()

    def _get_or_clone_repository(self, repo_url: str):
        """
        Return an existing valid local clone when possible.

        If the repository hasn't been cloned yet, clone it.

        This prevents Analyze -> Ask AI -> Generate PDF from cloning
        the same repository three separate times.
        """

        repo_key = self._get_repository_key(repo_url)

        cached_path = self._repository_cache.get(repo_key)

        if cached_path:
            cached_path = Path(cached_path)

            if cached_path.exists() and cached_path.is_dir():
                return str(cached_path)

            # Remove invalid cache entry.
            self._repository_cache.pop(repo_key, None)

        clone_path = self.parser.clone_repository(repo_url)

        if not clone_path:
            return None

        clone_path = Path(clone_path)

        if not clone_path.exists() or not clone_path.is_dir():
            return None

        self._repository_cache[repo_key] = str(clone_path)

        return str(clone_path)

    # ------------------------------------------------------------------
    # ANALYSIS
    # ------------------------------------------------------------------

    def _build_analysis(self, clone_path):
        """
        Build the complete repository analysis.
        """

        repository_info = self.parser.get_repository_info(
            clone_path
        )

        repository_info["total_commits"] = (
            self.parser.get_commit_count(clone_path)
        )

        repository_info["total_contributors"] = (
            self.parser.get_contributors_count(clone_path)
        )

        repository_info["hotspot_files"] = (
            self.parser.get_hotspot_files(clone_path)
        )

        repository_info["languages"] = (
            self.parser.get_languages(clone_path)
        )

        repository_info["documentation"] = (
            self.parser.get_documentation_files(clone_path)
        )

        repository_info["configurations"] = (
            self.parser.get_configuration_files(clone_path)
        )

        repository_info["structure"] = (
            self.parser.get_repository_structure(clone_path)
        )

        repository_info["dependencies"] = (
            self.parser.get_dependencies(clone_path)
        )

        repository_info["statistics"] = (
            self.parser.get_file_statistics(clone_path)
        )

        repository_info["readme"] = (
            self.parser.get_readme_content(clone_path)
        )

        analysis = {
            "repository_name": repository_info["repository_name"],
            "default_branch": repository_info["default_branch"],
            "total_branches": repository_info["total_branches"],
            "total_commits": repository_info["total_commits"],
            "total_contributors": repository_info[
                "total_contributors"
            ],
            "hotspot_files": repository_info["hotspot_files"],
            "languages": repository_info["languages"],
            "dependencies": repository_info["dependencies"],
            "documentation": repository_info["documentation"],
            "configuration_files": repository_info[
                "configurations"
            ],
            "structure": repository_info["structure"],
            "statistics": repository_info["statistics"],
            "readme": repository_info["readme"],
        }

        repository_info["analysis"] = analysis

        return repository_info

    # ------------------------------------------------------------------
    # AI HELPERS
    # ------------------------------------------------------------------

    def _default_ai_summary(self, message="AI service is currently unavailable."):
        """
        Return a consistent fallback AI summary.
        """

        return {
            "repository_purpose": "AI Summary unavailable.",
            "technologies_used": [],
            "project_organization": "Unavailable.",
            "intended_users": "Unavailable.",
            "beginner_summary": message,
        }

    def _default_ai_recommendations(self):
        """
        Return a consistent fallback recommendation structure.
        """

        return {
            "strengths": [],
            "areas_for_improvement": [],
            "best_practices": [],
            "overall_quality": "Unavailable",
        }

    def _generate_ai_summary(self, analysis):
        """
        Generate an AI summary while safely handling Gemini failures.
        """

        try:
            prompt = self.prompt_builder.build_summary_prompt(
                analysis
            )

            summary = self.gemini.generate_response(prompt)

            if isinstance(summary, dict):
                return summary

            return self._default_ai_summary(
                "AI service returned an unexpected response."
            )

        except Exception:
            return self._default_ai_summary()

    def _generate_ai_recommendations(self, analysis):
        """
        Generate AI recommendations while safely handling failures.
        """

        try:
            prompt = (
                self.prompt_builder.build_recommendation_prompt(
                    analysis
                )
            )

            recommendations = self.gemini.generate_response(
                prompt
            )

            if isinstance(recommendations, dict):
                return recommendations

            return self._default_ai_recommendations()

        except Exception:
            return self._default_ai_recommendations()

    # ------------------------------------------------------------------
    # MAIN ANALYSIS
    # ------------------------------------------------------------------

    def analyze_repository(self, repo_url: str):
        """
        Clone and completely analyze a GitHub repository.
        """

        repo_url = (
            repo_url.strip()
            if isinstance(repo_url, str)
            else ""
        )

        if not self.validate_repository_url(repo_url):
            return {
                "status": "error",
                "message": (
                    "Please enter a valid GitHub repository URL."
                ),
            }

        try:
            clone_path = self._get_or_clone_repository(
                repo_url
            )

            if clone_path is None:
                return {
                    "status": "error",
                    "message": (
                        "Unable to clone the repository. "
                        "Please check that it exists and is public."
                    ),
                }

            repository_info = self._build_analysis(
                clone_path
            )

            analysis = repository_info["analysis"]

            # AI Summary
            repository_info["ai_summary"] = (
                self._generate_ai_summary(analysis)
            )

            # AI Recommendations
            repository_info["ai_recommendations"] = (
                self._generate_ai_recommendations(analysis)
            )

            repository_info["status"] = "success"

            return repository_info

        except Exception as exc:
            return {
                "status": "error",
                "message": (
                    f"Repository analysis failed: {exc}"
                ),
            }

    # ------------------------------------------------------------------
    # ASK AI
    # ------------------------------------------------------------------

    def ask_question(
        self,
        repo_url: str,
        question: str,
    ):
        """
        Answer a user's question about the repository.

        The existing cloned repository is reused whenever possible.
        """

        repo_url = (
            repo_url.strip()
            if isinstance(repo_url, str)
            else ""
        )

        question = (
            question.strip()
            if isinstance(question, str)
            else ""
        )

        if not self.validate_repository_url(repo_url):
            return {
                "status": "error",
                "message": "Invalid GitHub repository URL.",
            }

        if not question:
            return {
                "status": "error",
                "message": "Please enter a question.",
            }

        try:
            clone_path = self._get_or_clone_repository(
                repo_url
            )

            if clone_path is None:
                return {
                    "status": "error",
                    "message": (
                        "Unable to access the repository."
                    ),
                }

            repository_info = self._build_analysis(
                clone_path
            )

            analysis = repository_info["analysis"]

            prompt = self.prompt_builder.build_qa_prompt(
                analysis,
                question,
            )

            answer = self.gemini.generate_response(
                prompt
            )

            return {
                "status": "success",
                "repository": analysis["repository_name"],
                "question": question,
                "answer": answer,
            }

        except Exception as exc:
            return {
                "status": "error",
                "message": (
                    f"Unable to answer the question: {exc}"
                ),
            }

    # ------------------------------------------------------------------
    # PDF REPORT
    # ------------------------------------------------------------------

    def generate_pdf_report(self, repo_url):
        """
        Generate a PDF report for a repository.

        The same repository clone is reused rather than cloning again.
        """

        repo_url = (
            repo_url.strip()
            if isinstance(repo_url, str)
            else ""
        )

        if not self.validate_repository_url(repo_url):
            return None

        try:
            clone_path = self._get_or_clone_repository(
                repo_url
            )

            if clone_path is None:
                return None

            repository_info = self._build_analysis(
                clone_path
            )

            analysis = repository_info["analysis"]

            # AI Summary
            repository_info["ai_summary"] = (
                self._generate_ai_summary(analysis)
            )

            # AI Recommendations
            repository_info["ai_recommendations"] = (
                self._generate_ai_recommendations(analysis)
            )

            # Make sure the reports directory exists.
            reports_directory = Path("reports")
            reports_directory.mkdir(
                parents=True,
                exist_ok=True,
            )

            repository_name = (
                repository_info.get(
                    "repository_name",
                    "Repository"
                )
            )

            # Create a safe filename.
            safe_name = "".join(
                character
                if character.isalnum()
                or character in ("-", "_")
                else "_"
                for character in repository_name
            )

            filename = (
                reports_directory
                / (
                    f"{safe_name}_Analysis_Report_"
                    f"{uuid4().hex[:8]}.pdf"
                )
            )

            self.pdf_generator.generate_report(
                repository_info,
                str(filename),
            )

            if not filename.exists():
                return None

            return str(filename)

        except Exception:
            return None