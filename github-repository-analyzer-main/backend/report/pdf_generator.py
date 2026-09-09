import os
import tempfile
import uuid

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFGenerator:
    """
    Generates a PDF report for a GitHub repository analysis.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()

        self.title_style = self.styles["Title"]
        self.title_style.alignment = TA_CENTER

        self.heading_style = self.styles["Heading1"]
        self.normal_style = self.styles["BodyText"]

    # ---------------------------------------------------------
    # Utility methods
    # ---------------------------------------------------------

    def _safe_text(self, value, default="Unavailable"):
        """
        Convert any value into safe text for ReportLab.
        """

        if value is None:
            return default

        if isinstance(value, (dict, list, tuple)):
            return str(value)

        text = str(value).strip()

        return text if text else default

    def _safe_list(self, value):
        """
        Convert a value into a list safely.
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        return [value]

    def _create_chart_path(self, prefix):
        """
        Create a unique temporary path for chart images.
        """

        filename = f"{prefix}_{uuid.uuid4().hex}.png"

        return os.path.join(
            tempfile.gettempdir(),
            filename
        )

    def _cleanup_file(self, path):
        """
        Safely remove a temporary chart file.
        """

        if not path:
            return

        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass

    # ---------------------------------------------------------
    # Language Chart
    # ---------------------------------------------------------

    def create_language_chart(self, languages):
        """
        Create a programming-language pie chart.

        Returns:
            Path to generated chart or None when no language data exists.
        """

        if not isinstance(languages, dict):
            return None

        cleaned_languages = {}

        for language, count in languages.items():
            try:
                count = int(count)
            except (TypeError, ValueError):
                continue

            if count > 0:
                cleaned_languages[str(language)] = count

        if not cleaned_languages:
            return None

        labels = list(cleaned_languages.keys())
        sizes = list(cleaned_languages.values())

        chart_path = self._create_chart_path("language_chart")

        figure = plt.figure(figsize=(5, 5))

        try:
            plt.pie(
                sizes,
                labels=labels,
                autopct="%1.1f%%",
                startangle=140
            )

            plt.title("Programming Languages")

            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )

        finally:
            plt.close(figure)

        return chart_path

    # ---------------------------------------------------------
    # Hotspot Chart
    # ---------------------------------------------------------

    def create_hotspot_chart(self, hotspot_files):
        """
        Create a chart showing the top hotspot files.
        """

        if not isinstance(hotspot_files, list):
            return None

        valid_items = []

        for item in hotspot_files[:10]:

            if not isinstance(item, (list, tuple)):
                continue

            if len(item) < 2:
                continue

            file_name = self._safe_text(
                item[0],
                "Unknown file"
            )

            try:
                commits = int(item[1])
            except (TypeError, ValueError):
                continue

            valid_items.append(
                (file_name, commits)
            )

        if not valid_items:
            return None

        files = [
            item[0]
            for item in valid_items
        ]

        commits = [
            item[1]
            for item in valid_items
        ]

        chart_path = self._create_chart_path(
            "hotspot_chart"
        )

        figure = plt.figure(figsize=(8, 5))

        try:
            plt.barh(
                files,
                commits
            )

            plt.title(
                "Top 10 Hotspot Files"
            )

            plt.xlabel(
                "Number of Commits"
            )

            plt.tight_layout()

            plt.savefig(
                chart_path,
                bbox_inches="tight"
            )

        finally:
            plt.close(figure)

        return chart_path

    # ---------------------------------------------------------
    # Main PDF generation
    # ---------------------------------------------------------

    def generate_report(self, data, filename):
        """
        Generate the complete repository analysis PDF.
        """

        if not isinstance(data, dict):
            raise ValueError(
                "PDF report data must be a dictionary."
            )

        if not filename:
            raise ValueError(
                "PDF filename cannot be empty."
            )

        chart_paths = []

        document = SimpleDocTemplate(
            filename,
            title="GitHub Repository Analysis Report"
        )

        elements = []

        # -----------------------------------------------------
        # Basic repository information
        # -----------------------------------------------------

        repository_name = self._safe_text(
            data.get("repository_name"),
            "Unknown Repository"
        )

        default_branch = self._safe_text(
            data.get("default_branch"),
            "Unknown"
        )

        total_branches = data.get(
            "total_branches",
            0
        )

        total_commits = data.get(
            "total_commits",
            0
        )

        total_contributors = data.get(
            "total_contributors",
            0
        )

        languages = data.get(
            "languages",
            {}
        )

        dependencies = data.get(
            "dependencies",
            []
        )

        hotspot_files = data.get(
            "hotspot_files",
            []
        )

        statistics = data.get(
            "statistics",
            {}
        )

        if not isinstance(statistics, dict):
            statistics = {}

        # -----------------------------------------------------
        # Cover Page
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "GitHub Repository Analysis Report",
                self.title_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        elements.append(
            Paragraph(
                "Generated by GitHub Repository Analyzer "
                "with AI Assistant",
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.6 * inch
            )
        )

        # -----------------------------------------------------
        # Repository Overview
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "Repository Overview",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        overview_data = [
            [
                "Repository Name",
                repository_name
            ],
            [
                "Default Branch",
                self._safe_text(
                    default_branch,
                    "Unknown"
                )
            ],
            [
                "Branches",
                self._safe_text(
                    total_branches,
                    "0"
                )
            ],
            [
                "Commits",
                self._safe_text(
                    total_commits,
                    "0"
                )
            ],
            [
                "Contributors",
                self._safe_text(
                    total_contributors,
                    "0"
                )
            ],
        ]

        overview_table = Table(
            overview_data,
            colWidths=[
                180,
                250
            ]
        )

        overview_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.darkblue
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (0, -1),
                        colors.white
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, -1),
                        colors.beige
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold"
                    ),
                ]
            )
        )

        elements.append(
            overview_table
        )

        elements.append(
            Spacer(
                1,
                0.5 * inch
            )
        )

        # -----------------------------------------------------
        # Repository Statistics
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "Repository Statistics",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        statistics_table_data = [
            [
                "Statistic",
                "Value"
            ],
            [
                "Total Files",
                self._safe_text(
                    statistics.get(
                        "total_files",
                        0
                    ),
                    "0"
                )
            ],
            [
                "Total Directories",
                self._safe_text(
                    statistics.get(
                        "total_directories",
                        0
                    ),
                    "0"
                )
            ],
        ]

        statistics_table = Table(
            statistics_table_data,
            colWidths=[
                220,
                180
            ]
        )

        statistics_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkgreen
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold"
                    ),
                ]
            )
        )

        elements.append(
            statistics_table
        )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # Programming Languages
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "Programming Languages",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        language_data = [
            [
                "Language",
                "Files",
                "Percentage"
            ]
        ]

        if isinstance(languages, dict):
            valid_languages = {}

            for language, count in languages.items():
                try:
                    count = int(count)
                except (TypeError, ValueError):
                    continue

                if count > 0:
                    valid_languages[
                        str(language)
                    ] = count

            languages = valid_languages

        else:
            languages = {}

        total_language_files = sum(
            languages.values()
        )

        if total_language_files > 0:

            for language, count in languages.items():

                percentage = (
                    count /
                    total_language_files
                ) * 100

                language_data.append(
                    [
                        language,
                        str(count),
                        f"{percentage:.1f}%"
                    ]
                )

        else:

            language_data.append(
                [
                    "No languages detected",
                    "0",
                    "0.0%"
                ]
            )

        language_table = Table(
            language_data,
            colWidths=[
                180,
                100,
                120
            ]
        )

        language_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.navy
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.beige
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold"
                    ),
                ]
            )
        )

        elements.append(
            language_table
        )

        # -----------------------------------------------------
        # Language Pie Chart
        # -----------------------------------------------------

        language_chart = (
            self.create_language_chart(
                languages
            )
        )

        if language_chart:

            chart_paths.append(
                language_chart
            )

            elements.append(
                Spacer(
                    1,
                    0.2 * inch
                )
            )

            elements.append(
                Image(
                    language_chart,
                    width=250,
                    height=250
                )
            )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # Dependencies
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "Dependencies",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        dependency_data = [
            ["Dependency"]
        ]

        dependency_list = self._safe_list(
            dependencies
        )

        if dependency_list:

            for dependency in dependency_list:

                dependency_data.append(
                    [
                        self._safe_text(
                            dependency,
                            "Unknown"
                        )
                    ]
                )

        else:

            dependency_data.append(
                ["No dependencies found"]
            )

        dependency_table = Table(
            dependency_data,
            colWidths=[350]
        )

        dependency_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkgreen
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold"
                    ),
                ]
            )
        )

        elements.append(
            dependency_table
        )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # Hotspot Files
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "Hotspot Files",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        hotspot_data = [
            [
                "File",
                "Commits"
            ]
        ]

        valid_hotspots = []

        if isinstance(
            hotspot_files,
            list
        ):

            for item in hotspot_files:

                if not isinstance(
                    item,
                    (list, tuple)
                ):
                    continue

                if len(item) < 2:
                    continue

                file_name = self._safe_text(
                    item[0],
                    "Unknown file"
                )

                try:
                    commits = int(item[1])
                except (
                    TypeError,
                    ValueError
                ):
                    continue

                valid_hotspots.append(
                    (
                        file_name,
                        commits
                    )
                )

        if valid_hotspots:

            for file_name, commits in valid_hotspots:

                hotspot_data.append(
                    [
                        file_name,
                        str(commits)
                    ]
                )

        else:

            hotspot_data.append(
                [
                    "No hotspot files found",
                    "-"
                ]
            )

        hotspot_table = Table(
            hotspot_data,
            colWidths=[
                320,
                80
            ]
        )

        hotspot_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.darkred
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.grey
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.beige
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, -1),
                        "Helvetica-Bold"
                    ),
                ]
            )
        )

        elements.append(
            hotspot_table
        )

        # -----------------------------------------------------
        # Hotspot Chart
        # -----------------------------------------------------

        hotspot_chart = (
            self.create_hotspot_chart(
                valid_hotspots
            )
        )

        if hotspot_chart:

            chart_paths.append(
                hotspot_chart
            )

            elements.append(
                Spacer(
                    1,
                    0.2 * inch
                )
            )

            elements.append(
                Image(
                    hotspot_chart,
                    width=420,
                    height=260
                )
            )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # AI Summary
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "AI Repository Summary",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        summary = data.get(
            "ai_summary",
            {}
        )

        if not isinstance(
            summary,
            dict
        ):
            summary = {}

        elements.append(
            Paragraph(
                "<b>Repository Purpose</b>",
                self.normal_style
            )
        )

        elements.append(
            Paragraph(
                self._safe_text(
                    summary.get(
                        "repository_purpose"
                    ),
                    "Unavailable."
                ),
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Technologies
        elements.append(
            Paragraph(
                "<b>Technologies Used</b>",
                self.normal_style
            )
        )

        technologies = self._safe_list(
            summary.get(
                "technologies_used",
                []
            )
        )

        if technologies:

            for tech in technologies:

                elements.append(
                    Paragraph(
                        f"• {self._safe_text(tech)}",
                        self.normal_style
                    )
                )

        else:

            elements.append(
                Paragraph(
                    "No technology information available.",
                    self.normal_style
                )
            )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Project Organization
        elements.append(
            Paragraph(
                "<b>Project Organization</b>",
                self.normal_style
            )
        )

        elements.append(
            Paragraph(
                self._safe_text(
                    summary.get(
                        "project_organization"
                    ),
                    "Unavailable."
                ),
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Intended Users
        elements.append(
            Paragraph(
                "<b>Intended Users</b>",
                self.normal_style
            )
        )

        elements.append(
            Paragraph(
                self._safe_text(
                    summary.get(
                        "intended_users"
                    ),
                    "Unavailable."
                ),
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Beginner Summary
        elements.append(
            Paragraph(
                "<b>Beginner Summary</b>",
                self.normal_style
            )
        )

        elements.append(
            Paragraph(
                self._safe_text(
                    summary.get(
                        "beginner_summary"
                    ),
                    "Unavailable."
                ),
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # AI Recommendations
        # -----------------------------------------------------

        elements.append(
            Paragraph(
                "AI Recommendations",
                self.heading_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.2 * inch
            )
        )

        recommendations = data.get(
            "ai_recommendations",
            {}
        )

        if not isinstance(
            recommendations,
            dict
        ):
            recommendations = {}

        # Strengths
        elements.append(
            Paragraph(
                "<b>Repository Strengths</b>",
                self.normal_style
            )
        )

        strengths = self._safe_list(
            recommendations.get(
                "strengths",
                []
            )
        )

        if strengths:

            for strength in strengths:

                elements.append(
                    Paragraph(
                        f"✔ {self._safe_text(strength)}",
                        self.normal_style
                    )
                )

        else:

            elements.append(
                Paragraph(
                    "No strengths available.",
                    self.normal_style
                )
            )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Areas for Improvement
        elements.append(
            Paragraph(
                "<b>Areas for Improvement</b>",
                self.normal_style
            )
        )

        improvements = self._safe_list(
            recommendations.get(
                "areas_for_improvement",
                []
            )
        )

        if improvements:

            for improvement in improvements:

                elements.append(
                    Paragraph(
                        f"• {self._safe_text(improvement)}",
                        self.normal_style
                    )
                )

        else:

            elements.append(
                Paragraph(
                    "No improvement recommendations available.",
                    self.normal_style
                )
            )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Best Practices
        elements.append(
            Paragraph(
                "<b>Best Practices</b>",
                self.normal_style
            )
        )

        best_practices = self._safe_list(
            recommendations.get(
                "best_practices",
                []
            )
        )

        if best_practices:

            for practice in best_practices:

                elements.append(
                    Paragraph(
                        f"• {self._safe_text(practice)}",
                        self.normal_style
                    )
                )

        else:

            elements.append(
                Paragraph(
                    "No best-practice recommendations available.",
                    self.normal_style
                )
            )

        elements.append(
            Spacer(
                1,
                0.15 * inch
            )
        )

        # Overall Quality
        elements.append(
            Paragraph(
                "<b>Overall Repository Quality</b>",
                self.normal_style
            )
        )

        elements.append(
            Paragraph(
                self._safe_text(
                    recommendations.get(
                        "overall_quality"
                    ),
                    "Unavailable."
                ),
                self.normal_style
            )
        )

        elements.append(
            Spacer(
                1,
                0.4 * inch
            )
        )

        # -----------------------------------------------------
        # Build PDF
        # -----------------------------------------------------

        try:

            document.build(
                elements
            )

        finally:

            for chart_path in chart_paths:
                self._cleanup_file(
                    chart_path
                )