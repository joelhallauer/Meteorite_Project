def format_mass(m: float) -> str:
    if m < 1_000:      return f"{m:.2f} g"
    if m < 1_000_000:  return f"{m/1_000:.2f} kg"
    return f"{m/1_000_000:.2f} t"

def format_mass_int(m: float) -> str:
    if m < 1:          return f"{m:.1f} g"
    if m < 1_000:      return f"{int(round(m))} g"
    if m < 1_000_000:  return f"{int(round(m/1_000))} kg"
    return f"{int(round(m/1_000_000))} t"
