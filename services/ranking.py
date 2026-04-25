from typing import List, Dict 

def rank_by_gpa(students: List[Dict[str, float]]) -> List[Dict[str, float]]: 
    return sorted(students, key=lambda x: (-x['gpa'],
                                            x['name'].strip().split()[-1],
                                              x['name'].strip().split()[0]))
## The sorting key is a tuple that sorts primarily by GPA in descending order (hence the negative sign), then by last name, and finally by first name.
#  This ensures that students with the same GPA are ranked alphabetically by their names.