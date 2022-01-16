"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine
if their course can be taken or not.

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge.
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
from abc import ABC, abstractmethod
import json
import re


class Condition(ABC):
    @abstractmethod
    def satisfied(self, courses_list: list[str]) -> bool:
        pass


class Conjunction(Condition):
    def __init__(self, subconditions: list[Condition] = []):
        self.subconditions = subconditions

    def __repr__(self):
        return f"({' & '.join(map(repr, self.subconditions))})"

    def satisfied(self, courses_list: list[str]) -> bool:
        return all(sub.satisfied(courses_list) for sub in self.subconditions)


class Union(Condition):
    def __init__(self, subconditions: list[Condition] = []):
        self.subconditions = subconditions

    def __repr__(self):
        return f"({' | '.join(map(repr, self.subconditions))})"

    def satisfied(self, courses_list: list[str]) -> bool:
        return any(sub.satisfied(courses_list) for sub in self.subconditions)


class SingleCourse(Condition):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def satisfied(self, courses_list: list[str]) -> bool:
        return self.name in courses_list


class UOC(Condition):
    def __init__(self, num_credits: int, prefix: str, courses: list[str]):
        self.num_credits = num_credits
        self.prefix = prefix
        self.courses = courses

    def __repr__(self):
        return f'{self.num_credits} credits in {self.prefix}/{self.courses}'

    def satisfied(self, courses_list: list[str]) -> bool:
        credits_done = 0
        for course in courses_list:
            if ((self.courses and course in self.courses)
                    or self.prefix is None
                    or course.startswith(self.prefix)):
                credits_done += 6
        return credits_done >= self.num_credits


class Verum(Condition):
    def __repr__(self):
        return 'T'

    def satisfied(self, courses_list: list[str]) -> bool:
        return True


def parse_condition(condition: str) -> Condition | None:
    condition = condition.strip()
    if not condition:
        return Verum()
    if condition.isnumeric():
        return SingleCourse(f'COMP{condition}')
    if re.match(r'[a-zA-Z]{4}\d{4}$', condition):
        return SingleCourse(condition)

    groups, type_of_condition = parse_groups(condition)
    if len(groups) == 1:
        # couldn't split any further. This may be a UOC condition, but I don't
        # have enough time right now to finish this
        return None
    if type_of_condition:
        return type_of_condition(list(filter(None, map(parse_condition, groups))))
    else:
        return None


def parse_groups(condition: str) -> tuple[list[str], type[Conjunction] | type[Union] | None]:
    groups: list[str] = []
    group: list[str] = []
    brackets = 0
    type = None

    def endgroup():
        nonlocal group
        nonlocal type
        joined = ''.join(group)
        if 'or' in joined.lower():
            type = Union
        elif 'and' in joined.lower():
            type = Conjunction
        group = []

    for char in condition:
        if not brackets and group and char == '(':
            groups.append(''.join(group))
            endgroup()
            brackets = 1
        elif brackets == 1 and char == ')':
            groups.append(''.join(group))
            group = []
            brackets = 0
        else:
            group.append(char)
            if char == '(':
                brackets += 1
            elif char == ')':
                brackets -= 1
            elif not brackets and (match := re.search(r'.*([a-zA-Z]{4}\d{4})$', ''.join(group))):
                groups.append(match[1])
                endgroup()

    if group:
        groups.append(''.join(group))
        endgroup()

    return groups, type


# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    raw_conditions: dict[str, str] = json.load(f)
    CONDITIONS = {
        course: parse_condition(condition) for course, condition in raw_conditions.items()
    }
    f.close()


def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course
    can be unlocked by them.

    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    return CONDITIONS[target_course].satisfied(courses_list)
