from backend.report.pdf_generator import PDFGenerator
from urllib.parse import urlparse

from backend.ai.prompt_builder import PromptBuilder
from backend.ai.gemini_client import GeminiClient

class RepositoryService:
    def __init__(self):

        self.parser = RepositoryParser()

        self.prompt_builder = PromptBuilder()
        
        self.gemini = GeminiClient()

        self.pdf_generator = PDFGenerator()

    def validate_repository_url(self, repo_url: str):
        """
        Validate if the given URL is a GitHub repository URL.
        """

        parsed_url = urlparse(repo_url)

        if parsed_url.scheme not in ("http", "https"):
            return False

        if parsed_url.netloc != "github.com":
            return False

        path_parts = parsed_url.path.strip("/").split("/")

        if len(path_parts) != 2:
            return False

        return True
    def _build_analysis(self, clone_path):
        """
        Builds and returns the complete repository analysis.
        """

        repository_info = self.parser.get_repository_info(clone_path)

        repository_info["total_commits"] = self.parser.get_commit_count(clone_path)

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

        analysis = {
            "repository_name": repository_info["repository_name"],
            "default_branch": repository_info["default_branch"],
            "total_branches": repository_info["total_branches"],
            "total_commits": repository_info["total_commits"],
            "total_contributors": repository_info["total_contributors"],
            "languages": repository_info["languages"],
            "dependencies": repository_info["dependencies"],
            "documentation": repository_info["documentation"],
            "configuration_files": repository_info["configurations"],
            "structure": repository_info["structure"],
            "statistics": repository_info["statistics"],
            "readme": self.parser.get_readme_content(clone_path)
        }

        repository_info["analysis"] = analysis

        return repository_info
    def analyze_repository(self, repo_url: str):

        if not self.validate_repository_url(repo_url):
            return {
                "status": "error",
                "message": "Invalid GitHub repository URL."
            }

        clone_path = self.parser.clone_repository(repo_url)

        repository_info = self._build_analysis(clone_path)

        analysis = repository_info["analysis"]

        prompt = self.prompt_builder.build_summary_prompt(analysis)

        summary = self.gemini.generate_response(prompt)

        repository_info["ai_summary"] = summary
        recommendation_prompt = self.prompt_builder.build_recommendation_prompt(
            analysis
        )

        recommendations = self.gemini.generate_response(
            recommendation_prompt
        )

        repository_info["ai_recommendations"] = recommendations

        return repository_info
    def ask_question(self, repo_url: str, question: str):
        """
        Answers a user's question about the repository.
        """

        if not self.validate_repository_url(repo_url):
            return {
                "status": "error",
                "message": "Invalid GitHub repository URL."
            }

        clone_path = self.parser.clone_repository(repo_url)

        repository_info = self._build_analysis(clone_path)

        analysis = repository_info["analysis"]

        prompt = self.prompt_builder.build_qa_prompt(
            analysis,
            question
        )

        answer = self.gemini.generate_response(prompt)

        return {
            "repository": analysis["repository_name"],
            "question": question,
            "answer": answer
        }
    def generate_pdf_report(self, repo_url):

        if not self.validate_repository_url(repo_url):
            return None

        clone_path = self.parser.clone_repository(repo_url)

        repository_info = self._build_analysis(clone_path)

        prompt = self.prompt_builder.build_summary_prompt(
            repository_info["analysis"]
        )

        summary = self.gemini.generate_response(prompt)

        repository_info["ai_summary"] = summary
        recommendation_prompt = self.prompt_builder.build_recommendation_prompt(
            repository_info["analysis"]
        )

        recommendations = self.gemini.generate_response(
            recommendation_prompt
        )

        repository_info["ai_recommendations"] = recommendations
        filename = "Repository_Analysis_Report.pdf"

        self.pdf_generator.generate_report(
            repository_info,
            filename
        )

        return filename