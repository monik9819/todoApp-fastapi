import pytest

def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1
    assert type("hello" is str)

def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)

def test_boolean_check():
    valid = False
    assert valid is False
    assert valid is not True

def test_gt_lt():
    assert 3 < 5
    assert 3 <= 3

def test_list():
    num_list = [1,2,3,4,5]
    any_list = [False, False]

    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)


class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():
    return Student("John", "Doe", "Math", 1)


def test_person_init(default_employee):
    assert default_employee.first_name == "John", "first_name should be John"
    assert default_employee.last_name == "Doe", "last_name should be Doe"
    assert default_employee.major == "Math"
    assert default_employee.years == 1