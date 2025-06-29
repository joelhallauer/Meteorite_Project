# Formatierer für die Masse
def format_mass(mass: float) -> str:
    if mass < 1_000:               # < 1 kg
        return f"{mass:.2f} g"
    elif mass < 1_000_000:         # < 1 t
        return f"{mass/1_000:.2f} kg"
    else:
        return f"{mass/1_000_000:.2f} t"

def format_mass_int(mass: float) -> str:
    """Massen schön ohne Nachkommastellen (außer < 1 g) formatieren."""
    if mass < 1:                     # 0,1 g usw. soll eine Nachkomma behalten
        return f"{mass:.1f} g"
    if mass < 1_000:
        return f"{int(round(mass))} g"
    if mass < 1_000_000:
        return f"{int(round(mass/1_000))} kg"
    return f"{int(round(mass/1_000_000))} t"
