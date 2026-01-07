"""
Business Logic Analyzer

Extracts business logic, rules, and user flows from source code:
- User authentication flows
- Business rules and validations
- Data models and relationships
- State machines and workflows
- Error handling logic
"""

from pathlib import Path
from typing import List, Dict, Optional, Set
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
class BusinessLogicAnalysis:
    """Complete business logic analysis result"""
    user_flows: List[UserFlow] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    data_models: List[DataModel] = field(default_factory=list)
    state_machines: Dict[str, List[str]] = field(default_factory=dict)
    mock_data: Dict[str, any] = field(default_factory=dict)


class BusinessLogicAnalyzer:
    """Analyzes source code to extract business logic"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.analysis = BusinessLogicAnalysis()

    def analyze(self) -> BusinessLogicAnalysis:
        """
        Perform complete business logic analysis

        Returns:
            BusinessLogicAnalysis with extracted information
        """
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

        return self.analysis

    def _analyze_file(self, file_path: Path):
        """Analyze a single source file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract business rules from comments
            self._extract_business_rules_from_comments(content, str(file_path))
            
            # Extract validation rules
            self._extract_validations(content, str(file_path))
            
            # Extract error handling
            self._extract_error_handling(content, str(file_path))
            
        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _analyze_viewmodels(self):
        """Analyze ViewModels to extract user flows"""
        viewmodel_files = list(self.project_path.rglob("*ViewModel.kt"))
        
        for vm_file in viewmodel_files:
            try:
                content = vm_file.read_text(encoding='utf-8')
                
                # Extract flow name from class name
                class_match = re.search(r'class\s+(\w+)ViewModel', content)
                if not class_match:
                    continue
                
                flow_name = class_match.group(1)
                
                # Extract state class
                state_match = re.search(
                    r'var\s+state\s+by\s+mutableStateOf\((\w+)\(\)\)',
                    content
                )
                
                # Extract public methods (user actions)
                methods = re.findall(
                    r'fun\s+(\w+)\([^)]*\)\s*\{',
                    content
                )
                
                # Create user flow
                flow = UserFlow(
                    name=flow_name,
                    description=f"User flow for {flow_name}",
                    steps=[f"User {method}" for method in methods],
                    entry_point=f"{flow_name}Screen",
                    success_outcome="Navigate to next screen",
                    source_files=[str(vm_file)]
                )
                
                self.analysis.user_flows.append(flow)
                
            except Exception as e:
                print(f"Warning: Could not analyze ViewModel {vm_file}: {e}")

    def _analyze_repositories(self):
        """Analyze repositories for data access patterns"""
        repo_files = list(self.project_path.rglob("*Repository.kt"))
        
        for repo_file in repo_files:
            try:
                content = repo_file.read_text(encoding='utf-8')
                
                # Extract interface methods
                interface_methods = re.findall(
                    r'suspend\s+fun\s+(\w+)\([^)]*\):\s*(\w+)',
                    content
                )
                
                for method_name, return_type in interface_methods:
                    # Create business rule for data access
                    rule = BusinessRule(
                        type=BusinessRuleType.AUTHORIZATION,
                        description=f"Data access: {method_name} returns {return_type}",
                        condition=f"User must be authenticated",
                        source_file=str(repo_file),
                        related_entities=[return_type]
                    )
                    self.analysis.business_rules.append(rule)
                    
            except Exception as e:
                print(f"Warning: Could not analyze Repository {repo_file}: {e}")

    def _analyze_models(self):
        """Analyze data models"""
        model_files = list(self.project_path.rglob("models/*.kt"))
        
        for model_file in model_files:
            try:
                content = model_file.read_text(encoding='utf-8')
                
                # Extract data class
                class_match = re.search(
                    r'data\s+class\s+(\w+)\s*\((.*?)\)',
                    content,
                    re.DOTALL
                )
                
                if not class_match:
                    continue
                
                class_name = class_match.group(1)
                params = class_match.group(2)
                
                # Parse fields
                fields = {}
                for field_match in re.finditer(
                    r'val\s+(\w+):\s+([^,\n]+)',
                    params
                ):
                    field_name = field_match.group(1)
                    field_type = field_match.group(2).strip()
                    fields[field_name] = field_type
                
                model = DataModel(
                    name=class_name,
                    fields=fields,
                    source_file=str(model_file)
                )
                
                self.analysis.data_models.append(model)
                
            except Exception as e:
                print(f"Warning: Could not analyze model {model_file}: {e}")

    def _analyze_mock_data(self):
        """Analyze mock data to understand business scenarios"""
        mock_files = list(self.project_path.rglob("mock/*.kt"))
        
        for mock_file in mock_files:
            try:
                content = mock_file.read_text(encoding='utf-8')
                
                # Extract lazy property with mock data
                lazy_match = re.search(
                    r'val\s+MockData\.(\w+).*?by\s+lazy\s*\{(.*?)\}',
                    content,
                    re.DOTALL
                )
                
                if lazy_match:
                    entity_name = lazy_match.group(1)
                    lazy_body = lazy_match.group(2)
                    
                    # Extract range for test data count
                    range_match = re.search(r'\((\d+)L?\.\.(\d+)L?\)', lazy_body)
                    if range_match:
                        start, end = range_match.groups()
                        self.analysis.mock_data[entity_name] = {
                            'count': int(end) - int(start) + 1,
                            'start_id': int(start),
                            'end_id': int(end),
                            'source': str(mock_file)
                        }
                
            except Exception as e:
                print(f"Warning: Could not analyze mock data {mock_file}: {e}")

    def _extract_business_rules_from_comments(self, content: str, file_path: str):
        """Extract business rules from TODO and comments"""
        # Find TODO comments
        todos = re.findall(r'//\s*TODO:?\s*(.+)', content)
        for todo in todos:
            if any(keyword in todo.lower() for keyword in [
                'validate', 'check', 'auth', 'permission', 'rule'
            ]):
                rule = BusinessRule(
                    type=BusinessRuleType.VALIDATION,
                    description=todo.strip(),
                    condition="Not yet implemented",
                    source_file=file_path
                )
                self.analysis.business_rules.append(rule)

    def _extract_validations(self, content: str, file_path: str):
        """Extract validation logic"""
        # Find require() statements
        requires = re.findall(r'require\((.*?)\)\s*\{?\s*["\'](.+?)["\']', content)
        for condition, message in requires:
            rule = BusinessRule(
                type=BusinessRuleType.VALIDATION,
                description=f"Validation: {condition}",
                condition=condition.strip(),
                source_file=file_path,
                error_messages=[message]
            )
            self.analysis.business_rules.append(rule)

    def _extract_error_handling(self, content: str, file_path: str):
        """Extract error handling logic"""
        # Find catch blocks
        catches = re.findall(
            r'catch\s*\(\s*\w+:\s*(\w+)\s*\)\s*\{([^}]+)\}',
            content
        )
        for exception_type, handler_body in catches:
            rule = BusinessRule(
                type=BusinessRuleType.ERROR_HANDLING,
                description=f"Handle {exception_type}",
                condition=f"When {exception_type} occurs",
                source_file=file_path
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
            scenarios.append({
                'name': f"{flow.name} - Happy Path",
                'type': 'positive',
                'description': flow.description,
                'steps': flow.steps,
                'expected_outcome': flow.success_outcome,
                'priority': 'high'
            })
            
            # Failure scenarios
            for failure in flow.failure_outcomes:
                scenarios.append({
                    'name': f"{flow.name} - {failure}",
                    'type': 'negative',
                    'description': f"Test {failure} scenario",
                    'steps': flow.steps[:-1],  # All steps except last
                    'expected_outcome': failure,
                    'priority': 'medium'
                })
        
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
            'user_flows': [
                {
                    'name': flow.name,
                    'description': flow.description,
                    'steps': flow.steps,
                    'entry_point': flow.entry_point,
                    'success_outcome': flow.success_outcome,
                    'failure_outcomes': flow.failure_outcomes,
                    'source_files': flow.source_files
                }
                for flow in self.analysis.user_flows
            ],
            'business_rules': [
                {
                    'type': rule.type.value,
                    'description': rule.description,
                    'condition': rule.condition,
                    'source_file': rule.source_file,
                    'related_entities': rule.related_entities,
                    'error_messages': rule.error_messages
                }
                for rule in self.analysis.business_rules
            ],
            'data_models': [
                {
                    'name': model.name,
                    'fields': model.fields,
                    'validations': model.validations,
                    'source_file': model.source_file
                }
                for model in self.analysis.data_models
            ],
            'mock_data': self.analysis.mock_data
        }

