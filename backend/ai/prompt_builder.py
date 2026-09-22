class PromptBuilder:
    """
    Builds prompts for different AI tasks.
    """

    def build_summary_prompt(self, analysis):

        return f"""
    You are an experienced software engineer.

    Analyze the following GitHub repository.

    Repository Name:
    {analysis["repository_name"]}

    Languages:
    {analysis["languages"]}

    Dependencies:
    {analysis["dependencies"]}  

    Repository Structure:
    {analysis["structure"]}

    Documentation:
    {analysis["documentation"]}

    README:
    {analysis["readme"]}

    IMPORTANT:

    Return ONLY valid JSON.

    Do not return Markdown.

    Do not return explanations.
    Do not wrap the JSON in ```.

    Return exactly in this format:

    {{
        "repository_purpose": "...",

        "technologies_used": [
            "...",
            "..."
        ],

        "project_organization": "...",

        "intended_users": "...",

        "beginner_summary": "..."
    }}
    """

    def build_qa_prompt(self, analysis, question):
    
            return f"""
        You are an experienced software engineer.

        Repository Information:

        Repository Name:
        {analysis["repository_name"]}

        Languages:
        {analysis["languages"]}

        Dependencies:
        {analysis["dependencies"]}

        Repository Structure:
        {analysis["structure"]}

        README:
        {analysis["readme"]}

        User Question:

        {question}

        Answer the user's question using only the repository information.

        If the repository does not contain enough information,
        say that clearly instead of guessing.
        """
    def build_recommendation_prompt(self, analysis):

        return f"""
    You are an experienced software architect.

    Analyze the following GitHub repository.

    Repository Name:
    {analysis["repository_name"]}

    Languages:
    {analysis["languages"]}

    Dependencies:
    {analysis["dependencies"]}

    Repository Structure:
    {analysis["structure"]}

    Documentation:
    {analysis["documentation"]}

    README:
    {analysis["readme"]}

    IMPORTANT:

    Return ONLY valid JSON.

    Do not return Markdown.
    Do not return explanations.
    Do not wrap the JSON inside ```.

    Return exactly in this format:

    {{
        "strengths": [
            "...",
            "..."
        ],

        "areas_for_improvement": [
            "...",
            "..."
        ],

        "best_practices": [
            "...",
            "..."
        ],

        "overall_quality": "Excellent"
    }}
    """
    def build_improvement_prompt(self, analysis):
        pass