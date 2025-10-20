"""High-level client interface for WCTF Core SDK.

This module provides the WCTFClient class, which is the primary interface
for interacting with company research data.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from wctf_core.operations.company import (
    get_company_facts,
    get_company_flags,
    list_companies as list_companies_op,
)
from wctf_core.operations.research import (
    get_research_prompt as get_research_prompt_op,
    save_research_results as save_research_results_op,
)
from wctf_core.operations.flags import (
    get_flags_extraction_prompt_op,
    save_flags_op,
    add_manual_flag as add_manual_flag_op,
)
from wctf_core.operations.insider import (
    get_insider_extraction_prompt as get_insider_extraction_prompt_op,
    save_insider_facts as save_insider_facts_op,
)
from wctf_core.operations.conversation import (
    get_conversation_questions as get_conversation_questions_op,
)
from wctf_core.operations.decision import (
    gut_check as gut_check_op,
    save_gut_decision as save_gut_decision_op,
    get_evaluation_summary as get_evaluation_summary_op,
)
from wctf_core.utils.paths import get_company_dir


class WCTFClient:
    """High-level client for WCTF company research operations.

    Provides a simple interface for managing company research data,
    including facts, flags, insider interviews, and analysis workflows.

    All methods that interact with the filesystem accept the optional
    data_dir provided during initialization.

    Example:
        >>> from wctf_core import WCTFClient
        >>> client = WCTFClient()
        >>> companies = client.list_companies()
        >>> len(companies) >= 0
        True
        >>> facts = client.get_facts("Stripe")  # doctest: +SKIP
    """

    def __init__(self, data_dir: Optional[Path | str] = None):
        """Initialize a WCTF client.

        Args:
            data_dir: Path to data directory. Defaults to ./data relative to
                     current working directory.

        Example:
            >>> client = WCTFClient()  # Uses ./data
            >>> client.data_dir  # doctest: +SKIP
            PosixPath('...')
            >>> client = WCTFClient("/custom/path")  # doctest: +SKIP
        """
        self.data_dir = Path(data_dir) if data_dir else None

    # Company Discovery Methods

    def list_companies(self) -> List[Dict[str, Any]]:
        """List all companies in the research database.

        Returns a list of companies with metadata about available data files.
        Useful for discovering what companies have been researched and what
        information is available.

        Returns:
            List of dictionaries with company metadata:
            - name (str): Company name
            - has_facts (bool): Whether company.facts.yaml exists
            - has_flags (bool): Whether company.flags.yaml exists

        Example:
            >>> client = WCTFClient()
            >>> companies = client.list_companies()
            >>> isinstance(companies, list)
            True
            >>> all('name' in c for c in companies)
            True

        See Also:
            - get_facts(): Retrieve facts for a specific company
            - company_exists(): Check if a company directory exists
        """
        result = list_companies_op(base_path=self.data_dir)
        return result.get("company_details", [])

    def company_exists(self, company_name: str) -> bool:
        """Check if a company directory exists.

        Args:
            company_name: Name of the company to check

        Returns:
            True if company directory exists, False otherwise

        Example:
            >>> client = WCTFClient()
            >>> client.company_exists("NonExistentCompany123")
            False
        """
        try:
            company_dir = get_company_dir(company_name, base_path=self.data_dir)
            return company_dir.exists()
        except Exception:
            return False

    # Facts Operations

    def get_facts(self, company_name: str) -> Dict[str, Any]:
        """Get research facts for a specific company.

        Returns detailed factual information from company.facts.yaml including
        financial health, market position, organizational stability, and technical culture.

        Args:
            company_name: Name of the company (e.g., 'Stripe', 'Anthropic')

        Returns:
            Dictionary with:
            - success (bool): Whether retrieval was successful
            - facts (dict): Facts data if successful
            - error (str): Error message if unsuccessful

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_facts("Stripe")  # doctest: +SKIP
            >>> result['success']  # doctest: +SKIP
            True
        """
        return get_company_facts(company_name=company_name, base_path=self.data_dir)

    def save_facts(self, company_name: str, yaml_content: str) -> Dict[str, Any]:
        """Save research facts for a company.

        Takes YAML content (as a string) and saves it to the appropriate
        company directory. Merges with existing facts if file already exists.

        Args:
            company_name: Name of the company
            yaml_content: Complete YAML content as a string

        Returns:
            Dictionary with:
            - success (bool): Whether save was successful
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Number of facts saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available)

        Example:
            >>> client = WCTFClient()
            >>> yaml_data = '''
            ... company: "TestCo"
            ... research_date: "2025-01-15"
            ... financial_health:
            ...   facts_found: []
            ...   missing_information: []
            ... market_position:
            ...   facts_found: []
            ...   missing_information: []
            ... organizational_stability:
            ...   facts_found: []
            ...   missing_information: []
            ... technical_culture:
            ...   facts_found: []
            ...   missing_information: []
            ... summary:
            ...   total_facts_found: 0
            ...   information_completeness: "low"
            ... '''  # doctest: +SKIP
            >>> result = client.save_facts("TestCo", yaml_data)  # doctest: +SKIP
        """
        return save_research_results_op(
            company_name=company_name,
            yaml_content=yaml_content,
            base_path=self.data_dir
        )

    # Flags Operations

    def get_flags(self, company_name: str) -> Dict[str, Any]:
        """Get evaluation flags for a specific company.

        Returns evaluation data from company.flags.yaml including
        green flags, red flags, missing critical data, and synthesis.

        Args:
            company_name: Name of the company (e.g., 'Stripe', 'Anthropic')

        Returns:
            Dictionary with:
            - success (bool): Whether retrieval was successful
            - flags (dict): Flags data if successful
            - error (str): Error message if unsuccessful

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_flags("Stripe")  # doctest: +SKIP
        """
        return get_company_flags(company_name=company_name, base_path=self.data_dir)

    def get_flags_extraction_prompt(self) -> Dict[str, Any]:
        """Get prompt for extracting evaluation flags from research.

        Returns a prompt for analyzing research facts and extracting green flags,
        red flags, and missing critical data. The prompt expects research facts
        to be provided in the conversation context.

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available) and extraction_prompt

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_flags_extraction_prompt()
            >>> result['success']
            True
            >>> 'extraction_prompt' in result
            True
        """
        return get_flags_extraction_prompt_op(base_path=self.data_dir)

    def save_flags(
        self,
        company_name: str,
        flags_yaml: str
    ) -> Dict[str, Any]:
        """Save extracted evaluation flags.

        Takes YAML content with extracted flags and saves to company.flags.yaml.
        Merges with existing flags if file already exists.

        Args:
            company_name: Name of the company
            flags_yaml: Complete YAML content with extracted flags

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available)

        Example:
            >>> client = WCTFClient()  # doctest: +SKIP
            >>> flags_yaml = '''  # doctest: +SKIP
            ... company: "Stripe"
            ... evaluation_date: "2025-01-15"
            ... green_flags: {...}
            ... '''
            >>> result = client.save_flags("Stripe", flags_yaml)  # doctest: +SKIP
        """
        return save_flags_op(
            company_name=company_name,
            flags_yaml=flags_yaml,
            base_path=self.data_dir
        )

    def add_flag(
        self,
        company_name: str,
        flag_type: str,
        mountain_element: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Manually add a flag to company evaluation.

        Args:
            company_name: Name of the company
            flag_type: Type of flag - "green", "red", or "missing"
            mountain_element: Mountain element category
            **kwargs: Additional flag-specific fields (flag, impact, confidence, etc.)

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available)
        """
        return add_manual_flag_op(
            company_name=company_name,
            flag_type=flag_type,
            mountain_element=mountain_element,
            base_path=self.data_dir,
            **kwargs
        )

    # Research Workflow Methods

    def get_research_prompt(self, company_name: str) -> Dict[str, Any]:
        """Get the research prompt for a company.

        Returns a structured research prompt that can be used with
        web search capabilities to gather company information.

        Args:
            company_name: Name of the company to research

        Returns:
            Dictionary with:
            - success (bool): Whether prompt was generated
            - research_prompt (str): The formatted research prompt
            - instructions (str): Instructions for conducting research

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_research_prompt("Stripe")
            >>> result['success']
            True
            >>> 'research_prompt' in result
            True
        """
        return get_research_prompt_op(company_name=company_name)

    # Insider Interview Methods

    def get_insider_extraction_prompt(
        self,
        company_name: str,
        interview_date: str,
        interviewee_name: str,
        interviewee_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get prompt for extracting facts from insider interview transcript.

        Returns a formatted prompt for analyzing interview transcripts and
        extracting structured facts.

        Args:
            company_name: Name of the company
            interview_date: Date of interview (YYYY-MM-DD)
            interviewee_name: Name of person interviewed
            interviewee_role: Optional role/title

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available) and extraction prompt
        """
        return get_insider_extraction_prompt_op(
            company_name=company_name,
            interview_date=interview_date,
            interviewee_name=interviewee_name,
            interviewee_role=interviewee_role
        )

    def save_insider_facts(
        self,
        company_name: str,
        interview_date: str,
        interviewee_name: str,
        extracted_facts_yaml: str,
        interviewee_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save extracted insider interview facts.

        Takes YAML content with extracted facts and saves to company.insider.yaml.
        Merges with existing insider facts if file already exists.

        Args:
            company_name: Name of the company
            interview_date: Date of interview (YYYY-MM-DD)
            interviewee_name: Name of person interviewed
            extracted_facts_yaml: YAML content with extracted facts
            interviewee_role: Optional role/title

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available)
        """
        return save_insider_facts_op(
            company_name=company_name,
            interview_date=interview_date,
            interviewee_name=interviewee_name,
            extracted_facts_yaml=extracted_facts_yaml,
            interviewee_role=interviewee_role,
            base_path=self.data_dir
        )

    # Conversation & Decision Methods

    def get_conversation_questions(
        self,
        company_name: str,
        stage: str = "opening",
        max_questions: int = 8
    ) -> Dict[str, Any]:
        """Get conversation guidance questions based on existing company data.

        Args:
            company_name: Name of the company
            stage: Conversation stage - "opening", "follow_up", or "deep_dive"
            max_questions: Maximum number of questions to return

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available) and questions list
        """
        return get_conversation_questions_op(
            company_name=company_name,
            stage=stage,
            max_questions=max_questions,
            base_path=self.data_dir
        )

    def gut_check(self, company_name: str) -> Dict[str, Any]:
        """Generate a gut-check summary for decision making.

        Reads facts and flags, then formats an organized summary to help
        with decision making.

        Args:
            company_name: Name of the company

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available) and formatted summary
        """
        return gut_check_op(company_name=company_name, base_path=self.data_dir)

    def save_decision(
        self,
        company_name: str,
        mountain_worth_climbing: str,
        confidence: str,
        reasoning: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save a gut decision to the company's flags file.

        Args:
            company_name: Name of the company
            mountain_worth_climbing: "YES", "NO", or "MAYBE"
            confidence: "HIGH", "MEDIUM", or "LOW"
            reasoning: Optional reasoning text explaining the decision

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available)
        """
        return save_gut_decision_op(
            company_name=company_name,
            mountain_worth_climbing=mountain_worth_climbing,
            confidence=confidence,
            reasoning=reasoning,
            base_path=self.data_dir
        )

    def get_evaluation_summary(self) -> Dict[str, Any]:
        """Generate a summary table of all company evaluations.

        Returns a formatted table showing all companies with their evaluation
        status, decisions, and confidence levels.

        Returns:
            Dictionary with:
            - success (bool): Whether operation completed successfully
            - message (str): Human-readable confirmation
            - company_name (str): Display name (e.g., "Toast, Inc.")
            - company_slug (str): Filesystem slug (e.g., "toast-inc")
            - file_path (str): Absolute path to saved file
            - items_saved (int): Count of items saved
            - operation (str): "created", "updated", or "merged"

            On error:
            - success (bool): False
            - message (str): User-friendly error explanation
            - error (str): Technical error details
            - company_name (str): Display name (if available)
            - company_slug (str): Filesystem slug (if available), company count, and summary table

        Example:
            >>> client = WCTFClient()
            >>> result = client.get_evaluation_summary()
            >>> result['success']
            True
        """
        return get_evaluation_summary_op(base_path=self.data_dir)
