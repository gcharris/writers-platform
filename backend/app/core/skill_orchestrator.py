"""Skill Orchestrator - Central routing system for writing craft skills.

This module provides intelligent routing and orchestration for all writing craft
skills. It determines which provider (Claude Skill, Native Python, etc.) to use
based on user tier, provider health, and skill availability.

Sprint 12 - Task 12-02
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import time
import logging

logger = logging.getLogger(__name__)


class SkillProvider(Enum):
    """Available skill providers."""
    CLAUDE_SKILL = "claude_skill"
    NATIVE_PYTHON = "native_python"
    OPENAI = "openai"
    LOCAL_LLM = "local_llm"
    CUSTOM = "custom"


class SkillStatus(Enum):
    """Skill execution status."""
    SUCCESS = "success"
    ERROR = "error"
    FALLBACK = "fallback"
    UNAVAILABLE = "unavailable"


@dataclass
class SkillRequest:
    """Standardized skill request format.

    Attributes:
        skill_name: Name of the skill to execute
        capability: Type of operation (analyze, enhance, generate, validate)
        input_data: Input data for the skill
        context: Optional context information
        user_id: User making the request
        user_tier: User's subscription tier (standard, premium)
        preferred_provider: User's provider preference
        allow_fallback: Whether to fall back to alternative provider
    """
    skill_name: str
    capability: str
    input_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    user_tier: str = "standard"
    preferred_provider: Optional[SkillProvider] = None
    allow_fallback: bool = True


@dataclass
class SkillResponse:
    """Standardized skill response format.

    Attributes:
        status: Execution status
        provider: Provider that executed the skill
        data: Response data matching skill's output schema
        metadata: Execution metadata (timing, cost, etc.)
        error: Error information if status is ERROR
    """
    status: SkillStatus
    provider: SkillProvider
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "status": self.status.value,
            "provider": self.provider.value,
            "data": self.data,
            "metadata": self.metadata
        }
        if self.error:
            result["error"] = self.error
        return result


class SkillOrchestrator:
    """Central orchestrator for all writing craft skills.

    This class routes skill requests to the best available provider based on:
    - User subscription tier (premium vs standard)
    - Provider health and availability
    - User preferences
    - Cost optimization

    It also handles fallback logic and error recovery.
    """

    def __init__(self, user_tier: str = "standard", knowledge_path: Optional[Path] = None):
        """Initialize skill orchestrator.

        Args:
            user_tier: User subscription tier (standard, premium)
            knowledge_path: Path to reference knowledge directory
        """
        self.user_tier = user_tier
        self.knowledge_path = knowledge_path or Path(__file__).parent.parent / "knowledge"
        self.providers = {}
        self.provider_health = {}
        self.usage_log = []
        self.native_agents = {}
        self.project_skills = {}  # Sprint 14: project_id -> {skill_type -> GeneratedSkill}

        # Initialize providers
        self._init_providers()
        self._register_native_agents()

    def _init_providers(self):
        """Initialize skill providers."""
        # Import providers (lazy loading to avoid circular dependencies)
        try:
            from factory.mcp.claude_skill_bridge import MCPSkillBridge
            self.providers[SkillProvider.CLAUDE_SKILL] = {
                "class": MCPSkillBridge,
                "instance": None,
                "capabilities": ["analyze", "enhance", "generate", "validate"]
            }
        except ImportError:
            logger.warning("Claude Skill Bridge not available")

        # Native Python agents will be registered as they're implemented
        self.provider_health = {
            SkillProvider.CLAUDE_SKILL: True,  # Assume healthy unless proven otherwise
            SkillProvider.NATIVE_PYTHON: False  # Will be enabled as agents are implemented
        }

    def _register_native_agents(self):
        """Register native Python skill implementations."""
        # Scene Analyzer Agent
        from factory.agents.explants.scene_analyzer import SceneAnalyzerAgent

        self.native_agents["scene-analyzer"] = {
            "agent_class": SceneAnalyzerAgent,
            "description": "Analyzes scene quality using Explants craft standards",
            "capability": "analyze",
            "input_schema": {
                "scene_content": "string - The scene text to analyze",
                "mode": "enum[detailed|quick|variant_comparison] - Analysis depth",
                "phase": "enum[phase1|phase2|phase3] - Voice complexity"
            },
            "output_schema": {
                "total_score": "integer - Overall score (0-100)",
                "category_scores": "object - Breakdown by category",
                "quality_tier": "string - Quality tier",
                "fixes": "array[object] - Specific improvement suggestions"
            }
        }

        # Mark native Python provider as available if we have agents
        if self.native_agents:
            self.provider_health[SkillProvider.NATIVE_PYTHON] = True

    async def execute_skill(
        self,
        request: SkillRequest,
        project_id: Optional[str] = None
    ) -> SkillResponse:
        """Execute a skill request with intelligent routing.

        Sprint 14: Now supports project-specific skills. If project_id is provided,
        routes to project-specific skill first, then falls back to global skills.

        Args:
            request: Skill request to execute
            project_id: Optional project ID for project-specific skills

        Returns:
            Skill response with execution results
        """
        start_time = time.time()

        # Sprint 14: Try project-specific skill first if project_id provided
        if project_id and project_id in self.project_skills:
            # Extract skill type from skill_name (e.g., "scene-analyzer" from "scene-analyzer-the-explants")
            skill_type = self._extract_skill_type(request.skill_name)

            if skill_type in self.project_skills[project_id]:
                try:
                    result = await self._execute_project_skill(
                        project_id,
                        skill_type,
                        request
                    )

                    execution_time = (time.time() - start_time) * 1000
                    self._log_execution(request, SkillProvider.CUSTOM, execution_time, success=True)

                    result.metadata.update({
                        "execution_time_ms": execution_time,
                        "project_id": project_id,
                        "skill_type": skill_type
                    })

                    return result
                except Exception as e:
                    logger.warning(f"Project-specific skill failed: {e}. Falling back to global skills.")

        # Fall back to global skills (existing logic)
        # Get provider priority list
        provider_priority = self._get_provider_priority(request)

        # Try providers in priority order
        last_error = None
        for provider in provider_priority:
            try:
                result = await self._call_provider(provider, request)

                # Log successful execution
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                self._log_execution(request, provider, execution_time, success=True)

                # Add execution metadata
                result.metadata.update({
                    "execution_time_ms": execution_time,
                    "attempted_providers": [p.value for p in provider_priority]
                })

                return result
            except Exception as e:
                logger.warning(f"Provider {provider.value} failed: {str(e)}")
                last_error = str(e)

                # Mark provider as unhealthy
                self.provider_health[provider] = False

                # If no fallback allowed, return error immediately
                if not request.allow_fallback:
                    break

        # All providers failed
        execution_time = (time.time() - start_time) * 1000
        self._log_execution(request, None, execution_time, success=False)

        return SkillResponse(
            status=SkillStatus.ERROR,
            provider=provider_priority[0] if provider_priority else SkillProvider.NATIVE_PYTHON,
            data={},
            metadata={
                "execution_time_ms": execution_time,
                "attempted_providers": [p.value for p in provider_priority]
            },
            error={
                "code": "ALL_PROVIDERS_FAILED",
                "message": f"All providers failed. Last error: {last_error}"
            }
        )

    def _get_provider_priority(self, request: SkillRequest) -> List[SkillProvider]:
        """Determine provider priority order.

        Args:
            request: Skill request

        Returns:
            List of providers in priority order
        """
        # If user specified a provider, try that first
        if request.preferred_provider:
            priority = [request.preferred_provider]

            # Add fallbacks if allowed
            if request.allow_fallback:
                priority.extend([
                    p for p in SkillProvider
                    if p != request.preferred_provider and self.provider_health.get(p, False)
                ])

            return priority

        # Premium users: Try Claude Skill first, fall back to Native Python
        if request.user_tier == "premium":
            priority = []

            if self.provider_health.get(SkillProvider.CLAUDE_SKILL, False):
                priority.append(SkillProvider.CLAUDE_SKILL)

            if self.provider_health.get(SkillProvider.NATIVE_PYTHON, False):
                priority.append(SkillProvider.NATIVE_PYTHON)

            return priority

        # Standard users: Try Native Python first, fall back to Claude Skill if available
        priority = []

        if self.provider_health.get(SkillProvider.NATIVE_PYTHON, False):
            priority.append(SkillProvider.NATIVE_PYTHON)

        if self.provider_health.get(SkillProvider.CLAUDE_SKILL, False):
            priority.append(SkillProvider.CLAUDE_SKILL)

        return priority

    async def _call_provider(
        self,
        provider: SkillProvider,
        request: SkillRequest
    ) -> SkillResponse:
        """Route request to specific provider.

        Args:
            provider: Provider to use
            request: Skill request

        Returns:
            Skill response

        Raises:
            Exception if provider fails
        """
        if provider == SkillProvider.CLAUDE_SKILL:
            return await self._call_claude_skill(request)
        elif provider == SkillProvider.NATIVE_PYTHON:
            return await self._call_native_python(request)
        else:
            raise NotImplementedError(f"Provider {provider.value} not yet implemented")

    async def _call_claude_skill(self, request: SkillRequest) -> SkillResponse:
        """Call Claude Skill via MCP Bridge.

        Args:
            request: Skill request

        Returns:
            Skill response
        """
        # Get or create bridge instance
        if not self.providers[SkillProvider.CLAUDE_SKILL]["instance"]:
            BridgeClass = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
            self.providers[SkillProvider.CLAUDE_SKILL]["instance"] = BridgeClass(
                user_tier=request.user_tier
            )

        bridge = self.providers[SkillProvider.CLAUDE_SKILL]["instance"]

        # Call the skill
        result = await bridge.call_skill(
            skill_id=request.skill_name,
            input_data=request.input_data,
            context=request.context
        )

        # Convert to SkillResponse
        if result["status"] == "success":
            status = SkillStatus.SUCCESS
        elif result["status"] == "fallback":
            status = SkillStatus.FALLBACK
        else:
            status = SkillStatus.ERROR

        return SkillResponse(
            status=status,
            provider=SkillProvider.CLAUDE_SKILL,
            data=result.get("data", {}),
            metadata=result.get("metadata", {}),
            error=result.get("error")
        )

    async def _call_native_python(self, request: SkillRequest) -> SkillResponse:
        """Call Native Python agent.

        Args:
            request: Skill request

        Returns:
            Skill response

        Raises:
            NotImplementedError if agent not yet implemented
        """
        # TODO: Implement native Python agent routing
        # For now, this is a placeholder that will be implemented in Task 12-03
        raise NotImplementedError("Native Python agents not yet implemented")

    def list_available_skills(self, user_tier: str = "standard") -> List[Dict[str, Any]]:
        """List all skills available to a user.

        Args:
            user_tier: User's subscription tier

        Returns:
            List of available skills with metadata
        """
        available_skills = []

        # Get skills from Claude Skill Bridge
        if self.provider_health.get(SkillProvider.CLAUDE_SKILL, False):
            if not self.providers[SkillProvider.CLAUDE_SKILL]["instance"]:
                BridgeClass = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
                self.providers[SkillProvider.CLAUDE_SKILL]["instance"] = BridgeClass(
                    user_tier=user_tier
                )

            bridge = self.providers[SkillProvider.CLAUDE_SKILL]["instance"]
            available_skills.extend(bridge.list_skills())

        # TODO: Add native Python agents as they're implemented

        return available_skills

    def get_skill_info(self, skill_name: str, user_tier: str = "standard") -> Optional[Dict[str, Any]]:
        """Get detailed information about a skill.

        Args:
            skill_name: Skill identifier
            user_tier: User's subscription tier

        Returns:
            Skill metadata or None if not found
        """
        # Check Claude Skill Bridge
        if self.provider_health.get(SkillProvider.CLAUDE_SKILL, False):
            if not self.providers[SkillProvider.CLAUDE_SKILL]["instance"]:
                BridgeClass = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
                self.providers[SkillProvider.CLAUDE_SKILL]["instance"] = BridgeClass(
                    user_tier=user_tier
                )

            bridge = self.providers[SkillProvider.CLAUDE_SKILL]["instance"]
            info = bridge.get_skill_info(skill_name)
            if info:
                return info

        # TODO: Check native Python agents

        return None

    def health_check(self) -> Dict[str, Any]:
        """Check health of all providers.

        Returns:
            Health status for each provider
        """
        health_status = {}

        for provider, is_healthy in self.provider_health.items():
            health_status[provider.value] = {
                "healthy": is_healthy,
                "available": provider in self.providers
            }

        return health_status

    def _log_execution(
        self,
        request: SkillRequest,
        provider: Optional[SkillProvider],
        execution_time_ms: float,
        success: bool
    ):
        """Log skill execution for analytics.

        Args:
            request: Skill request
            provider: Provider used (or None if all failed)
            execution_time_ms: Execution time in milliseconds
            success: Whether execution was successful
        """
        log_entry = {
            "timestamp": time.time(),
            "skill_name": request.skill_name,
            "capability": request.capability,
            "user_id": request.user_id,
            "user_tier": request.user_tier,
            "provider": provider.value if provider else None,
            "execution_time_ms": execution_time_ms,
            "success": success
        }

        self.usage_log.append(log_entry)

        # Keep only last 1000 entries
        if len(self.usage_log) > 1000:
            self.usage_log = self.usage_log[-1000:]

    def list_available_skills(self) -> List[Dict[str, Any]]:
        """List all available skills for current user.

        Returns:
            List of skill definitions with availability info
        """
        skills = []

        # Add native Python skills
        for skill_id, agent_info in self.native_agents.items():
            skills.append({
                "name": f"native-{skill_id}",
                "skill_id": skill_id,
                "capability": agent_info["capability"],
                "description": agent_info["description"],
                "available": True,
                "providers": ["native_python"],
                "cost_tier": "free"
            })

        # Add Claude Skills if available
        if SkillProvider.CLAUDE_SKILL in self.providers:
            try:
                bridge_class = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
                bridge = bridge_class(user_tier=self.user_tier)
                claude_skills = bridge.list_skills()
                for skill in claude_skills:
                    # Check if we already have native version
                    if skill["skill_id"] not in [s["skill_id"] for s in skills]:
                        skill["available"] = True
                        skill["providers"] = ["claude_skill"]
                        skills.append(skill)
                    else:
                        # Add claude_skill as additional provider
                        for existing in skills:
                            if existing["skill_id"] == skill["skill_id"]:
                                existing["providers"].append("claude_skill")
            except Exception as e:
                logger.warning(f"Failed to list Claude Skills: {e}")

        return skills

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific skill.

        Args:
            skill_name: Skill identifier

        Returns:
            Skill definition with details, or None if not found
        """
        # Check native agents
        if skill_name in self.native_agents:
            agent_info = self.native_agents[skill_name]
            return {
                "name": f"native-{skill_name}",
                "skill_id": skill_name,
                "capability": agent_info["capability"],
                "description": agent_info["description"],
                "available": True,
                "providers": ["native_python"],
                "cost_tier": "free",
                "input_schema": agent_info["input_schema"],
                "output_schema": agent_info["output_schema"],
                "examples": []
            }

        # Check Claude Skills
        if SkillProvider.CLAUDE_SKILL in self.providers:
            try:
                bridge_class = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
                bridge = bridge_class(user_tier=self.user_tier)
                skill_info = bridge.get_skill_info(skill_name)
                if skill_info:
                    return skill_info
            except Exception as e:
                logger.warning(f"Failed to get Claude Skill info: {e}")

        return None

    async def check_provider_health(self) -> Dict[str, Any]:
        """Check health status of all skill providers.

        Returns:
            Provider health status and overall health
        """
        health = {
            "providers": {},
            "overall_status": "healthy"
        }

        unhealthy_count = 0
        total_count = 0

        # Check Native Python
        total_count += 1
        if self.native_agents:
            health["providers"]["native_python"] = {
                "available": True,
                "latency_ms": 0
            }
        else:
            health["providers"]["native_python"] = {
                "available": False,
                "error": "No native agents registered"
            }
            unhealthy_count += 1

        # Check Claude Skill
        total_count += 1
        if SkillProvider.CLAUDE_SKILL in self.providers:
            try:
                # Test call to check availability
                bridge_class = self.providers[SkillProvider.CLAUDE_SKILL]["class"]
                bridge = bridge_class(user_tier=self.user_tier)
                start = time.time()
                bridge.list_skills()  # Quick test call
                latency = (time.time() - start) * 1000
                health["providers"]["claude_skill"] = {
                    "available": True,
                    "latency_ms": int(latency)
                }
            except Exception as e:
                health["providers"]["claude_skill"] = {
                    "available": False,
                    "error": str(e)
                }
                unhealthy_count += 1
        else:
            health["providers"]["claude_skill"] = {
                "available": False,
                "error": "Not configured"
            }
            unhealthy_count += 1

        # Determine overall status
        if unhealthy_count == 0:
            health["overall_status"] = "healthy"
        elif unhealthy_count == total_count:
            health["overall_status"] = "unhealthy"
        else:
            health["overall_status"] = "degraded"

        return health

    # ===== Sprint 14: Project-Specific Skill Support =====

    def register_project_skills(
        self,
        project_id: str,
        skills: Dict[str, Any]
    ):
        """
        Register project-specific skills.

        Sprint 14: Adds support for project-specific skills generated during setup.

        Args:
            project_id: Project identifier (e.g., "the-explants")
            skills: Dictionary of skill_type -> GeneratedSkill
        """

        if project_id not in self.project_skills:
            self.project_skills[project_id] = {}

        for skill_type, skill in skills.items():
            self.project_skills[project_id][skill_type] = skill

        logger.info(f"Registered {len(skills)} skills for project: {project_id}")

    async def _execute_project_skill(
        self,
        project_id: str,
        skill_type: str,
        request: SkillRequest
    ) -> SkillResponse:
        """
        Execute project-specific skill.

        Sprint 14: Calls project-specific Claude Code skill stored in project directory.

        Args:
            project_id: Project identifier
            skill_type: Skill type (e.g., "scene-analyzer")
            request: Skill request

        Returns:
            Skill response

        Raises:
            Exception if skill execution fails
        """
        import subprocess
        import json

        skill = self.project_skills[project_id][skill_type]

        # Use Claude Code to execute the skill
        # Skills are Claude Code skills stored in project .claude/skills/
        logger.info(f"Executing project skill: {skill.skill_name}")

        try:
            result = subprocess.run(
                ["claude", "skill", skill.skill_name, json.dumps(request.input_data)],
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout
            )

            if result.returncode != 0:
                raise Exception(f"Skill execution failed: {result.stderr}")

            output = json.loads(result.stdout)

            return SkillResponse(
                status=SkillStatus.SUCCESS,
                provider=SkillProvider.CUSTOM,
                data=output,
                metadata={
                    "project_id": project_id,
                    "skill_type": skill_type,
                    "skill_name": skill.skill_name
                }
            )

        except subprocess.TimeoutExpired:
            raise Exception(f"Skill execution timed out after 60 seconds")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse skill output: {e}")
        except Exception as e:
            raise Exception(f"Skill execution error: {e}")

    def _extract_skill_type(self, skill_name: str) -> str:
        """
        Extract skill type from full skill name.

        Examples:
            "scene-analyzer-the-explants" -> "scene-analyzer"
            "scene-enhancer-witty-hearts" -> "scene-enhancer"
            "scene-analyzer" -> "scene-analyzer"

        Args:
            skill_name: Full skill name

        Returns:
            Skill type
        """
        # Known skill types
        known_types = [
            "scene-analyzer",
            "scene-enhancer",
            "character-validator",
            "scene-writer",
            "scene-multiplier",
            "scaffold-generator"
        ]

        # Try to match known types
        for skill_type in known_types:
            if skill_name.startswith(skill_type):
                return skill_type

        # If no match, return the whole name
        return skill_name

    def list_project_skills(self, project_id: str) -> List[Dict[str, Any]]:
        """
        List all skills for a project.

        Sprint 14: Returns project-specific skills.

        Args:
            project_id: Project identifier

        Returns:
            List of skill metadata dictionaries
        """

        if project_id not in self.project_skills:
            return []

        skills = []
        for skill_type, skill in self.project_skills[project_id].items():
            skills.append({
                "skill_name": skill.skill_name,
                "skill_type": skill_type,
                "voice_profile": skill.voice_profile.voice_name,
                "genre": skill.voice_profile.genre,
                "project_id": project_id
            })

        return skills

    def get_project_skill_info(
        self,
        project_id: str,
        skill_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a project skill.

        Sprint 14: Returns detailed skill metadata.

        Args:
            project_id: Project identifier
            skill_type: Skill type (e.g., "scene-analyzer")

        Returns:
            Skill metadata or None if not found
        """

        if project_id not in self.project_skills:
            return None

        if skill_type not in self.project_skills[project_id]:
            return None

        skill = self.project_skills[project_id][skill_type]

        return {
            "skill_name": skill.skill_name,
            "skill_type": skill_type,
            "voice_profile": {
                "name": skill.voice_profile.voice_name,
                "genre": skill.voice_profile.genre,
                "characteristics": skill.voice_profile.primary_characteristics
            },
            "project_id": project_id,
            "references": list(skill.references.keys()),
            "available": True
        }

    def list_all_projects(self) -> List[str]:
        """
        List all projects with registered skills.

        Sprint 14: Returns project IDs.

        Returns:
            List of project IDs
        """
        return list(self.project_skills.keys())
