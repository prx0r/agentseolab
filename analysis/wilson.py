"""Wilson score interval — canonical closed form (bounds within [0,1]).
Verified against statsmodels proportion_confint(method='wilson')."""
import math

def wilson(k, n, z=1.96):
    if n == 0: return None
    center = (k + z*z/2) / (n + z*z)
    half = (z / (n + z*z)) * math.sqrt(k*(n-k)/n + z*z/4)
    lo, hi = max(0.0, center - half), min(1.0, center + half)
    return {"p": round(k/n, 3), "ci95": [round(lo, 3), round(hi, 3)], "n": n,
            "excludes_0.5": lo > 0.5 or hi < 0.5}
