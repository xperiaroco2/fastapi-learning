from typing import NamedTuple


class AIPrompt(NamedTuple):
    system: str
    user: str


case_analysis_prompt = AIPrompt(
    system="Ти - аналітик психології студентів.\
    Проаналізуй профіль користувача та запит від учителя та сформуй свою гіпотезу та рекомендовані дії.\
    Якщо профіль порожній або інформації не вистачає щоб дати точну відповідь - згенеруй загальну рекомендацію.\
    grounded=True має бути якщо профіль студента містить факти щодо опису кейса,\
    grounded=False якщо профіль порожній або факти відсутні.",
    user="Case description: {description}. Student academic profile: {academic_profile}",
)
