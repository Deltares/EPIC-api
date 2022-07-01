import json

import pytest
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
    LinkagesQuestion,
    NationalFrameworkQuestion,
)
from epic_app.models.epic_user import EpicOrganization, EpicUser
from epic_app.models.models import Program
from epic_app.serializers.answer_serializer import (
    AgreementAnswerSerializer,
    AnswerSerializer,
    EvolutionAnswerSerializer,
    MultipleChoiceAnswerSerializer,
    _BaseAnswerSerializer,
)
from epic_app.tests import django_postgresql_db
from epic_app.tests.epic_db_fixture import epic_test_db
from epic_app.utils import get_submodel_type_list


@pytest.fixture(autouse=False)
@django_postgresql_db
def answer_serializer_fixture(
    epic_test_db: pytest.fixture,
):
    """
    Dummy fixture just to load a default db from dummy_db.

    Args:
        epic_test_db (pytest.fixture): Fixture to load for the whole file tests.
    """
    theonewhoasks = EpicUser.objects.create(
        username="TheOneWhoAsks",
        organization=EpicOrganization.objects.create(name="TestCorp"),
    )
    nfq = NationalFrameworkQuestion.objects.all().first()
    evq = EvolutionQuestion.objects.all().first()
    lkq = LinkagesQuestion.objects.all().first()
    yna = AgreementAnswer.objects.create(
        user=theonewhoasks,
        question=nfq,
        selected_choice=AgreementAnswerType.AGR,
        justify_answer="Velit ex cupidatat do magna ipsum.",
    )
    sca = EvolutionAnswer.objects.create(
        user=theonewhoasks,
        question=evq,
        selected_choice=EvolutionChoiceType.ENGAGED,
        justify_answer="Ipsum anim fugiat sit nostrud enim.",
    )
    mca = MultipleChoiceAnswer.objects.create(
        user=theonewhoasks,
        question=lkq,
    )
    selected_programs = [Program.objects.all()[2], Program.objects.all()[4]]
    mca.selected_programs.add(*selected_programs)
    return {
        AgreementAnswer: {
            "url": "http://testserver/api/answer/1/",
            "id": yna.id,
            "user": theonewhoasks.id,
            "question": nfq.id,
            "selected_choice": str(AgreementAnswerType.AGR),
            "justify_answer": "Velit ex cupidatat do magna ipsum.",
        },
        EvolutionAnswer: {
            "id": sca.id,
            "justify_answer": "Ipsum anim fugiat sit nostrud enim.",
            "question": evq.id,
            "selected_choice": str(EvolutionChoiceType.ENGAGED),
            "url": "http://testserver/api/answer/2/",
            "user": theonewhoasks.id,
        },
        MultipleChoiceAnswer: {
            "id": mca.id,
            "question": lkq.id,
            "selected_programs": [sp.id for sp in selected_programs],
            "url": "http://testserver/api/answer/3/",
            "user": theonewhoasks.id,
        },
    }


def get_serializer():
    factory = APIRequestFactory()
    request = factory.get("/")

    return {
        "request": Request(request),
    }


serializer_context = get_serializer()


@django_postgresql_db
class TestAnswerSerializer:
    @pytest.mark.parametrize("answer_type", get_submodel_type_list(Answer))
    def test_get_concrete_serializer_registered_answer_subclasses_succeeds(
        self,
        answer_type: Answer,
    ):
        r_serializer = _BaseAnswerSerializer.get_concrete_serializer(answer_type)
        assert r_serializer is not None
        assert issubclass(r_serializer, _BaseAnswerSerializer)

    def test_get_concrete_serializer_unregistered_answer_subclasses_raises(self):
        class DummySerializer(_BaseAnswerSerializer):
            pass

        with pytest.raises(ValueError) as err_info:
            _BaseAnswerSerializer.get_concrete_serializer(DummySerializer)

        assert (
            str(err_info.value)
            == f"Question type {DummySerializer} has no designated serializer."
        )

    def test_serialize_all_answers(self, answer_serializer_fixture: dict):
        expected_data = [
            dict(
                url=asf["url"],
                id=asf["id"],
                user=asf["user"],
                question=asf["question"],
            )
            for asf in answer_serializer_fixture.values()
        ]

        serialized_data = list(
            AnswerSerializer(
                Answer.objects.all(),
                many=True,
                context=serializer_context,
            ).data
        )

        assert len(serialized_data) == 3
        assert json.dumps(serialized_data) == json.dumps(expected_data)

    @pytest.mark.parametrize(
        "serializer, answer_type",
        [
            pytest.param(
                AgreementAnswerSerializer,
                AgreementAnswer,
            ),
            pytest.param(
                EvolutionAnswerSerializer,
                EvolutionAnswer,
            ),
            pytest.param(
                MultipleChoiceAnswerSerializer,
                MultipleChoiceAnswer,
            ),
        ],
    )
    def test_given_valid_instances_serializer_returns_type_expected_data(
        self,
        serializer,
        answer_type: Answer,
        answer_serializer_fixture: dict,
    ):
        # Define test data
        expected_data = answer_serializer_fixture[answer_type]
        expected_data.pop("url")
        # Run test
        serialized_data = list(
            serializer(
                answer_type.objects.all(),
                many=True,
                context=serializer_context,
            ).data
        )

        # Verify final expectations.
        assert len(serialized_data) == 1
        for field, value in expected_data.items():
            assert (
                serialized_data[0][field] == value
            ), f"{field} not matching expectations."
