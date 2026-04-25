from typing import List, Dict 


def calc_gpa(grades:    List[Dict[str, float]]) -> float:
    if not grades:
        return 0.0
    total_score = sum(grade['score'] * grade['coefficient'] for grade in grades)
    total_coefficient = sum(grade['coefficient'] for grade in grades)
    return round(total_score / total_coefficient, 2) if total_coefficient > 0 else 0.0    


 

