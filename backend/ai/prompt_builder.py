class PromptBuilder:
    """
    Builds prompts for different AI tasks.
    """

    def build_summary_prompt(self, analysis):
        return f"""
        You are an experienced software engineer.

        Analyze the following repository.

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

        Write:

        1. Repository purpose
        2. Technologies used
        3. Project organization
        4. Intended users
        5. Beginner-friendly summary
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

        Analyze this repository and provide recommendations.

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

        Give:

        1. Repository Strengths (3-5 bullet points)
        2. Areas for Improvement (3-5 bullet points)
        3. Best Practices to Follow
        4. Overall Repository Quality (Excellent / Good / Average / Needs Improvement)

        Keep the answer concise and professional.
        """
    def build_improvement_prompt(self, analysis):
        pass