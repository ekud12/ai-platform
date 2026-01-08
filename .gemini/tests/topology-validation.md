# Topology Validation Tests

## Purpose

This file defines topology conflict detection rules.

## Authority

Topology must pass all validation before operation.

## Scope

All topology structure validation.

## Constraints

- All tests must pass
- Validation runs at startup
- Violations block operation

## Validation Tests

### Acyclicity Test

```
TEST: GraphIsAcyclic
METHOD: Topological sort on authority edges
EXPECT: Sort completes without cycle detection
FAIL: Report cycle members
```

### Single Ownership Test

```
TEST: NoSharedOwnership
METHOD: Check ownership map for duplicates
EXPECT: Each concern maps to exactly one owner
FAIL: Report multiply-owned concerns
```

### Node Validity Test

```
TEST: AllNodesValid
METHOD: Verify all node files exist
EXPECT: All paths resolve to files
FAIL: Report missing files
```

### Edge Validity Test

```
TEST: AllEdgesValid
METHOD: Verify all edge endpoints exist
EXPECT: Both from and to nodes exist
FAIL: Report invalid edges
```

### Forbidden Edge Test

```
TEST: NoForbiddenEdges
METHOD: Check allowed edges against forbidden list
EXPECT: No forbidden edges present
FAIL: Report forbidden edges found
```

### Reachability Test

```
TEST: HumanReachable
METHOD: BFS from each node to Human
EXPECT: Path exists from every node
FAIL: Report unreachable nodes
```

### Completeness Test

```
TEST: AllConcernsCovered
METHOD: Compare concern list to ownership map
EXPECT: Every concern has owner
FAIL: Report orphaned concerns
```

## Validation Report

```markdown
# Graph Validation Report

## Test Results

| Test | Result | Details |
|------|--------|---------|
| GraphIsAcyclic | PASS/FAIL | [cycle info] |
| NoSharedOwnership | PASS/FAIL | [conflicts] |
| AllNodesValid | PASS/FAIL | [missing] |
| AllEdgesValid | PASS/FAIL | [invalid] |
| NoForbiddenEdges | PASS/FAIL | [violations] |
| HumanReachable | PASS/FAIL | [unreachable] |
| AllConcernsCovered | PASS/FAIL | [orphans] |

## Overall: PASS/FAIL
```
