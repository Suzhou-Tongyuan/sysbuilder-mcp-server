"""Run UTF-8 Sysbuilder modeling scripts."""
from __future__ import annotations

import ast
import builtins
import inspect
import keyword
import re
from pathlib import Path

import sysbuilder_mcp_server.core as sysbuilder_core
from sysbuilder_mcp_server.core.api_catalog import get_api_names
from sysbuilder_mcp_server.mcp_instance import mcp
from sysbuilder_mcp_server.path_config import get_output_root, get_workspace_root
from sysbuilder_mcp_server.tools.common import (
    _json,
    ensure_sysbuilder_session,
    ensure_utf8_script_text,
    execute_python_source,
    get_runtime_modeling_rules_metadata,
    resolve_output_path,
)


_API_NAME_PREFIXES = (
    "New",
    "Create",
    "Set",
    "Get",
    "Open",
    "Save",
    "Export",
    "Import",
    "Generate",
    "Gen",
    "Run",
    "Calculate",
    "Delete",
    "AutoLayout",
    "Adjust",
    "Insert",
    "Start",
    "Find",
    "Connect",
    "Exit",
    "Help",
    "List",
    "Echo",
)

_HIGH_LEVEL_TOOL_NAMES = {
    "create_satisfy_trace",
    "create_allocate_trace",
}

_UNSUPPORTED_API_REPLACEMENTS = {
    "NewObjectNode": "No object-node API is currently exposed. In activity diagrams, use explicit object flows and, when ports are needed, create NewInputPort/NewOutputPort under the activity element itself and connect those endpoints explicitly. Do not try to place ports directly on the activity diagram.",
    "CreateObjectNode": "No object-node API is currently exposed. In activity diagrams, use explicit object flows and, when ports are needed, create input/output ports under the activity element itself. Do not create ports directly on the activity diagram.",
    "CreateActivityActionNode": "Use NewActivity(...) to create an action-like activity element, then InsertElementToDiagram(...).",
    "NewActivityActionNode": "Use NewActivity(...) to create an action-like activity element, then InsertElementToDiagram(...).",
    "CreateSwimlane": "Swimlanes/activity partitions are not exposed. Model responsibility with packages, names, blocks, or allocate relationships.",
    "NewSwimlane": "Swimlanes/activity partitions are not exposed. Model responsibility with packages, names, blocks, or allocate relationships.",
    "CreateActivityPartition": "Activity partitions are not exposed. Model responsibility with packages, names, blocks, or allocate relationships.",
    "NewActivityPartition": "Activity partitions are not exposed. Model responsibility with packages, names, blocks, or allocate relationships.",
    "CreateActivityParameterNode": "Activity parameter nodes are not exposed. If ports are needed, create NewInputPort/NewOutputPort under the activity element itself and connect them with explicit object flows; do not place ports on the activity diagram.",
    "NewActivityParameterNode": "Activity parameter nodes are not exposed. If ports are needed, create NewInputPort/NewOutputPort under the activity element itself and connect them with explicit object flows; do not place ports on the activity diagram.",
}


def _available_sysbuilder_api_names() -> set[str]:
    names = set(_HIGH_LEVEL_TOOL_NAMES)
    names.update(get_api_names())
    for name in dir(sysbuilder_core):
        if name.startswith("_"):
            continue
        value = getattr(sysbuilder_core, name)
        if inspect.isfunction(value):
            names.add(name)
    return names


def _preflight_sysbuilder_api_usage(source: str) -> dict:
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "errors": [f"Python syntax error before execution: {exc}"],
            "warnings": [],
            "forbidden_imports": [],
            "unknown_api_calls": [],
            "available_api_hint": "Fix Python syntax first, then verify Sysbuilder API names with lookup_sysbuilder_api or resources/quickref/sysbuilder_python_api.md.",
        }

    forbidden_imports = []
    local_function_names = set()
    called_names = []
    available_api_names = _available_sysbuilder_api_names()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            local_function_names.add(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            local_function_names.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "mworks" or alias.name.startswith("mworks."):
                    forbidden_imports.append({"module": alias.name, "lineno": getattr(node, "lineno", None)})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "mworks" or module.startswith("mworks."):
                forbidden_imports.append({"module": module, "lineno": getattr(node, "lineno", None)})
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name:
                called_names.append({"name": name, "lineno": getattr(node, "lineno", None)})

    unknown_api_calls = []
    known_unsupported_api_calls = []
    for item in called_names:
        name = item["name"]
        if not name.startswith(_API_NAME_PREFIXES):
            continue
        if name in available_api_names or name in local_function_names:
            continue
        if name in _UNSUPPORTED_API_REPLACEMENTS:
            known_unsupported_api_calls.append(
                {
                    **item,
                    "replacement": _UNSUPPORTED_API_REPLACEMENTS[name],
                }
            )
        unknown_api_calls.append(item)

    errors = []
    warnings = []
    if forbidden_imports:
        errors.append(
            "Do not import mworks.sysbuilder in MCP run_script. Sysbuilder APIs are injected automatically; call APIs directly or use `from sysbuilder_mcp_server.core import *`."
        )
    if unknown_api_calls:
        errors.append(
            "The script calls Sysbuilder-looking API names that are not available in the MCP API catalog. Use lookup_sysbuilder_api or resources/quickref/sysbuilder_python_api.md before execution."
        )
    if known_unsupported_api_calls:
        errors.append(
            "The script uses known unsupported Sysbuilder API names. Apply the replacement guidance in known_unsupported_api_calls; do not retry by inventing similar names."
        )

    if not forbidden_imports:
        warnings.append(
            "Sysbuilder APIs are already injected in run_script; explicit imports are optional. If importing, prefer `from sysbuilder_mcp_server.core import *`."
        )

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "forbidden_imports": forbidden_imports,
        "unknown_api_calls": unknown_api_calls,
        "known_unsupported_api_calls": known_unsupported_api_calls,
        "available_api_count": len(available_api_names),
        "allowed_explicit_import": "from sysbuilder_mcp_server.core import *",
        "api_usage_hint": "Use direct calls such as NewProject(...), CreateRelationMapping(...), and CalculateParametricDiagram(...). Do not invent API names. For relation mapping, create and type both endpoints first, map source to target, then calculate the parametric diagram and inspect parameter_calculation.json. For activity data, use explicit object flows and keep ports under the activity element.",
        "next_recommended_actions": [
            "Call lookup_sysbuilder_api first and lock the needed API set before rewriting the full script in one pass.",
            "Replace unsupported APIs immediately with exposed patterns from quickref; do not keep retrying similar names.",
            "If a state-machine or activity-diagram endpoint was just created with graphName, connect it with the corresponding ByGraphName API instead of guessing full element names.",
        ]
        if errors or warnings
        else [],
    }


def _analyze_traceability_usage(source: str) -> dict:
    calls = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", source or ""))
    creates_requirements = "NewRequirement" in calls
    creates_behavior = bool({"NewActivity", "NewBlock"} & calls)
    creates_satisfy = bool({"CreateRequirementSatisfyLine", "create_satisfy_trace"} & calls)
    creates_allocate = bool({"CreateAllocateLine", "create_allocate_trace"} & calls)

    warnings = []
    next_recommended_actions = []
    if creates_requirements and not creates_satisfy:
        warnings.append("The script creates requirements but does not create satisfy trace relationships.")
        next_recommended_actions.append(
            "Call create_satisfy_trace(...) or CreateRequirementSatisfyLine(...) from implementation elements to requirements."
        )
    if creates_behavior and not creates_allocate:
        warnings.append("The script creates activities/blocks but does not create allocate trace relationships.")
        next_recommended_actions.append(
            "Call create_allocate_trace(...) or CreateAllocateLine(...) from functions/activities to architecture blocks."
        )

    return {
        "calls_detected": sorted(calls),
        "creates_requirements": creates_requirements,
        "creates_behavior_or_blocks": creates_behavior,
        "creates_satisfy": creates_satisfy,
        "creates_allocate": creates_allocate,
        "warnings": warnings,
        "next_recommended_actions": next_recommended_actions,
        "high_level_tools": ["create_satisfy_trace", "create_allocate_trace"],
    }


def _analyze_parametric_verification_usage(source: str) -> dict:
    """分析关系映射和参数图计算调用是否遵循先建模、后映射、再计算的顺序。"""
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze parametric verification because the script has syntax errors: {exc}"],
            "relation_mapping_lines": [],
            "parametric_calculation_lines": [],
            "next_recommended_actions": [],
        }

    relation_mapping_lines: list[int] = []
    parametric_calculation_lines: list[int] = []
    constraint_expression_lines: list[int] = []
    parametric_diagram_lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        lineno = getattr(node, "lineno", 0) or 0
        if name == "CreateRelationMapping":
            relation_mapping_lines.append(lineno)
        elif name == "CalculateParametricDiagram":
            parametric_calculation_lines.append(lineno)
        elif name == "SetConstraintExpression":
            constraint_expression_lines.append(lineno)
        elif name == "NewPARDiagram":
            parametric_diagram_lines.append(lineno)

    relation_mapping_lines.sort()
    parametric_calculation_lines.sort()
    constraint_expression_lines.sort()
    parametric_diagram_lines.sort()

    warnings: list[str] = []
    if parametric_calculation_lines:
        first_calculation = parametric_calculation_lines[0]
        if any(line > first_calculation for line in relation_mapping_lines):
            warnings.append(
                "CreateRelationMapping(...) appears after CalculateParametricDiagram(...). Create all mappings before calculating the parametric diagram."
            )
        if any(line > first_calculation for line in constraint_expression_lines):
            warnings.append(
                "SetConstraintExpression(...) appears after CalculateParametricDiagram(...). Define constraints before calculation."
            )
        if any(line > first_calculation for line in parametric_diagram_lines):
            warnings.append(
                "NewPARDiagram(...) appears after CalculateParametricDiagram(...). Create the parametric diagram before calculation."
            )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "relation_mapping_lines": relation_mapping_lines,
        "parametric_calculation_lines": parametric_calculation_lines,
        "constraint_expression_lines": constraint_expression_lines,
        "parametric_diagram_lines": parametric_diagram_lines,
        "verification_chain_detected": bool(relation_mapping_lines and parametric_calculation_lines),
        "next_recommended_actions": [
            "Create and type every mapping endpoint, define constraints and parameter-diagram bindings, then call CreateRelationMapping(...) from source to target.",
            "Call CalculateParametricDiagram(...) only after all mappings are complete, then inspect parameter_calculation.json values, constraint satisfaction, and error.",
        ]
        if relation_mapping_lines or parametric_calculation_lines
        else [],
    }



_ACTIVITY_LOGIC_NODE_CALLS = {
    "CreateActivityInitialNode": "initial",
    "CreateActivityFinalNode": "final",
    "CreateActivityFlowFinalNode": "flow_final",
    "CreateActivityDecisionNode": "decision",
    "CreateActivityMergeNode": "merge",
    "CreateActivityEventNode": "event",
    "CreateActivitySignalNode": "signal",
    "CreateActivityTimeEventNode": "time_event",
    "CreateActivityForkNode": "fork",
    "CreateActivityForkVerticalNode": "fork",
    "CreateActivityJoinNode": "join",
    "CreateActivityJoinVerticalNode": "join",
}

_CONSTRAINT_INTERFACE_CREATION_CALLS = {
    "NewInterfaceBlock",
    "NewInputParam",
    "NewOutputParam",
    "NewReturnParam",
    "NewProxyPort",
    "NewInputPort",
    "NewOutputPort",
    "NewValueProperty",
}

_ACTIVITY_INTERFACE_CREATION_CALLS = {
    "NewInputPort",
    "NewOutputPort",
}

_CONSTRAINT_EXPRESSION_RESERVED_WORDS = {
    "and",
    "or",
    "not",
    "true",
    "false",
    "True",
    "False",
    "if",
    "else",
    "min",
    "max",
    "abs",
    "sqrt",
    "sin",
    "cos",
    "tan",
    "exp",
    "log",
    "ln",
    "pow",
}

_STATE_TRANSITION_CONDITION_OPERATORS = (
    "==",
    "!=",
    ">=",
    "<=",
    ">",
    "<",
)

_ACTIVITY_SCRIPT_RESERVED_NAMES = set(keyword.kwlist) | set(dir(builtins)) | {
    "None",
    "True",
    "False",
    "__name__",
}

_STATE_NODE_CALLS = {
    "CreateState": "state",
    "CreateCompositeState": "composite_state",
    "CreateOrthogonalState": "orthogonal_state",
}

_STATE_SUBSTATE_CALL = "CreateSubState"

_STATE_CONTROL_NODE_CALLS = {
    "CreateStateInitialNode": "initial",
    "CreateStateFinalNode": "final",
    "CreateStateTerminateNode": "terminate",
    "CreateStateChoiceNode": "choice",
    "CreateStateForkNode": "fork",
    "CreateStateForkVerticalNode": "fork",
    "CreateStateJoinNode": "join",
    "CreateStateJoinVerticalNode": "join",
}

_STATE_BEHAVIOR_CALLS = {
    "SetStateEntry",
    "SetStateDoActivity",
    "SetStateExit",
}


def _literal_string(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        value = ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return ""
    return value if isinstance(value, str) else ""


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _get_call_arg(call: ast.Call, index: int, keyword_name: str) -> ast.AST | None:
    for keyword in call.keywords:
        if keyword.arg == keyword_name:
            return keyword.value
    if len(call.args) > index:
        return call.args[index]
    return None


def _analyze_activity_logic_node_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze activity logic node connectivity because the script has syntax errors: {exc}"],
            "unconnected_logic_nodes": [],
            "nodes": [],
            "graph_name_edges": [],
        }

    nodes: list[dict] = []
    edges: list[dict] = []
    incoming: dict[str, int] = {}
    outgoing: dict[str, int] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in _ACTIVITY_LOGIC_NODE_CALLS:
            graph_name = _literal_string(_get_call_arg(node, 1, "graphName"))
            if graph_name:
                nodes.append(
                    {
                        "graph_name": graph_name,
                        "node_type": _ACTIVITY_LOGIC_NODE_CALLS[name],
                        "api": name,
                        "lineno": getattr(node, "lineno", None),
                    }
                )
        elif name in {"CreateActivityControlFlowLineByGraphName", "CreateActivityObjectFlowLineByGraphName"}:
            start_name = _literal_string(_get_call_arg(node, 1, "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endGraphName"))
            line_name = _literal_string(_get_call_arg(node, 3, "lineName"))
            if start_name and end_name:
                edges.append(
                    {
                        "start_graph_name": start_name,
                        "end_graph_name": end_name,
                        "line_name": line_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", None),
                    }
                )
                outgoing[start_name] = outgoing.get(start_name, 0) + 1
                incoming[end_name] = incoming.get(end_name, 0) + 1

    unconnected = []
    degree_warnings = []
    node_types = {item["graph_name"]: item["node_type"] for item in nodes}
    missing_guard_edges = []
    decision_nodes_with_multiple_incoming = []
    decision_nodes_with_incoming_control_flow = []
    for item in nodes:
        graph_name = item["graph_name"]
        in_count = incoming.get(graph_name, 0)
        out_count = outgoing.get(graph_name, 0)
        item["incoming"] = in_count
        item["outgoing"] = out_count
        if in_count == 0 and out_count == 0:
            unconnected.append(item)

        node_type = item["node_type"]
        if node_type == "initial" and out_count == 0:
            degree_warnings.append(f"Activity initial node `{graph_name}` has no outgoing graph-name flow.")
        elif node_type in {"final", "flow_final"} and in_count == 0:
            degree_warnings.append(f"Activity final node `{graph_name}` has no incoming graph-name flow.")
        elif node_type == "decision" and in_count > 1:
            decision_nodes_with_multiple_incoming.append(item)
            degree_warnings.append(
                f"Activity decision/choice node `{graph_name}` must have exactly one incoming flow; found {in_count}."
            )
        elif node_type == "decision" and out_count == 0:
            degree_warnings.append(
                f"Activity decision/choice node `{graph_name}` should have outgoing graph-name control flows."
            )
        elif node_type not in {"initial", "final", "flow_final", "decision"} and (in_count == 0 or out_count == 0):
            degree_warnings.append(
                f"Activity logic node `{graph_name}` ({node_type}) should have both incoming and outgoing graph-name flows."
            )

    for edge in edges:
        if edge["api"] == "CreateActivityControlFlowLineByGraphName":
            if node_types.get(edge["start_graph_name"]) == "decision":
                line_name = edge.get("line_name", "").strip()
                if not (line_name.startswith("[") and line_name.endswith("]") and len(line_name) > 2):
                    missing_guard_edges.append(edge)
            if node_types.get(edge["end_graph_name"]) == "decision":
                decision_nodes_with_incoming_control_flow.append(edge)

    if unconnected:
        warnings.append(
            "Some activity logic nodes are created but never referenced by graph-name flow lines; they may appear isolated in the activity diagram."
        )
    warnings.extend(degree_warnings)
    if missing_guard_edges:
        warnings.append(
            "Outgoing control-flow lines from activity decision/choice nodes should include a guard in lineName, for example CreateActivityControlFlowLineByGraphName(diagram, 'Decision', 'Next', '[condition]')."
        )
    if decision_nodes_with_incoming_control_flow:
        warnings.append(
            "Activity decision/choice nodes must not have incoming control-flow lines; the single incoming line to a decision node must be an object flow from the upstream activity."
        )

    return {
        "ok": True,
        "warnings": warnings,
        "unconnected_logic_nodes": unconnected,
        "decision_nodes_with_multiple_incoming": decision_nodes_with_multiple_incoming,
        "decision_nodes_with_incoming_control_flow": decision_nodes_with_incoming_control_flow,
        "decision_control_flows_missing_guard": missing_guard_edges,
        "nodes": nodes,
        "graph_name_edges": edges,
        "next_recommended_actions": [
            "Connect activity logic nodes with CreateActivityControlFlowLineByGraphName(...) or CreateActivityObjectFlowLineByGraphName(...).",
            "Use the exact graphName passed to CreateActivity*Node(...) as the flow endpoint name.",
            "Add bracketed guards to decision/choice outgoing control flows, such as '[valid]' and '[else]'.",
            "Keep exactly one incoming flow for each activity decision/choice node.",
            "Do not add control-flow lines into decision/choice nodes; use exactly one incoming object flow from the upstream activity.",
            "For decision/choice nodes, treat the incoming line separately: use one incoming object flow, then use graph-name control flows only for outgoing branches.",
        ]
        if warnings
        else [],
    }


def _analyze_state_machine_complexity(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze state machine complexity because the script has syntax errors: {exc}"],
            "state_machines": [],
        }

    diagrams: dict[str, dict] = {}
    state_machine_defs: list[dict] = []
    state_behaviors: list[dict] = []
    substates: list[dict] = []

    def _diagram_item(diagram_name: str) -> dict:
        return diagrams.setdefault(
            diagram_name,
            {
                "diagram": diagram_name,
                "states": [],
                "control_nodes": [],
                "transitions": [],
                "behavior_bindings": [],
            },
        )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewStateMachine":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                state_machine_defs.append({"full_name": full_name, "lineno": getattr(node, "lineno", 0) or 0})
        elif name == "NewSTMDiagram":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                _diagram_item(full_name)
        elif name in _STATE_NODE_CALLS:
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            graph_name = _literal_string(_get_call_arg(node, 1, "graphName"))
            if diagram_name:
                _diagram_item(diagram_name)["states"].append(
                    {
                        "graph_name": graph_name,
                        "node_type": _STATE_NODE_CALLS[name],
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == _STATE_SUBSTATE_CALL:
            parent_state = _literal_string(_get_call_arg(node, 0, "parentStateFullName"))
            graph_name = _literal_string(_get_call_arg(node, 2, "graphName"))
            if parent_state:
                substates.append(
                    {
                        "parent_state": parent_state,
                        "graph_name": graph_name,
                        "node_type": "substate",
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name in _STATE_CONTROL_NODE_CALLS:
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            graph_name = _literal_string(_get_call_arg(node, 1, "graphName"))
            if diagram_name:
                _diagram_item(diagram_name)["control_nodes"].append(
                    {
                        "graph_name": graph_name,
                        "node_type": _STATE_CONTROL_NODE_CALLS[name],
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name in {"CreateStateTransitionLine", "CreateStateTransitionLineByGraphName"}:
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            if diagram_name:
                _diagram_item(diagram_name)["transitions"].append(
                    {
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name in _STATE_BEHAVIOR_CALLS:
            target = _literal_string(_get_call_arg(node, 0, "fullName"))
            binding = {
                "target": target,
                "api": name,
                "lineno": getattr(node, "lineno", 0) or 0,
            }
            state_behaviors.append(binding)

    for diagram_name, item in diagrams.items():
        stm_name = diagram_name.rsplit(".", 1)[0] if "." in diagram_name else ""
        # CreateSubState 只给父状态全名，不给图名；按状态机前缀归入对应状态机图。
        item["states"].extend(
            substate
            for substate in substates
            if stm_name and substate["parent_state"].startswith(f"{stm_name}.")
        )
        item["behavior_bindings"] = [
            binding
            for binding in state_behaviors
            if stm_name and binding["target"].startswith(f"{stm_name}.")
        ]
        states = item["states"]
        control_nodes = item["control_nodes"]
        transitions = item["transitions"]
        has_choice = any(node["node_type"] == "choice" for node in control_nodes)
        has_fork_join = (
            any(node["node_type"] == "fork" for node in control_nodes)
            and any(node["node_type"] == "join" for node in control_nodes)
        )
        has_composite_or_orthogonal = any(
            state["node_type"] in {"composite_state", "orthogonal_state"} for state in states
        )
        item["metrics"] = {
            "state_count": len(states),
            "transition_count": len(transitions),
            "has_choice": has_choice,
            "has_fork_join": has_fork_join,
            "has_composite_or_orthogonal": has_composite_or_orthogonal,
            "behavior_binding_count": len(item["behavior_bindings"]),
        }
        item_warnings = []
        if len(states) < 4:
            item_warnings.append("create at least 4 stable state nodes")
        if not has_choice:
            item_warnings.append("add a CreateStateChoiceNode(...) branch")
        if not (has_fork_join or has_composite_or_orthogonal):
            item_warnings.append("add fork/join concurrency or a composite/orthogonal state")
        if len(transitions) < 5:
            item_warnings.append("create at least 5 transitions")
        if not item["behavior_bindings"]:
            item_warnings.append("bind at least one entry/doActivity/exit behavior")
        item["complexity_warnings"] = item_warnings
        if item_warnings:
            warnings.append(
                f"State machine diagram `{diagram_name}` looks too simple: " + "; ".join(item_warnings) + "."
            )

    return {
        "ok": True,
        "warnings": warnings,
        "state_machine_definitions": state_machine_defs,
        "state_machines": list(diagrams.values()),
        "next_recommended_actions": [
            "Prefer lifecycle-rich state machines with stable states, choice branches, normal/error/recovery transitions, and at least one state behavior.",
            "Use CreateStateForkNode/CreateStateJoinNode or CreateCompositeState/CreateOrthogonalState when the modeled object has concurrent or nested modes.",
            "After all diagram blocks and lines are created, call AutoLayoutDiagram(...), then AdjustDiagramFrameToOptimalSize(...).",
        ]
        if warnings
        else [],
    }


def _analyze_state_transition_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze state transition usage because the script has syntax errors: {exc}"],
            "state_diagrams": [],
            "bad_transition_calls": [],
        }

    diagrams: dict[str, dict] = {}
    element_name_transition_calls: list[dict] = []
    bad_transition_calls: list[dict] = []
    explicit_graph_name_missing: list[dict] = []
    substate_graph_names: dict[str, set[str]] = {}
    state_machine_value_props: dict[str, set[str]] = {}
    invalid_transition_conditions: list[dict] = []
    transition_condition_unknown_variables: list[dict] = []
    multiple_unconditional_transitions: list[dict] = []

    def _diagram_item(diagram_name: str) -> dict:
        return diagrams.setdefault(
            diagram_name,
            {
                "diagram": diagram_name,
                "created_graph_names": [],
                "transitions_by_graph_name": [],
                "transitions_by_element_name": [],
                "unknown_graph_name_endpoints": [],
                "full_name_passed_to_graph_name_api": [],
                "missing_explicit_graph_names": [],
                "invalid_transition_conditions": [],
                "transition_condition_unknown_variables": [],
                "multiple_unconditional_transitions": [],
            },
        )

    def _stm_name_from_diagram(diagram_name: str) -> str:
        return diagram_name.rsplit(".", 1)[0] if "." in diagram_name else ""

    def _expression_identifiers(expression: str) -> set[str]:
        return {
            token
            for token in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expression or "")
            if token not in _CONSTRAINT_EXPRESSION_RESERVED_WORDS and token not in {"true", "false", "True", "False"}
        }

    def _is_condition_expression_valid(expression: str) -> tuple[bool, str]:
        raw = (expression or "").strip()
        if not raw:
            return False, "missing_condition"
        if raw.startswith("[") and raw.endswith("]"):
            return False, "bracket_label_not_allowed"
        if re.fullmatch(r"\d+(\.\d+)?", raw):
            return False, "numeric_label_not_allowed"
        if not any(op in raw for op in _STATE_TRANSITION_CONDITION_OPERATORS):
            return False, "no_comparison_operator"
        try:
            ast.parse(raw, mode="eval")
        except SyntaxError:
            return False, "not_parseable_expression"
        return True, ""

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewSTMDiagram":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if diagram_name:
                _diagram_item(diagram_name)
        elif name in _STATE_NODE_CALLS or name in _STATE_CONTROL_NODE_CALLS:
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            graph_name = _literal_string(_get_call_arg(node, 1, "graphName"))
            if diagram_name:
                if graph_name:
                    _diagram_item(diagram_name)["created_graph_names"].append(
                        {
                            "graph_name": graph_name,
                            "api": name,
                            "lineno": getattr(node, "lineno", 0) or 0,
                        }
                    )
                elif name in _STATE_CONTROL_NODE_CALLS:
                    bad = {
                        "diagram": diagram_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                        "problem": "missing_explicit_graph_name",
                    }
                    _diagram_item(diagram_name)["missing_explicit_graph_names"].append(bad)
                    explicit_graph_name_missing.append(bad)
        elif name == _STATE_SUBSTATE_CALL:
            parent_state = _literal_string(_get_call_arg(node, 0, "parentStateFullName"))
            graph_name = _literal_string(_get_call_arg(node, 2, "graphName"))
            if parent_state and graph_name:
                stm_name = parent_state.rsplit(".", 1)[0] if "." in parent_state else parent_state
                substate_graph_names.setdefault(stm_name, set()).add(graph_name)
        elif name == "NewValueProperty":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if "." in full_name:
                parent = ".".join(full_name.split(".")[:-1])
                state_machine_value_props.setdefault(parent, set()).add(_last_name_segment(full_name))
        elif name == "CreateStateTransitionLineByGraphName":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endGraphName"))
            line_name = _literal_string(_get_call_arg(node, 3, "lineName"))
            if diagram_name:
                item = {
                    "api": name,
                    "start_graph_name": start_name,
                    "end_graph_name": end_name,
                    "line_name": line_name,
                    "lineno": getattr(node, "lineno", 0) or 0,
                }
                _diagram_item(diagram_name)["transitions_by_graph_name"].append(item)
        elif name == "CreateStateTransitionLine":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startElementName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endElementName"))
            line_name = _literal_string(_get_call_arg(node, 3, "lineName"))
            call = {
                "api": name,
                "diagram": diagram_name,
                "start_element_name": start_name,
                "end_element_name": end_name,
                "line_name": line_name,
                "lineno": getattr(node, "lineno", 0) or 0,
            }
            element_name_transition_calls.append(call)
            if diagram_name:
                _diagram_item(diagram_name)["transitions_by_element_name"].append(call)

    for diagram_name, item in diagrams.items():
        created_names = {
            created["graph_name"]
            for created in item["created_graph_names"]
            if created.get("graph_name")
        }
        stm_name = _stm_name_from_diagram(diagram_name)
        for parent_name, graph_names in substate_graph_names.items():
            if stm_name and parent_name.startswith(f"{stm_name}."):
                created_names.update(graph_names)
        known_value_props = state_machine_value_props.get(stm_name, set())
        outgoing_counts: dict[str, dict[str, object]] = {}
        for transition in item["transitions_by_graph_name"]:
            # 新版 API 允许 ByGraphName 端点按图形名优先、再按限定名兜底解析。
            # 因此只对简单图形名做本地创建顺序校验，避免误伤合法的限定名端点。
            unknown = [
                value
                for value in (transition["start_graph_name"], transition["end_graph_name"])
                if value and "." not in value and created_names and value not in created_names
            ]
            if unknown:
                bad = {
                    **transition,
                    "diagram": diagram_name,
                    "problem": "unknown_graph_name_endpoint",
                    "unknown_endpoints": unknown,
                    "known_graph_names": sorted(created_names),
                }
                item["unknown_graph_name_endpoints"].append(bad)
                bad_transition_calls.append(bad)

            raw_condition = (transition.get("line_name") or "").strip()
            start_key = transition.get("start_graph_name") or ""
            bucket = outgoing_counts.setdefault(start_key, {"unconditional": 0, "items": []})
            bucket["items"].append(transition)
            if not raw_condition:
                bucket["unconditional"] = int(bucket["unconditional"]) + 1
            else:
                ok, reason = _is_condition_expression_valid(raw_condition)
                if not ok:
                    bad = {
                        **transition,
                        "diagram": diagram_name,
                        "problem": "invalid_transition_condition",
                        "reason": reason,
                    }
                    item["invalid_transition_conditions"].append(bad)
                    invalid_transition_conditions.append(bad)
                vars_in_expr = sorted(_expression_identifiers(raw_condition))
                unknown_vars = [name for name in vars_in_expr if name not in known_value_props]
                if unknown_vars:
                    bad = {
                        **transition,
                        "diagram": diagram_name,
                        "problem": "transition_condition_unknown_variables",
                        "unknown_variables": unknown_vars,
                        "known_state_machine_value_properties": sorted(known_value_props),
                    }
                    item["transition_condition_unknown_variables"].append(bad)
                    transition_condition_unknown_variables.append(bad)

        for start_key, counts in outgoing_counts.items():
            if int(counts["unconditional"]) > 1:
                bad = {
                    "diagram": diagram_name,
                    "start_graph_name": start_key,
                    "problem": "multiple_unconditional_transitions",
                    "unconditional_count": int(counts["unconditional"]),
                }
                item["multiple_unconditional_transitions"].append(bad)
                multiple_unconditional_transitions.append(bad)

        if item["transitions_by_element_name"] and item["created_graph_names"]:
            warnings.append(
                f"State machine diagram `{diagram_name}` uses CreateStateTransitionLine(...). For automatically created CreateState* graph nodes, use CreateStateTransitionLineByGraphName(...) with exact graphName endpoints instead."
            )

    if any(item["unknown_graph_name_endpoints"] for item in diagrams.values()):
        warnings.append(
            "Some simple state transition endpoints do not match any graphName created earlier in the same diagram. Check graphName spelling and creation order."
        )
    if explicit_graph_name_missing:
        warnings.append(
            "Some state-machine control nodes were created without an explicit graphName. Always pass a simple graphName for initial/choice/fork/join/final/terminate nodes."
        )
    if invalid_transition_conditions:
        warnings.append(
            "Some state transition conditions are not explicit boolean expressions. Use expressions such as `time > 1`, not labels like `1`, `2`, `加速`, or `[停止运行]`."
        )
    if transition_condition_unknown_variables:
        warnings.append(
            "Some state transition conditions reference variables that are not created as same-named value properties under the state machine."
        )
    if multiple_unconditional_transitions:
        warnings.append(
            "Some states or control nodes have more than one unconditional outgoing transition. At most one unconditional outgoing transition is allowed."
        )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "state_diagrams": list(diagrams.values()),
        "bad_transition_calls": bad_transition_calls,
        "missing_explicit_graph_names": explicit_graph_name_missing,
        "invalid_transition_conditions": invalid_transition_conditions,
        "transition_condition_unknown_variables": transition_condition_unknown_variables,
        "multiple_unconditional_transitions": multiple_unconditional_transitions,
        "next_recommended_actions": [
            "Create every state/control node with an explicit simple graphName.",
            "Connect automatically created state-machine nodes with CreateStateTransitionLineByGraphName(diagram, startGraphName, endGraphName); qualified endpoints are allowed when the backend can resolve them.",
            "For branching transitions, use explicit boolean conditions such as `time > 1` and create every referenced variable as a same-named value property under the state machine first.",
            "Allow at most one unconditional outgoing transition from the same state or control node.",
            "Do not retry failed state-machine connections with CreateStateTransitionLine(...) unless both endpoints are pre-existing elements with verified full names.",
        ]
        if warnings
        else [],
    }


def _analyze_state_machine_behavior_element_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze state-machine behavior elements because the script has syntax errors: {exc}"],
            "bad_activity_creations": [],
        }

    state_machine_names: set[str] = set()
    bad_activity_creations: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewStateMachine":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                state_machine_names.add(full_name)
        elif name == "NewActivity":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if not full_name:
                continue
            parent_name = ".".join(full_name.split(".")[:-1]) if "." in full_name else ""
            if parent_name and parent_name in state_machine_names:
                bad_activity_creations.append(
                    {
                        "api": name,
                        "full_name": full_name,
                        "state_machine": parent_name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                        "problem": "activity_created_directly_under_state_machine",
                    }
                )

    if bad_activity_creations:
        warnings.append(
            "Do not create activities directly under a state machine. State-machine-local actions should be modeled as opaque behaviors with NewOpaqueBehavior(...)."
        )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "bad_activity_creations": bad_activity_creations,
        "next_recommended_actions": [
            "Under a state machine, use NewOpaqueBehavior(...) for state-local actions instead of NewActivity(...).",
            "Then bind that opaque behavior with SetStateEntry(...), SetStateDoActivity(...), or SetStateExit(...).",
        ]
        if warnings
        else [],
    }


def _last_name_segment(full_name: str) -> str:
    raw = (full_name or "").strip().strip("'\"")
    if not raw:
        return ""
    return raw.split(".")[-1].strip("'\"")


def _endpoint_aliases(full_name: str) -> set[str]:
    short_name = _last_name_segment(full_name)
    return {value for value in {full_name, short_name} if value}


def _analyze_activity_element_flow_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze activity element flow connectivity because the script has syntax errors: {exc}"],
            "activity_elements": [],
            "flow_edges": [],
            "under_connected_activity_elements": [],
        }

    activity_diagrams: set[str] = set()
    activity_element_names: set[str] = set()
    interface_like_names: set[str] = set()
    inserted_elements: list[dict] = []
    edges: list[dict] = []
    incoming: dict[str, int] = {}
    outgoing: dict[str, int] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewACTDiagram":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if diagram_name:
                activity_diagrams.add(diagram_name)
        elif name == "NewActivity":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                activity_element_names.add(full_name)
        elif name in _CONSTRAINT_INTERFACE_CREATION_CALLS:
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                interface_like_names.add(full_name)
        elif name == "InsertElementToDiagram":
            element_name = _literal_string(_get_call_arg(node, 0, "fullElementName"))
            diagram_name = _literal_string(_get_call_arg(node, 1, "fullDiagramName"))
            if element_name:
                inserted_elements.append(
                    {
                        "full_name": element_name,
                        "short_name": _last_name_segment(element_name),
                        "diagram_full_name": diagram_name,
                        "lineno": getattr(node, "lineno", None),
                    }
                )
        elif name in {
            "CreateActivityControlFlowLine",
            "CreateActivityObjectFlowLine",
            "CreateActivityControlFlowLineByGraphName",
            "CreateActivityObjectFlowLineByGraphName",
        }:
            start_name = _literal_string(_get_call_arg(node, 1, "startElementName" if "ByGraphName" not in name else "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endElementName" if "ByGraphName" not in name else "endGraphName"))
            if start_name and end_name:
                edges.append(
                    {
                        "start": start_name,
                        "end": end_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", None),
                    }
                )
                outgoing[start_name] = outgoing.get(start_name, 0) + 1
                incoming[end_name] = incoming.get(end_name, 0) + 1

    def _count_for(full_name: str, counts: dict[str, int]) -> int:
        return sum(counts.get(alias, 0) for alias in _endpoint_aliases(full_name))

    checked_elements = []
    for item in inserted_elements:
        full_name = item["full_name"]
        diagram_name = item["diagram_full_name"]
        is_activity = full_name in activity_element_names
        is_interface_like = full_name in interface_like_names
        is_known_activity_diagram = bool(diagram_name and diagram_name in activity_diagrams)
        if not (is_activity or is_interface_like or is_known_activity_diagram):
            continue
        in_count = _count_for(full_name, incoming)
        out_count = _count_for(full_name, outgoing)
        checked = dict(item)
        checked["incoming"] = in_count
        checked["outgoing"] = out_count
        checked["element_kind"] = "activity" if is_activity else "interface_or_parameter"
        checked_elements.append(checked)

    under_connected = [
        item
        for item in checked_elements
        if item["element_kind"] == "activity" and (item["incoming"] == 0 or item["outgoing"] == 0)
    ]
    if under_connected:
        warnings.append(
            "Some activity elements inserted into diagrams do not have both incoming and outgoing activity flows. Activities must not be used as the start or end of the activity diagram; use initial/final nodes for that."
        )

    return {
        "ok": True,
        "warnings": warnings,
        "activity_elements": checked_elements,
        "flow_edges": edges,
        "under_connected_activity_elements": under_connected,
        "next_recommended_actions": [
            "Connect every activity element with at least one incoming and one outgoing CreateActivityControlFlowLine/CreateActivityObjectFlowLine.",
            "If an activity exchanges data through an interface/port/parameter, connect it with an object flow; that still counts as activity connectivity.",
            "Use CreateActivityInitialNode/CreateActivityFinalNode for process start/end, not ordinary activity elements.",
        ]
        if warnings
        else [],
    }


def _extract_constraint_variables(expression: str) -> set[str]:
    candidates = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expression or ""))
    return {
        name
        for name in candidates
        if name not in _CONSTRAINT_EXPRESSION_RESERVED_WORDS
    }


def _extract_constraint_function_calls(expression: str) -> list[str]:
    calls = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", expression or "")
    return sorted({name for name in calls if name not in _CONSTRAINT_EXPRESSION_RESERVED_WORDS})


def _analyze_constraint_expression_interfaces(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze constraint expressions because the script has syntax errors: {exc}"],
            "created_interface_names": [],
            "constraint_expressions": [],
            "missing_interface_variables": [],
            "function_like_constraint_expressions": [],
        }

    events: list[dict] = []
    all_created_names: set[str] = set()
    expressions: list[dict] = []
    missing: list[dict] = []
    function_like: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in _CONSTRAINT_INTERFACE_CREATION_CALLS:
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            short_name = _last_name_segment(full_name)
            if short_name:
                all_created_names.add(short_name)
                events.append(
                    {
                        "kind": "create",
                        "name": short_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "SetConstraintExpression":
            target = _literal_string(_get_call_arg(node, 0, "fullName"))
            expression = _literal_string(_get_call_arg(node, 1, "expression"))
            variables = sorted(_extract_constraint_variables(expression))
            function_calls = _extract_constraint_function_calls(expression)
            event = {
                "kind": "expression",
                "target": target,
                "expression": expression,
                "variables": variables,
                "function_calls": function_calls,
                "lineno": getattr(node, "lineno", 0) or 0,
            }
            events.append(event)

    created_so_far: set[str] = set()
    for event in sorted(events, key=lambda item: item["lineno"]):
        if event["kind"] == "create":
            created_so_far.add(event["name"])
            continue

        variables = event["variables"]
        expressions.append(
            {
                "target": event["target"],
                "expression": event["expression"],
                "variables": variables,
                "function_calls": event["function_calls"],
                "lineno": event["lineno"],
            }
        )
        missing_vars = [variable for variable in variables if variable not in created_so_far]
        if missing_vars:
            missing.append(
                {
                    "target": event["target"],
                    "expression": event["expression"],
                    "missing_variables": missing_vars,
                    "lineno": event["lineno"],
                }
            )
        if event["function_calls"]:
            function_like.append(
                {
                    "target": event["target"],
                    "expression": event["expression"],
                    "function_calls": event["function_calls"],
                    "lineno": event["lineno"],
                }
            )

    if missing:
        warnings.append(
            "Constraint expressions reference variables before same-named interface/port/parameter elements are created in this script."
        )
    if function_like:
        warnings.append(
            "Constraint expressions should not contain function-like calls such as integral(...), derivative(...), limit(...), or custom helper names; keep them as direct algebraic/logical relations."
        )

    return {
        "ok": True,
        "warnings": warnings,
        "created_interface_names": sorted(all_created_names),
        "constraint_expressions": expressions,
        "missing_interface_variables": missing,
        "function_like_constraint_expressions": function_like,
        "next_recommended_actions": [
            "Before SetConstraintExpression(...), create same-named elements with NewInputParam/NewOutputParam/NewReturnParam or NewProxyPort/NewInputPort/NewOutputPort/NewValueProperty.",
            "Use expression variable names exactly matching the final name segment of the created interface/port/parameter.",
            "Rewrite function-like expressions into direct algebraic or logical relations before calling SetConstraintExpression(...).",
        ]
        if warnings
        else [],
    }


def _extract_activity_script_variables(script: str) -> set[str]:
    try:
        tree = ast.parse(script or "")
    except SyntaxError:
        candidates = set(re.findall(r"\b[^\W\d]\w*\b", script or "", flags=re.UNICODE))
        return {
            name
            for name in candidates
            if name.isidentifier() and name not in _ACTIVITY_SCRIPT_RESERVED_NAMES
        }

    variables: set[str] = set()

    class _NameVisitor(ast.NodeVisitor):
        def visit_Name(self, node: ast.Name) -> None:  # noqa: N802 - ast visitor name
            if node.id not in _ACTIVITY_SCRIPT_RESERVED_NAMES:
                variables.add(node.id)

    _NameVisitor().visit(tree)
    return variables


def _extract_activity_script_assignment_targets(script: str) -> set[str]:
    try:
        tree = ast.parse(script or "")
    except SyntaxError:
        return {
            match
            for match in re.findall(r"(?m)^\s*([^\W\d]\w*)\s*=", script or "", flags=re.UNICODE)
            if match.isidentifier() and match not in _ACTIVITY_SCRIPT_RESERVED_NAMES
        }

    assigned: set[str] = set()

    def _remember(target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            if target.id not in _ACTIVITY_SCRIPT_RESERVED_NAMES:
                assigned.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for item in target.elts:
                _remember(item)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                _remember(target)
        elif isinstance(node, ast.AnnAssign):
            _remember(node.target)
        elif isinstance(node, ast.AugAssign):
            _remember(node.target)
    return assigned


def _analyze_activity_script_interface_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze activity script variables because the script has syntax errors: {exc}"],
            "activity_scripts": [],
            "missing_own_interface_variables": [],
        }

    own_interface_names: dict[str, set[str]] = {}
    own_interfaces: dict[str, dict[str, dict]] = {}
    object_flow_edges: list[dict] = []
    scripts: list[dict] = []
    missing: list[dict] = []
    direct_activity_object_flows: list[dict] = []
    missing_variable_object_flows: list[dict] = []
    orphan_activity_interfaces: list[dict] = []
    unassigned_output_interfaces: list[dict] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name in _ACTIVITY_INTERFACE_CREATION_CALLS:
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if "." not in full_name:
                continue
            parent_name = ".".join(full_name.split(".")[:-1])
            short_name = _last_name_segment(full_name)
            if parent_name and short_name:
                own_interface_names.setdefault(parent_name, set()).add(short_name)
                own_interfaces.setdefault(parent_name, {})[short_name] = {
                    "full_name": full_name,
                    "api": name,
                    "lineno": getattr(node, "lineno", 0) or 0,
                }
        elif name == "CreateActivityObjectFlowLine":
            start_name = _literal_string(_get_call_arg(node, 1, "startElementName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endElementName"))
            if start_name and end_name:
                object_flow_edges.append(
                    {
                        "start": start_name,
                        "end": end_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "CreateActivityObjectFlowLineByGraphName":
            start_name = _literal_string(_get_call_arg(node, 1, "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endGraphName"))
            if start_name and end_name:
                object_flow_edges.append(
                    {
                        "start": start_name,
                        "end": end_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "SetActivityScript":
            target = _literal_string(_get_call_arg(node, 0, "fullName"))
            if not target:
                continue
            script = _literal_string(_get_call_arg(node, 1, "script"))
            variables = sorted(_extract_activity_script_variables(script))
            assigned_variables = sorted(_extract_activity_script_assignment_targets(script))
            own_names = sorted(own_interface_names.get(target, set()))
            missing_vars = [variable for variable in variables if variable not in own_interface_names.get(target, set())]
            item = {
                "target": target,
                "variables": variables,
                "assigned_variables": assigned_variables,
                "own_interface_names": own_names,
                "lineno": getattr(node, "lineno", 0) or 0,
            }
            scripts.append(item)
            if missing_vars:
                missing.append(
                    {
                        "target": target,
                        "missing_variables": missing_vars,
                        "own_interface_names": own_names,
                        "lineno": item["lineno"],
                    }
                )

    for script_item in scripts:
        target = script_item["target"]
        variables = script_item["variables"]
        assigned_variables = set(script_item["assigned_variables"])
        for edge in object_flow_edges:
            if target in _endpoint_aliases(edge["start"]) or target in _endpoint_aliases(edge["end"]):
                direct_activity_object_flows.append(
                    {
                        "target": target,
                        "edge": edge,
                        "lineno": edge["lineno"],
                    }
                )

        for variable in variables:
            interface_info = own_interfaces.get(target, {}).get(variable)
            if not interface_info:
                continue
            endpoint = interface_info["full_name"]
            api = interface_info["api"]
            if api in {"NewInputPort", "NewInputParam"}:
                connected = any(_endpoint_aliases(endpoint) & _endpoint_aliases(edge["end"]) for edge in object_flow_edges)
                expected = "incoming"
            elif api in {"NewOutputPort", "NewOutputParam", "NewReturnParam"}:
                connected = any(_endpoint_aliases(endpoint) & _endpoint_aliases(edge["start"]) for edge in object_flow_edges)
                expected = "outgoing"
            else:
                connected = any(
                    _endpoint_aliases(endpoint) & _endpoint_aliases(edge["start"])
                    or _endpoint_aliases(endpoint) & _endpoint_aliases(edge["end"])
                    for edge in object_flow_edges
                )
                expected = "incoming_or_outgoing"
            if not connected:
                missing_variable_object_flows.append(
                    {
                        "target": target,
                        "variable": variable,
                        "endpoint": endpoint,
                        "endpoint_api": api,
                        "expected_flow_direction": expected,
                        "lineno": script_item["lineno"],
                    }
                )

        for variable, interface_info in own_interfaces.get(target, {}).items():
            if interface_info["api"] not in {"NewOutputPort", "NewOutputParam", "NewReturnParam"}:
                continue
            if variable not in assigned_variables:
                unassigned_output_interfaces.append(
                    {
                        "target": target,
                        "variable": variable,
                        "endpoint": interface_info["full_name"],
                        "endpoint_api": interface_info["api"],
                        "lineno": script_item["lineno"],
                    }
                )

    for parent_name, interfaces in own_interfaces.items():
        for short_name, interface_info in interfaces.items():
            endpoint = interface_info["full_name"]
            connected = any(
                _endpoint_aliases(endpoint) & _endpoint_aliases(edge["start"])
                or _endpoint_aliases(endpoint) & _endpoint_aliases(edge["end"])
                for edge in object_flow_edges
            )
            if not connected:
                orphan_activity_interfaces.append(
                    {
                        "target": parent_name,
                        "variable": short_name,
                        "endpoint": endpoint,
                        "endpoint_api": interface_info["api"],
                        "lineno": interface_info["lineno"],
                    }
                )

    if missing:
        warnings.append(
            "Activity scripts reference variables that are not same-named interfaces/ports/parameters owned by that activity."
        )
    if direct_activity_object_flows:
        warnings.append(
            "A scripted activity is using direct object-flow endpoints. If you also model ports for that activity, those ports must be created under the activity element itself and connected explicitly; do not place ports directly on the activity diagram."
        )
    if missing_variable_object_flows:
        warnings.append(
            "Some activity script variables have same-named ports/parameters but no explicit object flow endpoint using those ports/parameters."
        )
    if orphan_activity_interfaces:
        warnings.append(
            "Some activity-owned interfaces/ports/parameters are created but never connected by object flow. Keep ports under the activity element itself and connect them explicitly; do not create ports on the activity diagram."
        )
    if unassigned_output_interfaces:
        warnings.append(
            "Some activity output interfaces/ports/parameters are created but their same-named values are never assigned in the parent activity script."
        )

    return {
        "ok": True,
        "warnings": warnings,
        "activity_scripts": scripts,
        "missing_own_interface_variables": missing,
        "direct_activity_object_flows": direct_activity_object_flows,
        "missing_variable_object_flows": missing_variable_object_flows,
        "orphan_activity_interfaces": orphan_activity_interfaces,
        "unassigned_output_interfaces": unassigned_output_interfaces,
        "next_recommended_actions": [
            "If a script variable truly needs a modeled port, create the same-named NewInputPort/NewOutputPort under the activity element itself, not on the activity diagram.",
            "Keep activity script variables local to the activity's own input/output port names.",
            "If ports are used, pass scripted activity data with explicit object flows between corresponding ports, for example source.port -> scriptedActivity.port.",
            "Avoid creating spare activity ports; every added input/output port should participate in an object flow.",
            "When an activity creates an output port, assign that same-named variable in SetActivityScript(...), for example `out1 = 1` or `mode = sensor_value`.",
        ]
        if warnings
        else [],
    }


def _extract_guard_variables(guard_text: str) -> set[str]:
    raw = (guard_text or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1].strip()
    return {
        name
        for name in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", raw)
        if name not in {"and", "or", "not", "True", "False"}
    }


def _analyze_activity_decision_dataflow_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze activity decision dataflow because the script has syntax errors: {exc}"],
            "bad_decision_nodes": [],
        }

    activity_names: set[str] = set()
    inserted_activities_by_diagram: dict[str, dict[str, str]] = {}
    decision_nodes: dict[tuple[str, str], dict] = {}
    incoming_object_flows: dict[tuple[str, str], list[dict]] = {}
    full_name_object_flows: list[dict] = []
    outgoing_control_flows: dict[tuple[str, str], list[dict]] = {}
    script_assignments: dict[str, set[str]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewActivity":
            full_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if full_name:
                activity_names.add(full_name)
        elif name == "InsertElementToDiagram":
            element_name = _literal_string(_get_call_arg(node, 0, "fullElementName"))
            diagram_name = _literal_string(_get_call_arg(node, 1, "fullDiagramName"))
            if diagram_name and element_name and element_name in activity_names:
                inserted_activities_by_diagram.setdefault(diagram_name, {})[_last_name_segment(element_name)] = element_name
        elif name == "CreateActivityDecisionNode":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            graph_name = _literal_string(_get_call_arg(node, 1, "graphName"))
            if diagram_name and graph_name:
                decision_nodes[(diagram_name, graph_name)] = {
                    "diagram": diagram_name,
                    "graph_name": graph_name,
                    "lineno": getattr(node, "lineno", 0) or 0,
                }
        elif name == "CreateActivityObjectFlowLineByGraphName":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endGraphName"))
            if diagram_name and start_name and end_name:
                incoming_object_flows.setdefault((diagram_name, end_name), []).append(
                    {
                        "diagram": diagram_name,
                        "start_graph_name": start_name,
                        "end_graph_name": end_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "CreateActivityObjectFlowLine":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startElementName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endElementName"))
            if diagram_name and start_name and end_name:
                full_name_object_flows.append(
                    {
                        "diagram": diagram_name,
                        "start_graph_name": start_name,
                        "end_graph_name": end_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "CreateActivityControlFlowLineByGraphName":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startGraphName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endGraphName"))
            line_name = _literal_string(_get_call_arg(node, 3, "lineName"))
            if diagram_name and start_name and end_name:
                outgoing_control_flows.setdefault((diagram_name, start_name), []).append(
                    {
                        "diagram": diagram_name,
                        "start_graph_name": start_name,
                        "end_graph_name": end_name,
                        "line_name": line_name,
                        "api": name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "SetActivityScript":
            target = _literal_string(_get_call_arg(node, 0, "fullName"))
            script = _literal_string(_get_call_arg(node, 1, "script"))
            if target:
                script_assignments[target] = _extract_activity_script_assignment_targets(script)

    for edge in full_name_object_flows:
        for decision_key in decision_nodes:
            if decision_key[0] != edge["diagram"]:
                continue
            if decision_key[1] in _endpoint_aliases(edge["end_graph_name"]):
                incoming_object_flows.setdefault(decision_key, []).append(edge)

    bad_decision_nodes: list[dict] = []
    for key, item in decision_nodes.items():
        diagram_name, graph_name = key
        incoming_edges = incoming_object_flows.get(key, [])
        outgoing_edges = outgoing_control_flows.get(key, [])
        guard_variables = set()
        for edge in outgoing_edges:
            guard_variables.update(_extract_guard_variables(edge.get("line_name", "")))

        start_activity_full_name = ""
        for edge in incoming_edges:
            start_graph_name = edge["start_graph_name"]
            candidate = inserted_activities_by_diagram.get(diagram_name, {}).get(start_graph_name, "")
            if not candidate and "." in start_graph_name:
                parent_name = ".".join(start_graph_name.split(".")[:-1])
                if parent_name in activity_names:
                    candidate = parent_name
            if candidate:
                start_activity_full_name = candidate
                break

        issues = []
        if not incoming_edges:
            issues.append("missing_incoming_object_flow")
        if incoming_edges and not start_activity_full_name:
            issues.append("incoming_object_flow_source_is_not_a_resolved_activity")
        if start_activity_full_name and guard_variables:
            assigned = script_assignments.get(start_activity_full_name, set())
            if not (assigned & guard_variables):
                issues.append("upstream_activity_script_does_not_assign_guard_variable")
        elif start_activity_full_name and not script_assignments.get(start_activity_full_name):
            issues.append("upstream_activity_missing_script_assignment")

        if issues:
            bad_decision_nodes.append(
                {
                    **item,
                    "issues": issues,
                    "incoming_object_flows": incoming_edges,
                    "outgoing_control_flows": outgoing_edges,
                    "guard_variables": sorted(guard_variables),
                    "resolved_start_activity": start_activity_full_name,
                    "assigned_variables": sorted(script_assignments.get(start_activity_full_name, set())),
                }
            )

    if bad_decision_nodes:
        warnings.append(
            "Activity decision/choice nodes should be preceded by an activity, connected with an object flow, and the upstream activity script should assign the guard-related output value."
        )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "bad_decision_nodes": bad_decision_nodes,
        "next_recommended_actions": [
            "Prefer CreateActivityObjectFlowLine(...) with full element names. Use `element.port` endpoints only when you intentionally model ports under the activity element itself.",
            "Before each activity decision node, insert an upstream activity and connect it to the decision node with an object flow.",
            "Set an upstream activity script that assigns the output used by the decision guard, for example `out = 1` or `out = input_value / 2`.",
            "Write the outgoing guard using that modeled variable name, for example `[out == 1]`.",
            "Do not try to create or place ports directly on the activity diagram. If ports are needed, create them under the activity element itself.",
        ]
        if warnings
        else [],
    }


def _analyze_ibd_connector_usage(source: str) -> dict:
    warnings = []
    try:
        tree = ast.parse(source or "")
    except SyntaxError as exc:
        return {
            "ok": False,
            "warnings": [f"Could not analyze IBD connector usage because the script has syntax errors: {exc}"],
            "ibd_diagrams": [],
            "bad_connector_calls": [],
        }

    ibd_diagrams: dict[str, dict] = {}
    bad_connector_calls: list[dict] = []

    def _diagram_item(diagram_name: str) -> dict:
        return ibd_diagrams.setdefault(
            diagram_name,
            {
                "diagram": diagram_name,
                "inserted_elements": [],
                "connector_calls": [],
                "missing_inserted_parts": [],
            },
        )

    def _part_qualifier(endpoint: str) -> str:
        raw = (endpoint or "").strip().strip("'\"")
        if "." not in raw:
            return ""
        return raw.rsplit(".", 1)[0]

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        if name == "NewIBDDiagram":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullName"))
            if diagram_name:
                _diagram_item(diagram_name)
        elif name == "InsertElementToDiagram":
            element_name = _literal_string(_get_call_arg(node, 0, "fullElementName"))
            diagram_name = _literal_string(_get_call_arg(node, 1, "fullDiagramName"))
            if diagram_name and element_name:
                _diagram_item(diagram_name)["inserted_elements"].append(
                    {
                        "full_name": element_name,
                        "short_name": _last_name_segment(element_name),
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )
        elif name == "CreateConnectorLine":
            diagram_name = _literal_string(_get_call_arg(node, 0, "fullDiagramName"))
            start_name = _literal_string(_get_call_arg(node, 1, "startElementName"))
            end_name = _literal_string(_get_call_arg(node, 2, "endElementName"))
            if diagram_name:
                _diagram_item(diagram_name)["connector_calls"].append(
                    {
                        "diagram": diagram_name,
                        "start_element_name": start_name,
                        "end_element_name": end_name,
                        "lineno": getattr(node, "lineno", 0) or 0,
                    }
                )

    for diagram_name, item in ibd_diagrams.items():
        inserted_aliases = set()
        for inserted in item["inserted_elements"]:
            inserted_aliases.update(_endpoint_aliases(inserted["full_name"]))
        for call in item["connector_calls"]:
            missing_parts = []
            for endpoint in (call["start_element_name"], call["end_element_name"]):
                qualifier = _part_qualifier(endpoint)
                if qualifier and qualifier not in inserted_aliases and _last_name_segment(qualifier) not in inserted_aliases:
                    missing_parts.append(qualifier)
            if missing_parts:
                bad = {
                    **call,
                    "problem": "connector_part_not_inserted_into_ibd",
                    "missing_parts": sorted(set(missing_parts)),
                    "inserted_elements": sorted(inserted_aliases),
                }
                item["missing_inserted_parts"].append(bad)
                bad_connector_calls.append(bad)

    if bad_connector_calls:
        warnings.append(
            "Some IBD connector endpoints reference part-qualified ports whose owning part properties were not inserted into the same IBD before CreateConnectorLine(...). Insert the parts first with InsertElementToDiagram(...)."
        )

    return {
        "ok": not warnings,
        "warnings": warnings,
        "ibd_diagrams": list(ibd_diagrams.values()),
        "bad_connector_calls": bad_connector_calls,
        "next_recommended_actions": [
            "Before CreateConnectorLine(...), insert every referenced part property / component instance into the same IBD with InsertElementToDiagram(...).",
            "If a connector endpoint is written as `partA.port1`, make sure `partA` is already present in that IBD.",
        ]
        if warnings
        else [],
    }


_DESTRUCTIVE_SCRIPT_PATTERN = re.compile(
    r"\b(?:Delete|Remove|Overwrite|Clear|Close|Reset|Exit)[A-Za-z0-9_]*\s*\(|\b(?:unlink|rmdir|remove|removedirs)\s*\(",
    re.IGNORECASE,
)


def classify_script_risk(source: str) -> str:
    """Classify an executable modeling script for host confirmation UX."""
    return "destructive" if _DESTRUCTIVE_SCRIPT_PATTERN.search(source or "") else "write"


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
    meta={"sysbuilder": {"risk": "write", "dynamicRiskField": "risk"}},
)
def run_script(
    python_source: str = "",
    script_path: str = "",
    script_name: str = "sysbuilder_modeling_script.py",
    working_directory: str = "",
    auto_save_script: bool = True,
    strict_api_precheck: bool = True,
    process_path: str = "",
    ip: str = "",
    port: int = 0,
) -> str:
    """
    执行 Sysbuilder 建模 Python 脚本。

    使用要求：
    - 本工具只负责执行现成的建模脚本。
    - AI 客户端在需要建模时，应先自动生成完整的 Python 建模脚本，再调用本工具执行。
    - 跨需求指标、活动接口、块值属性和约束参数传值时，先调用 CreateRelationMapping(...) 建立源到目标映射，再调用 CalculateParametricDiagram(...)，并检查结果 JSON 中的数值、约束满足状态和错误信息。
    - 完整 SysML 建模脚本通常应包含追溯关系：需求应通过 satisfy 连接到满足它的活动/功能/结构元素，功能或活动应通过 allocate 分配到结构块。
    - 若只需补建追溯关系，优先使用高层工具 `create_satisfy_trace` 和 `create_allocate_trace`，它们会自动插入两端元素、创建连线并布局。
    - 活动图中的逻辑节点（初始、结束、决策、合并、分叉、汇合、事件、信号、时间事件）必须使用 graphName 连线，避免生成无连线孤立节点。
    - 状态机图不应只生成线性骨架；应包含多个稳定状态、选择分支、并发/复合结构、迁移和状态行为。
    - 自动创建的状态机图块必须使用 CreateStateTransitionLineByGraphName(...) 按 graphName 连线，不要失败后改用完整元素名猜测。
    - 脚本执行前会预检导入与 API 名称：禁止 `mworks` 导入，禁止调用未公开的 Sysbuilder API；不确定时先查 quickref 或 `sysbuilder_mcp_server.core`。
    - 约束表达式中的变量必须对应已创建的同名接口/端口/参数；使用变量前先创建对应名字的模型元素。
    - 活动脚本中的变量只能使用该活动自己的接口名、输入/输出端口名或输入/输出参数名；脚本相关数据对象流必须显式连接对应端口/参数，不要直接连到活动本身。
    - 所有执行脚本都会以 UTF-8 保存后再运行。
    - 运行时会自动注入建模规范上下文，可直接使用 `MODELING_RULES`、
      `GetModelingRuleText()`、`PrintModelingRuleSummary()` 读取规则，并使用 `OUTPUT_ROOT`
      获取中间数据根目录。

    入参说明：
    - `python_source`：待执行的完整 Python 建模脚本。
    - `script_path`：已有脚本路径；当 `python_source` 为空时读取这个文件执行。
    - `script_name`：未指定 `script_path` 时，落盘脚本文件名。
    - `working_directory`：脚本执行目录；默认是 MCP 中间数据根目录（用户目录下的 `Sysbuilder/SysMLAIOutput`）。
    """
    source = (python_source or "").strip()
    incoming_script_path = (script_path or "").strip()
    if not source and not incoming_script_path:
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "python_source and script_path cannot both be empty.",
                "hint": "请先由 AI 客户端生成 Python 建模脚本，再通过 python_source 或 script_path 调用本工具。",
            }
        )

    saved_path = ""
    if source:
        source = ensure_utf8_script_text(source)
    else:
        existing_path = Path(incoming_script_path).expanduser()
        if not existing_path.is_absolute():
            existing_path = (get_workspace_root() / existing_path).resolve()
        if not existing_path.is_file():
            return _json(
                {
                    "ok": False,
                    "tool": "run_script",
                    "error": f"script_path is not a file: {existing_path}",
                }
            )
        source = existing_path.read_text(encoding="utf-8")
        saved_path = str(existing_path)

    api_preflight = _preflight_sysbuilder_api_usage(source)
    if strict_api_precheck and not api_preflight.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "Sysbuilder API preflight failed.",
                "api_preflight": api_preflight,
                "hint": "Fix imports/API names before execution. In MCP run_script, use direct injected APIs or `from sysbuilder_mcp_server.core import *`.",
            }
        )

    state_transition_usage_analysis = _analyze_state_transition_usage(source)
    if strict_api_precheck and state_transition_usage_analysis.get("warnings"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "State transition preflight failed.",
                "state_transition_usage_analysis": state_transition_usage_analysis,
                "hint": "Create explicit graphName values for state-machine control nodes, use explicit boolean transition conditions, create referenced variables as value properties under the state machine, and allow at most one unconditional outgoing transition per node.",
            }
        )

    state_machine_behavior_element_analysis = _analyze_state_machine_behavior_element_usage(source)
    if strict_api_precheck and state_machine_behavior_element_analysis.get("warnings"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "State-machine behavior preflight failed.",
                "state_machine_behavior_element_analysis": state_machine_behavior_element_analysis,
                "hint": "Do not create activities directly under a state machine. Create state-local actions with NewOpaqueBehavior(...) and bind them with SetStateEntry/SetStateDoActivity/SetStateExit(...).",
            }
        )

    ibd_connector_usage_analysis = _analyze_ibd_connector_usage(source)
    if strict_api_precheck and ibd_connector_usage_analysis.get("warnings"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "IBD connector preflight failed.",
                "ibd_connector_usage_analysis": ibd_connector_usage_analysis,
                "hint": "Insert the owning part properties / component instances into the same IBD with InsertElementToDiagram(...) before calling CreateConnectorLine(...).",
            }
        )

    activity_logic_node_analysis = _analyze_activity_logic_node_usage(source)
    activity_element_flow_analysis = _analyze_activity_element_flow_usage(source)
    activity_script_interface_analysis = _analyze_activity_script_interface_usage(source)
    activity_decision_dataflow_analysis = _analyze_activity_decision_dataflow_usage(source)
    if strict_api_precheck and (
        activity_logic_node_analysis.get("decision_nodes_with_multiple_incoming")
        or activity_logic_node_analysis.get("decision_control_flows_missing_guard")
        or activity_decision_dataflow_analysis.get("warnings")
        or activity_script_interface_analysis.get("orphan_activity_interfaces")
        or activity_script_interface_analysis.get("unassigned_output_interfaces")
    ):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "Activity diagram preflight failed.",
                "activity_logic_node_analysis": activity_logic_node_analysis,
                "activity_element_flow_analysis": activity_element_flow_analysis,
                "activity_script_interface_analysis": activity_script_interface_analysis,
                "activity_decision_dataflow_analysis": activity_decision_dataflow_analysis,
                "hint": "Keep activity interfaces connected by object flow, place an activity before each decision node, connect that activity to the decision with an object flow, and assign the decision variable in the upstream activity script.",
            }
        )

    session = ensure_sysbuilder_session(process_path=process_path, ip=ip, port=(port or None))
    if not session.get("ok"):
        return _json(
            {
                "ok": False,
                "tool": "run_script",
                "error": "Failed to start or connect Sysbuilder.",
                "api_preflight": api_preflight,
                "session": session,
            }
        )

    if source and not saved_path:
        if auto_save_script or not incoming_script_path:
            target_path = resolve_output_path(incoming_script_path, default_name=script_name)
            target_path.write_text(source, encoding="utf-8")
            saved_path = str(target_path)
        filename = saved_path or "<run_script>"
    else:
        filename = saved_path or "<run_script>"

    wd = Path(working_directory).expanduser() if working_directory else get_output_root()
    if not wd.is_absolute():
        wd = (get_workspace_root() / wd).resolve()
    wd.mkdir(parents=True, exist_ok=True)

    result = execute_python_source(source=source, filename=filename, working_directory=wd)
    result.update(
        {
            "tool": "run_script",
            "risk": classify_script_risk(source),
            "script_path": saved_path,
            "working_directory": str(wd),
            "session": session,
            "api_preflight": api_preflight,
            "traceability_analysis": _analyze_traceability_usage(source),
            "parametric_verification_analysis": _analyze_parametric_verification_usage(source),
            "activity_logic_node_analysis": activity_logic_node_analysis,
            "state_machine_complexity_analysis": _analyze_state_machine_complexity(source),
            "state_transition_usage_analysis": state_transition_usage_analysis,
            "state_machine_behavior_element_analysis": state_machine_behavior_element_analysis,
            "ibd_connector_usage_analysis": ibd_connector_usage_analysis,
            "activity_element_flow_analysis": activity_element_flow_analysis,
            "constraint_expression_analysis": _analyze_constraint_expression_interfaces(source),
            "activity_script_interface_analysis": activity_script_interface_analysis,
            "activity_decision_dataflow_analysis": activity_decision_dataflow_analysis,
            "modeling_rules": get_runtime_modeling_rules_metadata(),
        }
    )
    return _json(result)
