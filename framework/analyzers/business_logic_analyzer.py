"""
Business Logic Analyzer

Extracts business logic, rules, and user flows from source code:
- User authentication flows
- Business rules and validations
- Data models and relationships
- State machines and workflows
- Error handling logic
- iOS Swift/SwiftUI support
- Deep AST analysis
- Negative test case generation
- Edge case detection
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import re


class BusinessRuleType(Enum):
    """Types of business rules"""

    VALIDATION = "validation"
    AUTHORIZATION = "authorization"
    STATE_TRANSITION = "state_transition"
    CALCULATION = "calculation"
    ERROR_HANDLING = "error_handling"


@dataclass
class BusinessRule:
    """Represents a business rule extracted from code"""

    type: BusinessRuleType
    description: str
    condition: str
    source_file: str
    line_number: Optional[int] = None
    related_entities: List[str] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)


@dataclass
class UserFlow:
    """Represents a user flow/journey"""

    name: str
    description: str
    steps: List[str]
    entry_point: str
    success_outcome: str
    failure_outcomes: List[str] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)


@dataclass
class DataModel:
    """Represents a data model/entity"""

    name: str
    fields: Dict[str, str]  # field_name -> field_type
    validations: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    source_file: Optional[str] = None


@dataclass
class EdgeCase:
    """Represents an edge case detected in code"""

    type: str  # boundary, null, empty, overflow, etc.
    description: str
    test_data: List[Any] = field(default_factory=list)
    source_file: Optional[str] = None
    severity: str = "medium"  # low, medium, high, critical


@dataclass
class StateMachine:
    """Represents a state machine extracted from code"""

    name: str
    states: List[str]
    transitions: Dict[str, List[str]]  # from_state -> [to_states]
    initial_state: str
    final_states: List[str] = field(default_factory=list)
    source_file: Optional[str] = None


@dataclass
class APIContract:
    """Represents an API contract/specification"""

    endpoint: str
    method: str  # GET, POST, PUT, DELETE, etc.
    request_schema: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)
    error_responses: List[Dict[str, Any]] = field(default_factory=list)
    authentication: Optional[str] = None
    rate_limit: Optional[str] = None
    description: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class BusinessLogicAnalysis:
    """Complete business logic analysis result"""

    user_flows: List[UserFlow] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    data_models: List[DataModel] = field(default_factory=list)
    state_machines: List[StateMachine] = field(default_factory=list)
    edge_cases: List[EdgeCase] = field(default_factory=list)
    api_contracts: List[APIContract] = field(default_factory=list)
    mock_data: Dict[str, Any] = field(default_factory=dict)
    negative_test_cases: List[Dict[str, Any]] = field(default_factory=list)
    platform: str = "android"  # android or ios


class BusinessLogicAnalyzer:
    """Analyzes source code to extract business logic"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.analysis = BusinessLogicAnalysis()
        self.platform = self._detect_platform()

    def _detect_platform(self) -> str:
        """Detect if project is Android or iOS"""
        if list(self.project_path.rglob("*.swift")):
            return "ios"
        elif list(self.project_path.rglob("*.kt")) or list(self.project_path.rglob("*.java")):
            return "android"
        else:
            return "unknown"

    def analyze(self) -> BusinessLogicAnalysis:
        """
        Perform complete business logic analysis

        Returns:
            BusinessLogicAnalysis with extracted information
        """
        if self.platform == "android":
            self._analyze_android()
        elif self.platform == "ios":
            self._analyze_ios()
        else:
            # Try both
            self._analyze_android()
            self._analyze_ios()

        # Extract state machines
        self._extract_state_machines()

        # Detect edge cases
        self._detect_edge_cases()

        # Generate negative test cases
        self._generate_negative_test_cases()

        # Generate API contracts
        self._generate_api_contracts()

        # Set platform in analysis
        self.analysis.platform = self.platform

        return self.analysis

    def _analyze_android(self) -> None:
        """Analyze Android (Kotlin/Java) project"""
        # Analyze Kotlin/Java files
        kotlin_files = list(self.project_path.rglob("*.kt"))
        java_files = list(self.project_path.rglob("*.java"))

        for file_path in kotlin_files + java_files:
            self._analyze_file(file_path)

        # Analyze ViewModels for flows
        self._analyze_viewmodels()

        # Analyze Repositories for data access patterns
        self._analyze_repositories()

        # Analyze data models
        self._analyze_models()

        # Analyze mock data for business scenarios
        self._analyze_mock_data()

    def _analyze_ios(self) -> None:
        """Analyze iOS (Swift/SwiftUI) project"""
        swift_files = list(self.project_path.rglob("*.swift"))

        for file_path in swift_files:
            self._analyze_swift_file(file_path)

        # Analyze SwiftUI Views for user flows
        self._analyze_swiftui_views()

        # Analyze ViewModels/ObservableObjects
        self._analyze_swift_viewmodels()

        # Analyze Swift models
        self._analyze_swift_models()

        # Analyze mock data
        self._analyze_swift_mock_data()

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single source file"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract business rules from comments
            self._extract_business_rules_from_comments(content, str(file_path))

            # Extract validation rules
            self._extract_validations(content, str(file_path))

            # Extract error handling
            self._extract_error_handling(content, str(file_path))

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _analyze_viewmodels(self) -> None:
        """Analyze ViewModels to extract user flows"""
        viewmodel_files = list(self.project_path.rglob("*ViewModel.kt"))

        for vm_file in viewmodel_files:
            try:
                content = vm_file.read_text(encoding="utf-8")

                # Extract flow name from class name
                class_match = re.search(r"class\s+(\w+)ViewModel", content)
                if not class_match:
                    continue

                flow_name = class_match.group(1)

                # Extract public methods (user actions)
                methods = re.findall(r"fun\s+(\w+)\([^)]*\)\s*\{", content)

                # Create user flow
                flow = UserFlow(
                    name=flow_name,
                    description=f"User flow for {flow_name}",
                    steps=[f"User {method}" for method in methods],
                    entry_point=f"{flow_name}Screen",
                    success_outcome="Navigate to next screen",
                    source_files=[str(vm_file)],
                )

                self.analysis.user_flows.append(flow)

            except Exception as e:
                print(f"Warning: Could not analyze ViewModel {vm_file}: {e}")

    def _analyze_repositories(self) -> None:
        """Analyze repositories for data access patterns"""
        repo_files = list(self.project_path.rglob("*Repository.kt"))

        for repo_file in repo_files:
            try:
                content = repo_file.read_text(encoding="utf-8")

                # Extract interface methods
                interface_methods = re.findall(r"suspend\s+fun\s+(\w+)\([^)]*\):\s*(\w+)", content)

                for method_name, return_type in interface_methods:
                    # Create business rule for data access
                    rule = BusinessRule(
                        type=BusinessRuleType.AUTHORIZATION,
                        description=f"Data access: {method_name} returns {return_type}",
                        condition="User must be authenticated",
                        source_file=str(repo_file),
                        related_entities=[return_type],
                    )
                    self.analysis.business_rules.append(rule)

            except Exception as e:
                print(f"Warning: Could not analyze Repository {repo_file}: {e}")

    def _analyze_models(self) -> None:
        """Analyze data models"""
        model_files = list(self.project_path.rglob("models/*.kt"))

        for model_file in model_files:
            try:
                content = model_file.read_text(encoding="utf-8")

                # Extract data class
                class_match = re.search(r"data\s+class\s+(\w+)\s*\((.*?)\)", content, re.DOTALL)

                if not class_match:
                    continue

                class_name = class_match.group(1)
                params = class_match.group(2)

                # Parse fields
                fields = {}
                for field_match in re.finditer(r"val\s+(\w+):\s+([^,\n]+)", params):
                    field_name = field_match.group(1)
                    field_type = field_match.group(2).strip()
                    fields[field_name] = field_type

                model = DataModel(name=class_name, fields=fields, source_file=str(model_file))

                self.analysis.data_models.append(model)

            except Exception as e:
                print(f"Warning: Could not analyze model {model_file}: {e}")

    def _analyze_mock_data(self) -> None:
        """Analyze mock data to understand business scenarios"""
        mock_files = list(self.project_path.rglob("mock/*.kt"))

        for mock_file in mock_files:
            try:
                content = mock_file.read_text(encoding="utf-8")

                # Extract lazy property with mock data
                lazy_match = re.search(
                    r"val\s+MockData\.(\w+).*?by\s+lazy\s*\{(.*?)\}",
                    content,
                    re.DOTALL,
                )

                if lazy_match:
                    entity_name = lazy_match.group(1)
                    lazy_body = lazy_match.group(2)

                    # Extract range for test data count
                    range_match = re.search(r"\((\d+)L?\.\.(\d+)L?\)", lazy_body)
                    if range_match:
                        start, end = range_match.groups()
                        self.analysis.mock_data[entity_name] = {
                            "count": int(end) - int(start) + 1,
                            "start_id": int(start),
                            "end_id": int(end),
                            "source": str(mock_file),
                        }

            except Exception as e:
                print(f"Warning: Could not analyze mock data {mock_file}: {e}")

    def _extract_business_rules_from_comments(self, content: str, file_path: str) -> None:
        """Extract business rules from TODO and comments"""
        # Find TODO comments
        todos = re.findall(r"//\s*TODO:?\s*(.+)", content)
        for todo in todos:
            if any(
                keyword in todo.lower()
                for keyword in [
                    "validate",
                    "check",
                    "auth",
                    "permission",
                    "rule",
                ]
            ):
                rule = BusinessRule(
                    type=BusinessRuleType.VALIDATION,
                    description=todo.strip(),
                    condition="Not yet implemented",
                    source_file=file_path,
                )
                self.analysis.business_rules.append(rule)

    def _extract_validations(self, content: str, file_path: str) -> None:
        """Extract validation logic"""
        # Find require() statements
        requires = re.findall(r'require\((.*?)\)\s*\{?\s*["\'](.+?)["\']', content)
        for condition, message in requires:
            rule = BusinessRule(
                type=BusinessRuleType.VALIDATION,
                description=f"Validation: {condition}",
                condition=condition.strip(),
                source_file=file_path,
                error_messages=[message],
            )
            self.analysis.business_rules.append(rule)

    def _extract_error_handling(self, content: str, file_path: str) -> None:
        """Extract error handling logic"""
        # Find catch blocks
        catches = re.findall(r"catch\s*\(\s*\w+:\s*(\w+)\s*\)\s*\{([^}]+)\}", content)
        for exception_type, _ in catches:
            rule = BusinessRule(
                type=BusinessRuleType.ERROR_HANDLING,
                description=f"Handle {exception_type}",
                condition=f"When {exception_type} occurs",
                source_file=file_path,
            )
            self.analysis.business_rules.append(rule)

    def generate_test_scenarios(self) -> List[Dict]:
        """
        Generate test scenarios from business logic

        Returns:
            List of test scenario dictionaries
        """
        scenarios = []

        for flow in self.analysis.user_flows:
            # Happy path scenario
            scenarios.append(
                {
                    "name": f"{flow.name} - Happy Path",
                    "type": "positive",
                    "description": flow.description,
                    "steps": flow.steps,
                    "expected_outcome": flow.success_outcome,
                    "priority": "high",
                }
            )

            # Failure scenarios
            for failure in flow.failure_outcomes:
                scenarios.append(
                    {
                        "name": f"{flow.name} - {failure}",
                        "type": "negative",
                        "description": f"Test {failure} scenario",
                        "steps": flow.steps[:-1],  # All steps except last
                        "expected_outcome": failure,
                        "priority": "medium",
                    }
                )

        return scenarios

    def generate_bdd_features(self) -> str:
        """
        Generate BDD feature file from business logic

        Returns:
            Gherkin feature file content
        """
        feature_content = []

        for flow in self.analysis.user_flows:
            feature_content.append(f"Feature: {flow.name}")
            feature_content.append(f"  {flow.description}")
            feature_content.append("")

            # Generate scenario from flow
            feature_content.append(f"  Scenario: {flow.name} - Success")
            feature_content.append(f"    Given I am on the {flow.entry_point}")

            for step in flow.steps:
                feature_content.append(f"    When {step}")

            feature_content.append(f"    Then {flow.success_outcome}")
            feature_content.append("")

        return "\n".join(feature_content)

    def get_mock_test_data(self) -> Dict:
        """
        Get mock test data for testing

        Returns:
            Dictionary with test data
        """
        return self.analysis.mock_data

    def export_to_json(self) -> Dict:
        """Export analysis to JSON-serializable dict"""
        return {
            "platform": self.platform,
            "user_flows": [
                {
                    "name": flow.name,
                    "description": flow.description,
                    "steps": flow.steps,
                    "entry_point": flow.entry_point,
                    "success_outcome": flow.success_outcome,
                    "failure_outcomes": flow.failure_outcomes,
                    "source_files": flow.source_files,
                }
                for flow in self.analysis.user_flows
            ],
            "business_rules": [
                {
                    "type": rule.type.value,
                    "description": rule.description,
                    "condition": rule.condition,
                    "source_file": rule.source_file,
                    "related_entities": rule.related_entities,
                    "error_messages": rule.error_messages,
                }
                for rule in self.analysis.business_rules
            ],
            "data_models": [
                {
                    "name": model.name,
                    "fields": model.fields,
                    "validations": model.validations,
                    "source_file": model.source_file,
                }
                for model in self.analysis.data_models
            ],
            "state_machines": [
                {
                    "name": sm.name,
                    "states": sm.states,
                    "transitions": sm.transitions,
                    "initial_state": sm.initial_state,
                    "final_states": sm.final_states,
                    "source_file": sm.source_file,
                }
                for sm in self.analysis.state_machines
            ],
            "edge_cases": [
                {
                    "type": ec.type,
                    "description": ec.description,
                    "test_data": ec.test_data,
                    "source_file": ec.source_file,
                    "severity": ec.severity,
                }
                for ec in self.analysis.edge_cases
            ],
            "api_contracts": [
                {
                    "endpoint": contract.endpoint,
                    "method": contract.method,
                    "request_schema": contract.request_schema,
                    "response_schema": contract.response_schema,
                    "error_responses": contract.error_responses,
                    "authentication": contract.authentication,
                    "rate_limit": contract.rate_limit,
                    "description": contract.description,
                    "source_file": contract.source_file,
                }
                for contract in self.analysis.api_contracts
            ],
            "negative_test_cases": self.analysis.negative_test_cases,
            "mock_data": self.analysis.mock_data,
        }

    # ===== iOS Swift/SwiftUI Analysis =====

    def _analyze_swift_file(self, file_path: Path) -> None:
        """Analyze a Swift source file"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Extract business rules from comments
            self._extract_business_rules_from_comments(content, str(file_path))

            # Extract validations (Swift guard statements)
            self._extract_swift_validations(content, str(file_path))

            # Extract error handling
            self._extract_swift_error_handling(content, str(file_path))

        except Exception as e:
            print(f"Warning: Could not analyze Swift file {file_path}: {e}")

    def _analyze_swiftui_views(self) -> None:
        """Analyze SwiftUI Views for user flows"""
        view_files = [f for f in self.project_path.rglob("*.swift") if "View" in f.stem and "ViewModel" not in f.stem]

        for view_file in view_files:
            try:
                content = view_file.read_text(encoding="utf-8")

                # Extract view name
                view_match = re.search(r"struct\s+(\w+):\s*View", content)
                if not view_match:
                    continue

                view_name = view_match.group(1)

                # Extract Button actions
                buttons = re.findall(
                    r'Button\(["\']([^"\']+)["\'].*?\{(.*?)\}',
                    content,
                    re.DOTALL,
                )

                # Extract NavigationLink destinations
                nav_links = re.findall(r"NavigationLink\(.*?destination:\s*(\w+)", content)

                # Create user flow
                if buttons or nav_links:
                    steps = [f"Tap {btn[0]}" for btn in buttons]
                    steps.extend([f"Navigate to {dest}" for dest in nav_links])

                    flow = UserFlow(
                        name=view_name.replace("View", ""),
                        description=f"User flow for {view_name}",
                        steps=steps,
                        entry_point=view_name,
                        success_outcome="Complete interaction",
                        source_files=[str(view_file)],
                    )

                    self.analysis.user_flows.append(flow)

            except Exception as e:
                print(f"Warning: Could not analyze SwiftUI View {view_file}: {e}")

    def _analyze_swift_viewmodels(self) -> None:
        """Analyze Swift ViewModels/ObservableObjects"""
        vm_files = list(self.project_path.rglob("*ViewModel.swift"))

        for vm_file in vm_files:
            try:
                content = vm_file.read_text(encoding="utf-8")

                # Extract class name
                class_match = re.search(r"class\s+(\w+ViewModel):\s*ObservableObject", content)
                if not class_match:
                    continue

                class_name = class_match.group(1)

                # Extract public methods
                methods = re.findall(r"func\s+(\w+)\([^)]*\)\s*(?:->.*?)?\{", content)

                # Create user flow
                flow = UserFlow(
                    name=class_name.replace("ViewModel", ""),
                    description=f"User flow for {class_name}",
                    steps=[f"User {method}" for method in methods],
                    entry_point=f"{class_name}Screen",
                    success_outcome="State updated",
                    source_files=[str(vm_file)],
                )

                self.analysis.user_flows.append(flow)

            except Exception as e:
                print(f"Warning: Could not analyze Swift ViewModel {vm_file}: {e}")

    def _analyze_swift_models(self) -> None:
        """Analyze Swift data models"""
        model_files = [f for f in self.project_path.rglob("*.swift") if "Model" in f.stem or f.parent.name == "Models"]

        for model_file in model_files:
            try:
                content = model_file.read_text(encoding="utf-8")

                # Extract struct/class definitions
                for match in re.finditer(
                    r"(?:struct|class)\s+(\w+):\s*(?:Codable|Identifiable|Hashable)(?:.*?)\{(.*?)\n\}",
                    content,
                    re.DOTALL,
                ):
                    model_name = match.group(1)
                    body = match.group(2)

                    # Parse properties
                    fields = {}
                    for prop_match in re.finditer(r"(?:var|let)\s+(\w+):\s+([^\n=]+)", body):
                        prop_name = prop_match.group(1)
                        prop_type = prop_match.group(2).strip()
                        fields[prop_name] = prop_type

                    if fields:
                        model = DataModel(
                            name=model_name,
                            fields=fields,
                            source_file=str(model_file),
                        )
                        self.analysis.data_models.append(model)

            except Exception as e:
                print(f"Warning: Could not analyze Swift model {model_file}: {e}")

    def _analyze_swift_mock_data(self) -> None:
        """Analyze Swift mock data"""
        mock_files = [f for f in self.project_path.rglob("*.swift") if "Mock" in f.stem or "Preview" in f.stem]

        for mock_file in mock_files:
            try:
                content = mock_file.read_text(encoding="utf-8")

                # Extract static mock arrays
                for match in re.finditer(
                    r"static\s+(?:let|var)\s+(\w+):\s*\[(\w+)\]\s*=\s*\[(.*?)\]",
                    content,
                    re.DOTALL,
                ):
                    entity_name = match.group(1)
                    entity_type = match.group(2)
                    array_content = match.group(3)

                    # Count items
                    items = [item.strip() for item in array_content.split(f"{entity_type}(") if item.strip()]
                    count = len(items)

                    if count > 0:
                        self.analysis.mock_data[entity_name] = {
                            "count": count,
                            "type": entity_type,
                            "source": str(mock_file),
                        }

            except Exception as e:
                print(f"Warning: Could not analyze Swift mock data {mock_file}: {e}")

    def _extract_swift_validations(self, content: str, file_path: str) -> None:
        """Extract Swift validation logic (guard statements)"""
        # Find guard statements
        guards = re.findall(r"guard\s+(.*?)\s+else\s*\{([^}]*)\}", content, re.DOTALL)

        for condition, else_body in guards:
            # Extract error message if present
            error_msg_match = re.search(r'["\'](.+?)["\']', else_body)
            error_msg = error_msg_match.group(1) if error_msg_match else "Validation failed"

            rule = BusinessRule(
                type=BusinessRuleType.VALIDATION,
                description=f"Guard: {condition.strip()}",
                condition=condition.strip(),
                source_file=file_path,
                error_messages=[error_msg],
            )
            self.analysis.business_rules.append(rule)

    def _extract_swift_error_handling(self, content: str, file_path: str) -> None:
        """Extract Swift error handling (do-catch, throws)"""
        # Find catch blocks
        catches = re.findall(r"catch\s+(?:let\s+)?(\w+)?\s*\{([^}]+)\}", content)

        for error_var, _ in catches:
            error_type = error_var or "Error"
            rule = BusinessRule(
                type=BusinessRuleType.ERROR_HANDLING,
                description=f"Handle {error_type}",
                condition=f"When {error_type} is thrown",
                source_file=file_path,
            )
            self.analysis.business_rules.append(rule)

    # ===== State Machine Extraction =====

    def _extract_state_machines(self) -> None:
        """Extract state machines from source code"""
        # Look for sealed classes (Kotlin) or enums (Swift) representing states
        if self.platform == "android" or self.platform == "unknown":
            self._extract_kotlin_state_machines()

        if self.platform == "ios" or self.platform == "unknown":
            self._extract_swift_state_machines()

    def _extract_kotlin_state_machines(self) -> None:
        """Extract state machines from Kotlin sealed classes"""
        kt_files = list(self.project_path.rglob("*.kt"))

        for kt_file in kt_files:
            try:
                content = kt_file.read_text(encoding="utf-8")

                # Find sealed classes that represent states
                sealed_matches = re.finditer(
                    r"sealed\s+class\s+(\w+State)\s*\{(.*?)\n\}",
                    content,
                    re.DOTALL,
                )

                for match in sealed_matches:
                    state_name = match.group(1)
                    body = match.group(2)

                    # Extract state variants
                    states = re.findall(r"(?:data\s+)?class\s+(\w+)\s*(?:\(.*?\))?", body)
                    states = [s for s in states if s != state_name]

                    if len(states) > 1:
                        # Try to find transitions in when expressions
                        transitions = self._find_state_transitions(content, states)

                        state_machine = StateMachine(
                            name=state_name,
                            states=states,
                            transitions=transitions,
                            initial_state=states[0] if states else "Unknown",
                            source_file=str(kt_file),
                        )
                        self.analysis.state_machines.append(state_machine)

            except Exception as e:
                print(f"Warning: Could not extract state machine from {kt_file}: {e}")

    def _extract_swift_state_machines(self) -> None:
        """Extract state machines from Swift enums"""
        swift_files = list(self.project_path.rglob("*.swift"))

        for swift_file in swift_files:
            try:
                content = swift_file.read_text(encoding="utf-8")

                # Find enums that represent states
                enum_matches = re.finditer(r"enum\s+(\w+State)\s*\{(.*?)\n\}", content, re.DOTALL)

                for match in enum_matches:
                    state_name = match.group(1)
                    body = match.group(2)

                    # Extract cases
                    states = re.findall(r"case\s+(\w+)", body)

                    if len(states) > 1:
                        transitions = self._find_state_transitions(content, states)

                        state_machine = StateMachine(
                            name=state_name,
                            states=states,
                            transitions=transitions,
                            initial_state=states[0] if states else "Unknown",
                            source_file=str(swift_file),
                        )
                        self.analysis.state_machines.append(state_machine)

            except Exception as e:
                print(f"Warning: Could not extract Swift state machine from {swift_file}: {e}")

    def _find_state_transitions(self, content: str, states: List[str]) -> Dict[str, List[str]]:
        """Find state transitions in when/switch expressions"""
        transitions: Dict[str, List[str]] = {state: [] for state in states}

        # Look for patterns like "state = NewState"
        for from_state in states:
            pattern = rf"{from_state}.*?=\s*(\w+)"
            matches = re.findall(pattern, content)
            for to_state in matches:
                if to_state in states and to_state not in transitions[from_state]:
                    transitions[from_state].append(to_state)

        return transitions

    # ===== Edge Case Detection =====

    def _detect_edge_cases(self) -> None:
        """Detect edge cases from code analysis"""
        # Boundary conditions
        self._detect_boundary_conditions()

        # Null/nil checks
        self._detect_null_checks()

        # Empty collection checks
        self._detect_empty_checks()

        # Overflow/underflow patterns
        self._detect_overflow_patterns()

    def _detect_boundary_conditions(self) -> None:
        """Detect boundary condition checks"""
        all_files = (
            list(self.project_path.rglob("*.kt"))
            + list(self.project_path.rglob("*.java"))
            + list(self.project_path.rglob("*.swift"))
        )

        seen_boundaries = set()  # Track unique boundary checks

        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Find comparisons with boundaries
                boundaries = re.findall(r"(\w+)\s*([<>=!]+)\s*(\d+)", content)

                for var_name, operator, value in boundaries:
                    if operator in ["<", "<=", ">", ">="] and value != "0":
                        # Create unique key for deduplication
                        boundary_key = (var_name, operator, value, str(file_path))

                        if boundary_key not in seen_boundaries:
                            seen_boundaries.add(boundary_key)

                            test_values = self._generate_boundary_test_values(int(value), operator)

                            edge_case = EdgeCase(
                                type="boundary",
                                description=f"Boundary check: {var_name} {operator} {value}",
                                test_data=test_values,
                                source_file=str(file_path),
                                severity="high",
                            )
                            self.analysis.edge_cases.append(edge_case)

            except Exception as e:
                print(f"Warning: Could not detect boundaries in {file_path}: {e}")

    def _generate_boundary_test_values(self, boundary: int, operator: str) -> List[int]:
        """Generate test values for boundary conditions"""
        if operator in ["<", "<="]:
            return [boundary - 1, boundary, boundary + 1]
        elif operator in [">", ">="]:
            return [boundary - 1, boundary, boundary + 1]
        else:
            return [boundary]

    def _detect_null_checks(self) -> None:
        """Detect null/nil safety checks"""
        all_files = list(self.project_path.rglob("*.kt")) + list(self.project_path.rglob("*.swift"))

        seen_null_checks = set()  # Track unique null checks

        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Kotlin null checks
                kt_null_checks = re.findall(r"(\w+)\s*[?!]=\s*null", content)

                # Swift nil checks
                swift_nil_checks = re.findall(r"(?:if|guard)\s+let\s+(\w+)", content)

                all_checks = set(kt_null_checks + swift_nil_checks)

                for var_name in all_checks:
                    # Create unique key for deduplication
                    null_check_key = (var_name, str(file_path))

                    if null_check_key not in seen_null_checks:
                        seen_null_checks.add(null_check_key)

                        edge_case = EdgeCase(
                            type="null",
                            description=f"Null safety check for {var_name}",
                            test_data=[None, "valid_value"],
                            source_file=str(file_path),
                            severity="high",
                        )
                        self.analysis.edge_cases.append(edge_case)

            except Exception as e:
                print(f"Warning: Could not detect null checks in {file_path}: {e}")

    def _detect_empty_checks(self) -> None:
        """Detect empty collection/string checks"""
        all_files = list(self.project_path.rglob("*.kt")) + list(self.project_path.rglob("*.swift"))

        seen_empty_checks = set()  # Track unique empty checks across files

        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # isEmpty checks
                empty_checks = re.findall(r"(\w+)\.isEmpty\(\)", content)

                for var_name in set(empty_checks):
                    # Create unique key for deduplication (include file_path like other methods)
                    empty_check_key = (var_name, str(file_path))

                    if empty_check_key not in seen_empty_checks:
                        seen_empty_checks.add(empty_check_key)

                        edge_case = EdgeCase(
                            type="empty",
                            description=f"Empty check for {var_name}",
                            test_data=[[], ["item"], "", "text"],
                            source_file=str(file_path),
                            severity="medium",
                        )
                        self.analysis.edge_cases.append(edge_case)

            except Exception as e:
                print(f"Warning: Could not detect empty checks in {file_path}: {e}")

    def _detect_overflow_patterns(self) -> None:
        """Detect potential overflow/underflow patterns"""
        all_files = list(self.project_path.rglob("*.kt")) + list(self.project_path.rglob("*.java"))

        # Track seen overflow patterns across all files
        seen_overflow = set()

        for file_path in all_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                # Arithmetic operations
                arithmetic = re.findall(r"(\w+)\s*([+\-*/])\s*(\w+)", content)

                for left, op, right in arithmetic:
                    if op in ["+", "*"]:
                        # Create unique key for deduplication
                        overflow_key = (left, op, right)

                        # Only add if not seen before
                        if overflow_key not in seen_overflow:
                            seen_overflow.add(overflow_key)
                            edge_case = EdgeCase(
                                type="overflow",
                                description=f"Potential overflow: {left} {op} {right}",
                                test_data=["MAX_VALUE", "MIN_VALUE", 0, 1, -1],
                                source_file=str(file_path),
                                severity="medium",
                            )
                            self.analysis.edge_cases.append(edge_case)

            except Exception as e:
                print(f"Warning: Could not detect overflow patterns in {file_path}: {e}")

    # ===== Negative Test Case Generation =====

    def _generate_negative_test_cases(self) -> None:
        """Generate negative test cases from business rules and edge cases"""
        # From validations
        for rule in self.analysis.business_rules:
            if rule.type == BusinessRuleType.VALIDATION:
                negative_case = {
                    "name": f"Negative: {rule.description}",
                    "type": "negative",
                    "description": f"Test violation of: {rule.condition}",
                    "expected_outcome": "Validation error",
                    "error_messages": rule.error_messages,
                    "priority": "high",
                    "source": ([rule.source_file] if rule.source_file else []),
                }
                self.analysis.negative_test_cases.append(negative_case)

        # From edge cases
        for edge_case in self.analysis.edge_cases:
            if edge_case.severity in ["high", "critical"]:
                negative_case = {
                    "name": f"Negative: {edge_case.description}",
                    "type": "negative",
                    "description": f"Test {edge_case.type} edge case",
                    "test_data": edge_case.test_data,
                    "expected_outcome": "Handle edge case gracefully",
                    "priority": edge_case.severity,
                    "source": ([edge_case.source_file] if edge_case.source_file else []),
                }
                self.analysis.negative_test_cases.append(negative_case)

        # From user flows - generate failure scenarios
        for flow in self.analysis.user_flows:
            # Invalid input scenario
            negative_case = {
                "name": f"Negative: {flow.name} - Invalid Input",
                "type": "negative",
                "description": f"Test {flow.name} with invalid input",
                "steps": flow.steps,
                "expected_outcome": "Show error message",
                "priority": "high",
                "source": ([flow.source_files[0]] if flow.source_files else []),
            }
            self.analysis.negative_test_cases.append(negative_case)

    # ===== API Contract Generation =====

    def _generate_api_contracts(self) -> None:
        """
        Generate API contracts from network calls and service definitions

        Extracts:
        - Endpoint URLs
        - HTTP methods
        - Request/response schemas
        - Error responses
        - Authentication requirements
        """
        if self.platform == "android":
            self._generate_android_api_contracts()
        elif self.platform == "ios":
            self._generate_ios_api_contracts()

    def _generate_android_api_contracts(self) -> None:
        """Generate API contracts from Android/Kotlin code"""
        # Find Retrofit service interfaces
        for file_path in self.project_path.rglob("*.kt"):
            try:
                content = file_path.read_text(encoding="utf-8")

                # Look for @GET, @POST, @PUT, @DELETE annotations
                api_methods = re.findall(
                    r"@(GET|POST|PUT|DELETE|PATCH)\(\"([^\"]+)\"\)\s+"
                    r"(?:suspend\s+)?fun\s+(\w+)\s*\([^)]*\)\s*:\s*([^\s{]+)",
                    content,
                    re.MULTILINE,
                )

                for method, endpoint, func_name, return_type in api_methods:
                    # Extract request parameters
                    func_match = re.search(
                        rf"fun\s+{func_name}\s*\(([^)]*)\)",
                        content,
                    )
                    request_params = {}
                    if func_match:
                        params_str = func_match.group(1)
                        # Parse @Body, @Query, @Path parameters
                        body_params = re.findall(r"@Body\s+(\w+):\s*(\w+)", params_str)
                        query_params = re.findall(r"@Query\(\"(\w+)\"\)\s+(\w+):\s*(\w+)", params_str)
                        path_params = re.findall(r"@Path\(\"(\w+)\"\)\s+(\w+):\s*(\w+)", params_str)

                        if body_params:
                            request_params["body"] = {name: type_name for name, type_name in body_params}
                        if query_params:
                            request_params["query"] = {param: type_name for param, _, type_name in query_params}
                        if path_params:
                            request_params["path"] = {param: type_name for param, _, type_name in path_params}

                    # Extract authentication info
                    auth = None
                    if "@Headers" in content or "Authorization" in content:
                        auth = "Bearer Token"

                    # Create API contract
                    contract = APIContract(
                        endpoint=endpoint,
                        method=method,
                        request_schema=request_params,
                        response_schema={"type": return_type},
                        authentication=auth,
                        description=f"API endpoint: {func_name}",
                        source_file=str(file_path),
                    )

                    # Extract error responses near this specific function
                    # Look for error codes in a context window around the function definition
                    func_start = content.find(f"fun {func_name}")
                    if func_start != -1:
                        # Get ~500 chars before and after function definition
                        context_start = max(0, func_start - 500)
                        context_end = min(len(content), func_start + 1000)
                        func_context = content[context_start:context_end]

                        error_codes = re.findall(r"(4\d{2}|5\d{2})", func_context)
                        if error_codes:
                            contract.error_responses = [
                                {"code": code, "description": "Error response"} for code in set(error_codes)
                            ]

                    self.analysis.api_contracts.append(contract)

            except Exception as e:
                print(f"Warning: Could not analyze API contracts in {file_path}: {e}")

    def _generate_ios_api_contracts(self) -> None:
        """Generate API contracts from iOS/Swift code"""
        for file_path in self.project_path.rglob("*.swift"):
            try:
                content = file_path.read_text(encoding="utf-8")

                # Look for URLSession calls with surrounding context
                url_pattern = r'URL\(string:\s*"([^"]+)"\)'
                url_matches = list(re.finditer(url_pattern, content))

                # Process each URL individually
                for url_match in url_matches:
                    url = url_match.group(1)

                    # Find HTTP method in context around this specific URL (not globally)
                    url_pos = url_match.start()
                    context_start = max(0, url_pos - 500)
                    context_end = min(len(content), url_pos + 500)
                    context = content[context_start:context_end]

                    # Search for httpMethod assignment in this context
                    method_match = re.search(r'httpMethod\s*=\s*"(GET|POST|PUT|DELETE|PATCH)"', context)
                    method = method_match.group(1) if method_match else "GET"

                    # Find schemas near this specific URL
                    # Extract Codable structs within this context
                    schemas = re.findall(
                        r"struct\s+(\w+):\s*Codable\s*{([^}]+)}",
                        context,
                        re.MULTILINE,
                    )

                    request_schema = {}
                    response_schema = {}

                    if schemas:
                        # Use first schema as response, second as request
                        if len(schemas) > 0:
                            struct_name, fields = schemas[0]
                            response_schema = {
                                "type": struct_name,
                                "fields": self._parse_swift_fields(fields),
                            }
                        if len(schemas) > 1:
                            struct_name, fields = schemas[1]
                            request_schema = {
                                "type": struct_name,
                                "fields": self._parse_swift_fields(fields),
                            }

                    # Authentication
                    auth = None
                    if "Authorization" in context or "Bearer" in context:
                        auth = "Bearer Token"

                    contract = APIContract(
                        endpoint=url,
                        method=method,
                        request_schema=request_schema,
                        response_schema=response_schema,
                        authentication=auth,
                        description=f"iOS API call from {file_path.name}",
                        source_file=str(file_path),
                    )

                    # Extract error handling from context
                    if "catch" in context or "Result" in context:
                        contract.error_responses = [
                            {
                                "type": "NetworkError",
                                "description": "Network failure",
                            },
                            {
                                "type": "DecodingError",
                                "description": "JSON parsing error",
                            },
                        ]

                    self.analysis.api_contracts.append(contract)

            except Exception as e:
                print(f"Warning: Could not analyze API contracts in {file_path}: {e}")

    def _parse_swift_fields(self, fields_str: str) -> Dict[str, str]:
        """Parse Swift struct fields"""
        fields_dict = {}
        field_matches = re.findall(r"let\s+(\w+):\s*(\w+)", fields_str)
        for name, type_name in field_matches:
            fields_dict[name] = type_name
        return fields_dict
