import datetime

def normalize_plant_location(loc):
    """
    Standardizes plant location strings to DB format: Title_Case_Suffix
    Examples: 
      'pune cv' -> 'Pune_CV'
      'Pune CV' -> 'Pune_CV'
      'Sanand PV 1' -> 'Sanand_PV1'
    """
    if not loc:
        return None
    
    loc = str(loc).strip()
    
    # If it already has underscores, assume it's close to correct format, just clean it
    if '_' in loc:
        parts = loc.split('_')
        new_parts = []
        for p in parts:
            p = p.strip()
            if p.upper() in ['CV', 'PV']:
                new_parts.append(p.upper())
            elif p.upper().startswith('PV') and len(p) > 2: # Handle PV1, PV2
                 new_parts.append(p.upper())
            else:
                new_parts.append(p.capitalize())
        return '_'.join(new_parts)

    # Otherwise, handle space separation (e.g. "Pune CV", "Sanand PV 1")
    parts = loc.split()
    if not parts:
        return None
    
    new_parts = []
    
    # Simple state machine to handle City, Type, and Suffix Number
    i = 0
    while i < len(parts):
        p = parts[i]
        
        # Handle Type (CV, PV)
        if p.upper() in ['CV', 'PV']:
            base = p.upper()
            # Check if next part is a digit (e.g., "PV" "1")
            if i + 1 < len(parts) and parts[i+1].isdigit():
                base += parts[i+1]
                i += 1 # Skip next part
            new_parts.append(base)
        # Handle combined Type+Digit (e.g., "PV1")
        elif p.upper().startswith('PV') and len(p) > 2:
             new_parts.append(p.upper())
        # Handle City Names
        else:
            new_parts.append(p.capitalize())
        i += 1
        
    return '_'.join(new_parts)

def calculate_end_date(doj_str):
    """Calculates end date as DOJ + 5 years."""
    if not doj_str:
        return None
    try:
        doj_str = str(doj_str).strip()
        
        if isinstance(doj_str, datetime.date):
            doj = doj_str
        else:
            doj = datetime.datetime.strptime(doj_str, '%Y-%m-%d').date()
            
        try:
            end_date = doj.replace(year=doj.year + 5)
        except ValueError:
            end_date = doj.replace(year=doj.year + 5, day=28)
        return end_date
    except ValueError:
        return None

