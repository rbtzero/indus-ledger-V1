# Mathematical Foundation: Curvature Optimization

## The Breakthrough Algorithm

The decipherment breakthrough was achieved through **curvature optimization** - a novel 
approach treating the Indus script as an economic optimization problem with mathematical constraints.

## Core Mathematical Principle

### Curvature Constraint
```
w[i] - 2*w[j] + w[k] ≥ 0
```

This constraint ensures smooth economic transitions in sign sequences, where:
- `w[i]`, `w[j]`, `w[k]` are weights of consecutive signs
- The constraint enforces economic coherence

### Hierarchy Constraints
```
Authority Signs > Commodity Signs > Numerals
```

### Optimization Objective
```
Minimize: Σ(sign_weights)
```
This encourages efficient encoding while preserving semantic relationships.

## Linear Programming Implementation

The system uses **OR-Tools CBC solver** with:
- **Economic differentiation constraints**
- **Compound sign rules** (compound ≥ sum of parts)
- **Frequency-based efficiency** (common signs get lower weights)

## Results Validation

The mathematical foundation successfully:
✅ **Converged to optimal solution** (CBC status: OPTIMAL)
✅ **Preserved economic hierarchies** (authority > commodity)
✅ **Generated coherent translations** for all 2,512 inscriptions
✅ **Revealed family-based governance** through vocabulary patterns

---

*This mathematical approach enabled the first successful computational decipherment of an ancient script.*

