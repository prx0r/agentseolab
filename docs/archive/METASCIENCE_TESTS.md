# Metascience Tests — Does the Experiment Measure What We Think?

## The Distinction

**Unit tests** verify the machinery runs.
**Metascience tests** verify the machinery measures what you think it measures.

A unit test says "the function returned 200."
A metascience test says "a deliberately bad agent fails, a good agent passes,
and changing one variable changes only the expected outcome."

Without metascience tests, you can have 100% passing unit tests while your
experiment silently produces convincing garbage. That is worse than crashing.

## Required Metascience Properties

1. **Negative control**: A deliberately wrong agent MUST fail.
   If it passes, your scorer is broken.

2. **Positive control**: A correct agent MUST pass.
   If it fails, your verifier is too strict or your tools are broken.

3. **Parameter sensitivity**: Right tool + wrong params MUST fail.
   If it passes, you're not actually testing parameter construction.

4. **Deterministic replay**: Same seed → byte-identical trial sequence.
   If not, your randomization isn't controlled.

5. **Isolation**: Changing ONE treatment dimension leaves all other
   manifest fields byte-identical. If not, variables are confounded.

6. **Discrimination**: The experiment CAN distinguish good from bad.
   Report the minimum detectable effect size at current n and α.

7. **No false positives from unparseable output**: UNPARSEABLE ≠ WRONG.
   These must be counted separately and never conflated.
EOF