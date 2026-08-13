"""
Safe mathematical evaluation tool using Python AST module.
"""

from __future__ import annotations

import ast
import math
import operator

from utils.logger import logger


class SafeCalculator:
    """
    Evaluates mathematical expressions safely without python eval().
    """

    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }

    UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    ALLOWED_FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "round": round,
    }

    ALLOWED_CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def _eval_node(self, node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.Name):
            if node.id in self.ALLOWED_CONSTANTS:
                return self.ALLOWED_CONSTANTS[node.id]
            raise ValueError(f"Unsupported variable or constant: '{node.id}'")

        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in self.UNARY_OPERATORS:
                operand = self._eval_node(node.operand)
                return self.UNARY_OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in self.OPERATORS:
                left = self._eval_node(node.left)
                right = self._eval_node(node.right)
                return self.OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self.ALLOWED_FUNCTIONS:
                func = self.ALLOWED_FUNCTIONS[node.func.id]
                args = [self._eval_node(arg) for arg in node.args]
                return func(*args)
            raise ValueError("Function call not allowed or unknown function.")

        else:
            raise ValueError(f"Unsupported syntax: {type(node).__name__}")

    def calculate(self, expression: str) -> str:
        """
        Safely parse and evaluate a mathematical expression string.
        """
        try:
            cleaned = expression.replace("^", "**").strip()
            parsed = ast.parse(cleaned, mode="eval")
            result = self._eval_node(parsed)
            return str(result)
        except ZeroDivisionError:
            return "Error: Division by zero."
        except Exception as exc:
            logger.warning("Calculator evaluation error for '%s': %s", expression, exc)
            return f"Error evaluating expression: {exc}"


def calculate(expression: str) -> str:
    """
    Standalone wrapper function for tool execution.
    """
    calculator = SafeCalculator()
    return calculator.calculate(expression)