import json
from typing import Any, Dict, Type

import pytest
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from epic_app.models.epic_answers import (
    AgreementAnswer,
    AgreementAnswerType,
    Answer,
    EvolutionAnswer,
    MultipleChoiceAnswer,
)
from epic_app.models.epic_questions import (
    EvolutionChoiceType,
    EvolutionQuestion,
    KeyAgencyActionsQuestion,
    LinkagesQuestion,
    NationalFrameworkQuestion,
    Question,
)
from epic_app.models.epic_user import EpicUser
from epic_app.models.models import Program
from epic_app.serializers.report_serializer import (
    AnswerListReportSerializer,
    AnswerReportSerializer,
    ProgramReportSerializer,
    QuestionReportSerializer,
)
from epic_app.tests import django_postgresql_db
from epic_app.tests.epic_db_fixture import epic_test_db
from epic_app.utils import get_submodel_type_list


@django_postgresql_db
def get_serializer():
    factory = APIRequestFactory()
    request = factory.get("/")

    return {
        "request": Request(request),
        "users": EpicUser.objects.all(),
    }


serializer_context = get_serializer()


@pytest.fixture(autouse=False)
@django_postgresql_db
def _report_serializer_fixture(
    epic_test_db: pytest.fixture,
) -> None:
    anakin = EpicUser.objects.filter(username="Anakin").first()
    aga = AgreementAnswer.objects.create(
        user=anakin,
        question=Question.objects.filter(pk=1).first(),
        selected_choice=AgreementAnswerType.DIS,
        justify_answer="Laboris proident enim dolore ullamco voluptate nisi labore laborum ut qui adipisicing occaecat exercitation culpa.",
    )
    sca = EvolutionAnswer.objects.create(
        user=anakin,
        question=Question.objects.filter(pk=3).first(),
        selected_choice=EvolutionChoiceType.EFFECTIVE,
        justify_answer="Ea ut ipsum deserunt culpa laborum excepteur laboris ad adipisicing ad officia laboris.",
    )
    mca = MultipleChoiceAnswer(
        user=anakin,
        question=Question.objects.filter(pk=5).first(),
    )
    mca.save()
    mca.selected_programs.add(4, 2)


@django_postgresql_db
class TestAnswerReportSerializer:
    def test_ctor(self):
        serializer = AnswerReportSerializer()
        assert isinstance(serializer, serializers.BaseSerializer)

    expected_answer_dict = {
        AgreementAnswer: {
            "id": 1,
            "selected_choice": "DISAGREE",
            "justify_answer": "Laboris proident enim dolore ullamco voluptate nisi labore laborum ut qui adipisicing occaecat exercitation culpa.",
            "user": 3,
            "question": 1,
        },
        EvolutionAnswer: {
            "id": 2,
            "selected_choice": "EFFECTIVE",
            "justify_answer": "Ea ut ipsum deserunt culpa laborum excepteur laboris ad adipisicing ad officia laboris.",
            "user": 3,
            "question": 3,
        },
        MultipleChoiceAnswer: {
            "id": 3,
            "user": 3,
            "question": 5,
            "selected_programs": [2, 4],
        },
    }

    @pytest.mark.parametrize("answer_type", get_submodel_type_list(Answer))
    def test_answer_report_to_representation(
        self, answer_type: Type[Answer], _report_serializer_fixture: pytest.fixture
    ):
        subtype_instance = answer_type.objects.all().first()
        answer_instance = Answer.objects.get(id=subtype_instance.id)
        represented_data = AnswerReportSerializer(
            context=serializer_context
        ).to_representation(answer_instance)
        assert represented_data == self.expected_answer_dict[answer_type]


@django_postgresql_db
class TestAnswerListReportSerializer:

    expected_answer_list_dict = {
        AgreementAnswer: {
            "answers": [
                TestAnswerReportSerializer.expected_answer_dict[AgreementAnswer]
            ],
            "summary": {
                "Strongly_disagree": 0,
                "Strongly_disagree_justify": [],
                "Disagree": 1,
                "Disagree_justify": [
                    "Laboris proident enim dolore ullamco voluptate nisi labore laborum ut qui adipisicing occaecat exercitation culpa."
                ],
                "Neither_agree_nor_disagree": 0,
                "Neither_agree_nor_disagree_justify": [],
                "Agree": 0,
                "Agree_justify": [],
                "Strongly_agree": 0,
                "Strongly_agree_justify": [],
                "no_valid_response": 2,
            },
        },
        EvolutionAnswer: {
            "answers": [
                TestAnswerReportSerializer.expected_answer_dict[EvolutionAnswer],
            ],
            "summary": {
                "Capable": 0,
                "Capable_justify": [],
                "Effective": 1,
                "Effective_justify": [
                    "Ea ut ipsum deserunt culpa laborum excepteur laboris ad adipisicing ad officia laboris."
                ],
                "Engaged": 0,
                "Engaged_justify": [],
                "Nascent": 0,
                "Nascent_justify": [],
                "no_valid_response": 2,
            },
        },
        MultipleChoiceAnswer: {
            "answers": [
                TestAnswerReportSerializer.expected_answer_dict[MultipleChoiceAnswer]
            ],
            "summary": {"b": 1, "d": 1, "no_valid_response": 2},
        },
    }

    def test_ctor(self):
        serializer = AnswerListReportSerializer(
            child=AnswerReportSerializer(read_only=True),
        )
        assert isinstance(serializer, serializers.ListSerializer)

    @pytest.mark.parametrize("answer_type", get_submodel_type_list(Answer))
    def test_answer_list_report_to_representation(
        self, answer_type: Type[Answer], _report_serializer_fixture: pytest.fixture
    ):
        # Define test data
        subtype_instance = answer_type.objects.all().first()

        class FakeInstance:
            instance = subtype_instance.question

        # Serialize data
        represented_data = AnswerListReportSerializer(
            child=AnswerReportSerializer(read_only=True), context=serializer_context
        ).to_representation(FakeInstance())

        # Verify final expectations.
        assert json.dumps(represented_data) == json.dumps(
            self.expected_answer_list_dict[answer_type]
        )


@django_postgresql_db
class TestQuestionReportSerializer:
    def test_ctor(self):
        serializer = QuestionReportSerializer()
        assert isinstance(serializer, serializers.BaseSerializer)

    expected_question_dict = {
        NationalFrameworkQuestion: {
            "url": "http://testserver/api/question/1/",
            "id": 1,
            "title": "Is this a National Framework question?",
            "question_answers": TestAnswerListReportSerializer.expected_answer_list_dict[
                AgreementAnswer
            ],
        },
        EvolutionQuestion: {
            "url": "http://testserver/api/question/3/",
            "id": 3,
            "title": "Is this an Evolution question?",
            "question_answers": TestAnswerListReportSerializer.expected_answer_list_dict[
                EvolutionAnswer
            ],
        },
        LinkagesQuestion: {
            "url": "http://testserver/api/question/5/",
            "id": 5,
            "title": "Finally a linkage question?",
            "question_answers": TestAnswerListReportSerializer.expected_answer_list_dict[
                MultipleChoiceAnswer
            ],
        },
        KeyAgencyActionsQuestion: {
            "url": "http://testserver/api/question/6/",
            "id": 6,
            "title": "Is this the new Key Agency Action question?",
            "question_answers": {"answers": [], "summary": {}},
        },
    }

    @pytest.mark.parametrize("question_type", get_submodel_type_list(Question))
    def test_question_report_to_representation(
        self, question_type: Type[Answer], _report_serializer_fixture: pytest.fixture
    ):
        subtype_instance = question_type.objects.all().first()
        question_instance = Question.objects.get(id=subtype_instance.id)
        represented_data = QuestionReportSerializer(
            context=serializer_context
        ).to_representation(question_instance)
        assert json.dumps(represented_data) == json.dumps(
            self.expected_question_dict[question_type]
        )


@django_postgresql_db
class TestProgramReportSerializer:
    def test_ctor(self):
        serializer = ProgramReportSerializer()
        assert isinstance(serializer, serializers.BaseSerializer)

    expected_program_data = {
        "url": "http://testserver/api/program/1/",
        "id": 1,
        "name": "a",
        "questions": [
            TestQuestionReportSerializer.expected_question_dict[
                NationalFrameworkQuestion
            ],
            {
                "url": "http://testserver/api/question/2/",
                "id": 2,
                "title": "Is this another National Framework question?",
                "question_answers": {"answers": [], "summary": {}},
            },
            TestQuestionReportSerializer.expected_question_dict[EvolutionQuestion],
            {
                "url": "http://testserver/api/question/4/",
                "id": 4,
                "title": "Is this yet another Evolution question?",
                "question_answers": {"answers": [], "summary": {}},
            },
            TestQuestionReportSerializer.expected_question_dict[LinkagesQuestion],
            TestQuestionReportSerializer.expected_question_dict[
                KeyAgencyActionsQuestion
            ],
        ],
    }

    def test_program_report_to_representation(
        self, _report_serializer_fixture: pytest.fixture
    ):
        program_instance = Program.objects.get(name="a")
        represented_data = ProgramReportSerializer(
            context=serializer_context
        ).to_representation(program_instance)
        assert json.dumps(represented_data) == json.dumps(self.expected_program_data)
