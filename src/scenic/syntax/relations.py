
"""Extracting relations (for later pruning) from the syntax of requirements"""

import math
from collections import defaultdict
from ast import Compare, BinOp, Eq, NotEq, Lt, LtE, Gt, GtE, Call, Add, Sub, Expression, Name

from scenic.core.distributions import needsSampling
from scenic.core.object_types import Point, Object

def inferRelationsFrom(reqNode, namespace, ego, line):
    matcher = RequirementMatcher(namespace)
    # Check for relative heading bounds
    rhMatcher = lambda node: matcher.matchUnaryFunction('RelativeHeading', node)
    allBounds = matcher.matchBounds(reqNode, rhMatcher)
    for target, bounds in allBounds.items():
        if not isinstance(target, Object):
            continue
        if ego is None:
            raise InvalidScenarioError(f'relative heading w.r.t. unassigned ego on line {line}')
        lower, upper = bounds
        if lower < -math.pi:
            lower = -math.pi
        if upper > math.pi:
            upper = math.pi
        if lower == -math.pi and upper == math.pi:
            continue    # skip trivial bounds
        rel = RelativeHeadingRelation(target, lower, upper)
        ego._relations.append(rel)
        conv = RelativeHeadingRelation(ego, -upper, -lower)
        target._relations.append(conv)

class RelativeHeadingRelation:
    def __init__(self, target, lower, upper):
        self.target = target
        self.lower, self.upper = lower, upper

class RequirementMatcher:
    def __init__(self, namespace):
        self.namespace = namespace

    def matchUnaryFunction(self, name, node):
        if not (isinstance(node, Call) and isinstance(node.func, Name)
                and node.func.id == name):
            return None
        if len(node.args) != 1:
            return None
        if len(node.keywords) != 0:
            return None
        return self.matchValue(node.args[0])

    def matchBounds(self, node, matchAtom):
        if not isinstance(node, Compare):
            return {}
        bounds = defaultdict(lambda: (float('-inf'), float('inf')))
        first = node.left
        for second, op in zip(node.comparators, node.ops):
            lower, upper, target = self.matchBoundsInner(first, second, op, matchAtom)
            first = second
            if target is None:
                continue
            bestLower, bestUpper = bounds[target]
            if lower is not None and lower > bestLower:
                bestLower = lower
            if upper is not None and upper < bestUpper:
                bestUpper = upper
            bounds[target] = (bestLower, bestUpper)
        return bounds

    def matchBoundsInner(self, left, right, op, matchAtom):
        # Reduce > and >= to < and <=
        if isinstance(op, Gt):
            return self.matchBoundsInner(right, left, Lt(), matchAtom)
        elif isinstance(op, GtE):
            return self.matchBoundsInner(right, left, LtE(), matchAtom)
        # Try matching a constant lower bound on the atom or its absolute value
        lconst = self.matchConstant(left)
        if isinstance(lconst, (int, float)):
            target = matchAtom(right)
            if target is not None:     # CONST op QUANTITY
                return (lconst, lconst, target) if isinstance(op, Eq) else (lconst, None, target)
            else:
                bounds = self.matchAbsBounds(right, lconst, op, False, matchAtom)
                if bounds is not None:      # CONST op abs(QUANTITY [+/- CONST])
                    return bounds
        # Try matching a constant upper bound on the atom or its absolute value
        rconst = self.matchConstant(right)
        if isinstance(rconst, (int, float)):
            target = matchAtom(left)
            if target is not None:      # QUANTITY op CONST
                return (rconst, rconst, target) if isinstance(op, Eq) else (None, rconst, target)
            else:
                bounds = self.matchAbsBounds(left, rconst, op, True, matchAtom)
                if bounds is not None:      # abs(QUANTITY [+/- CONST]) op CONST
                    return bounds
        return None, None, None

    def matchAbsBounds(self, node, const, op, isUpperBound, matchAtom):
        if not (isinstance(node, Call) and isinstance(node.func, Name)
                and node.func.id == 'abs'):
            return None     # not an invocation of abs
        if not isUpperBound and not isinstance(op, Eq):
            return None     # lower bounds on abs value don't bound underlying quantity
        if const < 0:
            raise RuntimeError('inconsistent require statement')    # TODO improve
        assert len(node.args) == 1
        arg = node.args[0]
        target = matchAtom(arg)
        if target is not None:   # abs(QUANTITY) </= CONST
            return (-const, const, target)
        elif isinstance(arg, BinOp) and isinstance(arg.op, (Add, Sub)):   # abs(X +/- Y) </= CONST
            match = None
            slconst = self.matchConstant(arg.left)
            target = matchAtom(arg.right)
            if (isinstance(slconst, (int, float))
                and target is not None):   # abs(CONST +/- QUANTITY) </= CONST
                match = slconst
            else:
                srconst = self.matchConstant(arg.right)
                target = matchAtom(arg.left)
                if (isinstance(srconst, (int, float))
                    and target is not None):    # abs(QUANTITY +/- CONST) </= CONST
                    match = srconst
            if match is not None:
                if isinstance(arg.op, Add):    # abs(QUANTITY + CONST) </= CONST
                    return (-const - match, const - match, target)
                else:   # abs(QUANTITY - CONST) </= CONST
                    return (-const + match, const + match, target)
        return None

    def matchConstant(self, node):
        value = self.matchValue(node)
        return None if needsSampling(value) else value

    def matchValue(self, node):
        # This method could have undesirable side-effects, but conditions in
        # requirements should not have side-effects to begin with
        try:
            code = compile(Expression(node), '<internal>', 'eval')
            value = eval(code, dict(self.namespace))
        except Exception:
            return None
        return value
