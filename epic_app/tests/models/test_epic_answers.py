import itertools
from typing import Any, Dict, List, Optional

import pytest
from django.db import IntegrityError

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
from epic_app.tests.epic_db_fixture import epic_test_db


@pytest.fixture(autouse=True)
def EpicAnswersFixture(epic_test_db: pytest.fixture):
    """
    Dummy fixture just to load a default db from dummy_db.

    Args:
        epic_test_db (pytest.fixture): Fixture to load for the whole file tests.
    """
    pass


def get_subtypes(model):
    subtypes = []
    for m in model.__subclasses__():
        if m.__subclasses__():
            subtypes.append(m.__subclasses__())
        else:
            subtypes.append([m])
    return list(itertools.chain(*subtypes))


@pytest.mark.django_db
class TestEpicAnswers:

    answer_ctor: dict = {
        MultipleChoiceAnswer: dict(),
        EvolutionAnswer: dict(
            selected_choice=EvolutionChoiceType.NASCENT,
            justify_answer="Magna laboris ex Lorem dolor mollit eiusmod occaecat deserunt reprehenderit labore velit ad excepteur.",
        ),
        AgreementAnswer: dict(
            selected_choice=AgreementAnswerType.DIS,
            justify_answer="Magna laboris ex Lorem dolor mollit eiusmod occaecat deserunt reprehenderit labore velit ad excepteur.",
        ),
    }

    def test_answer_ctor(self):
        # Define input data.
        epic_question = Question.objects.all().first()
        epic_user = EpicUser.objects.all().first()

        # Instantiate answer.
        base_answer = Answer(question=epic_question, user=epic_user)

        # Verify final expectations.
        assert str(epic_question) in str(base_answer)
        assert str(epic_user) in str(base_answer)
        assert not base_answer._get_supported_questions()
        assert not base_answer._check_question_integrity()
        with pytest.raises(IntegrityError) as err_info:
            base_answer.save()
        assert (
            str(err_info.value)
            == "Question type `Question` not allowed. Supported types: []."
        )
        with pytest.raises(NotImplementedError) as exc_err:
            base_answer.is_valid_answer()
        assert (
            str(exc_err.value)
            == "Validation only supported on inherited Answer classes."
        )
        with pytest.raises(NotImplementedError) as exc_err:
            base_answer.get_detailed_summary(Answer.objects.all())
        assert (
            str(exc_err.value)
            == "Detailed summary only supported on inherited Answer classes."
        )

    @pytest.mark.parametrize(
        "question_subtype",
        get_subtypes(Question),
    )
    @pytest.mark.parametrize("answer_subtype", get_subtypes(Answer))
    def test_SAVE_answer(self, question_subtype: Question, answer_subtype: Answer):
        # Define test data
        if not answer_subtype in self.answer_ctor.keys():
            # Check the key exists (doing a .get(key, None) would always check to false for linkages)
            pytest.fail(f"No test input defined for answer type: {answer_subtype}")

        answer_args = self.answer_ctor[answer_subtype]
        answer_args["question"] = question_subtype.objects.all().first()
        answer_args["user"] = EpicUser.objects.all().first()
        assert isinstance(answer_args["question"], Question)

        # Run test and verify expectations.
        answer_instance: Answer = answer_subtype(**answer_args)
        assert not answer_instance in list(answer_subtype.objects.all())

        if question_subtype in answer_instance._get_supported_questions():
            # Run test
            answer_instance.save()
            # Verify final expectations.
            assert answer_instance in list(answer_subtype.objects.all())
        else:
            # Run test
            with pytest.raises(IntegrityError) as ie_exc:
                answer_instance.save()

            # Verify final expectations.
            supported_answers: str = ", ".join(
                [
                    f"`{sq.__name__}`"
                    for sq in answer_instance._get_supported_questions()
                ]
            )
            assert (
                str(ie_exc.value)
                == f"Question type `{question_subtype.__name__}` not allowed. Supported types: [{supported_answers}]."
            )

    @pytest.mark.parametrize(
        "question_subtype, answer_subtype",
        [
            pytest.param(NationalFrameworkQuestion, AgreementAnswer),
            pytest.param(KeyAgencyActionsQuestion, AgreementAnswer),
            pytest.param(EvolutionQuestion, EvolutionAnswer),
            pytest.param(LinkagesQuestion, MultipleChoiceAnswer),
        ],
    )
    def test_SAVE_twice_answer_will_raise_integrity_error(
        self, question_subtype: Question, answer_subtype: Answer
    ):
        with pytest.raises(IntegrityError):
            # Create it once, there should be no problem
            self.test_SAVE_answer(question_subtype, answer_subtype)
            # Create it twice, it should trigger an update instead of create.
            self.test_SAVE_answer(question_subtype, answer_subtype)


@pytest.mark.django_db
class TestEvolutionAnswer:
    @pytest.mark.parametrize(
        "selected_choice, expected_result",
        [
            pytest.param("", False, id="No selected choice"),
            pytest.param(
                EvolutionChoiceType.CAPABLE, True, id="CAPABLE selected choice"
            ),
            pytest.param(
                EvolutionChoiceType.EFFECTIVE, True, id="EFFECTIVE selected choice"
            ),
            pytest.param(
                EvolutionChoiceType.ENGAGED, True, id="ENGAGED selected choice"
            ),
            pytest.param(
                EvolutionChoiceType.NASCENT, True, id="NASCENT selected choice"
            ),
        ],
    )
    @pytest.mark.parametrize(
        "justify_answer",
        [
            pytest.param("", id="Empty justification filled"),
            pytest.param("Lorem ipsum", id="Justification filled"),
        ],
    )
    def test_evolutionanswer_is_valid_answer(
        self,
        selected_choice: Optional[EvolutionChoiceType],
        justify_answer: Optional[str],
        expected_result: bool,
    ):
        an_user: EpicUser = EpicUser.objects.first()
        EvolutionAnswer.objects.all().delete()
        an_evolution_question = EvolutionQuestion.objects.first()
        sca = EvolutionAnswer.objects.create(
            user=an_user, question=an_evolution_question
        )
        sca.selected_choice = selected_choice
        sca.justify_answer = justify_answer
        sca.save()
        assert sca.is_valid_answer() == expected_result

    @pytest.mark.parametrize(
        "selected_choice",
        EvolutionChoiceType,
    )
    def test_evolutionanswer_get_detailed_summary(
        self,
        selected_choice: Optional[EvolutionChoiceType],
    ):
        # Define test data
        EvolutionAnswer.objects.all().delete()
        sca = EvolutionAnswer.objects.create(
            user=EpicUser.objects.first(), question=EvolutionQuestion.objects.first()
        )
        justify = "Consequat quis adipisicing culpa veniam aliquip anim amet labore commodo ullamco laborum quis enim in."
        sca.selected_choice = selected_choice
        sca.justify_answer = justify
        sca.save()

        # Define exepcted results
        def _get_result(choice_type) -> int:
            return 1 if selected_choice == choice_type else 0

        def _get_justify(choice_type) -> List[Optional[str]]:
            return [justify] if selected_choice == choice_type else []

        expected_result = {
            str(EvolutionChoiceType.CAPABLE.label): _get_result(
                EvolutionChoiceType.CAPABLE
            ),
            f"{str(EvolutionChoiceType.CAPABLE.label)}_justify": _get_justify(
                EvolutionChoiceType.CAPABLE
            ),
            str(EvolutionChoiceType.EFFECTIVE.label): _get_result(
                EvolutionChoiceType.EFFECTIVE
            ),
            f"{str(EvolutionChoiceType.EFFECTIVE.label)}_justify": _get_justify(
                EvolutionChoiceType.EFFECTIVE
            ),
            str(EvolutionChoiceType.ENGAGED.label): _get_result(
                EvolutionChoiceType.ENGAGED
            ),
            f"{str(EvolutionChoiceType.ENGAGED.label)}_justify": _get_justify(
                EvolutionChoiceType.ENGAGED
            ),
            str(EvolutionChoiceType.NASCENT.label): _get_result(
                EvolutionChoiceType.NASCENT
            ),
            f"{str(EvolutionChoiceType.NASCENT.label)}_justify": _get_justify(
                EvolutionChoiceType.NASCENT
            ),
            "no_valid_response": 0,
        }

        # Run test
        return_summary = EvolutionAnswer.get_detailed_summary(
            EvolutionAnswer.objects.all()
        )

        # Verify expectations
        assert return_summary == expected_result


@pytest.mark.django_db
class TestAgreementAnswer:
    @pytest.mark.parametrize(
        "justify_answer",
        [
            pytest.param("", id="Empty justification filled"),
            pytest.param("Lorem ipsum", id="Justification filled"),
        ],
    )
    @pytest.mark.parametrize(
        "yesno_answer, expected_result",
        [
            pytest.param(AgreementAnswerType.SDIS, True, id="Strongly disagree answer"),
            pytest.param(AgreementAnswerType.DIS, True, id="Disagree answer"),
            pytest.param(
                AgreementAnswerType.NAND, True, id="Neither agree nor disagree answer"
            ),
            pytest.param(AgreementAnswerType.AGR, True, id="Agree answer"),
            pytest.param(AgreementAnswerType.SAGR, True, id="Strongly agree answer"),
            pytest.param("", False, id="Empty answer"),
        ],
    )
    def test_agreementanswer_is_valid_answer(
        self,
        yesno_answer: Optional[AgreementAnswerType],
        justify_answer: Optional[str],
        expected_result: bool,
    ):
        an_user: EpicUser = EpicUser.objects.first()
        AgreementAnswer.objects.all().delete()
        a_yn_question = NationalFrameworkQuestion.objects.first()
        yna = AgreementAnswer.objects.create(user=an_user, question=a_yn_question)
        yna.selected_choice = yesno_answer
        yna.justify_answer = justify_answer
        yna.save()
        assert yna.is_valid_answer() == expected_result

    @pytest.mark.parametrize(
        "selected_choice",
        AgreementAnswerType,
    )
    def test_agreementanswer_get_detailed_summary(
        self,
        selected_choice: Optional[AgreementAnswerType],
    ):
        # Define test data
        AgreementAnswer.objects.all().delete()
        sca = AgreementAnswer.objects.create(
            user=EpicUser.objects.first(),
            question=NationalFrameworkQuestion.objects.first(),
        )
        justify = "Consequat quis adipisicing culpa veniam aliquip anim amet labore commodo ullamco laborum quis enim in."
        sca.selected_choice = selected_choice
        sca.justify_answer = justify
        sca.save()

        # Define exepcted results
        def _get_result(ag_type) -> int:
            return 1 if selected_choice == ag_type else 0

        def _get_justify(ag_type) -> List[Optional[str]]:
            return [justify] if selected_choice == ag_type else []

        expected_result = {
            str(AgreementAnswerType.SDIS.label): _get_result(AgreementAnswerType.SDIS),
            f"{str(AgreementAnswerType.SDIS.label)}_justify": _get_justify(
                AgreementAnswerType.SDIS
            ),
            str(AgreementAnswerType.DIS.label): _get_result(AgreementAnswerType.DIS),
            f"{str(AgreementAnswerType.DIS.label)}_justify": _get_justify(
                AgreementAnswerType.DIS
            ),
            str(AgreementAnswerType.NAND.label): _get_result(AgreementAnswerType.NAND),
            f"{str(AgreementAnswerType.NAND.label)}_justify": _get_justify(
                AgreementAnswerType.NAND
            ),
            str(AgreementAnswerType.AGR.label): _get_result(AgreementAnswerType.AGR),
            f"{str(AgreementAnswerType.AGR.label)}_justify": _get_justify(
                AgreementAnswerType.AGR
            ),
            str(AgreementAnswerType.SAGR.label): _get_result(AgreementAnswerType.SAGR),
            f"{str(AgreementAnswerType.SAGR.label)}_justify": _get_justify(
                AgreementAnswerType.SAGR
            ),
            "no_valid_response": 0,
        }

        # Run test
        return_summary = AgreementAnswer.get_detailed_summary(
            AgreementAnswer.objects.all()
        )

        # Verify expectations
        assert return_summary == expected_result


@pytest.mark.django_db
class TestMultipleChoiceAnswer:
    @pytest.mark.parametrize(
        "selected_programs, expected_result",
        [
            pytest.param(["a"], True, id="One selection"),
            pytest.param(["a", "b"], True, id="Multiple selection"),
            pytest.param("", False, id="No selection"),
            pytest.param([], False, id="Empty selection"),
        ],
    )
    def test_multiplechoiceanswer_is_valid_answer(
        self,
        selected_programs: Optional[List[int]],
        expected_result: bool,
    ):
        an_user: EpicUser = EpicUser.objects.first()
        MultipleChoiceAnswer.objects.all().delete()
        a_lnk_question = LinkagesQuestion.objects.first()
        mca = MultipleChoiceAnswer.objects.create(user=an_user, question=a_lnk_question)
        selected_ids = [
            Program.objects.get(name=p_name).id for p_name in selected_programs
        ]
        mca.selected_programs.set(selected_ids)
        mca.save()
        assert mca.is_valid_answer() == expected_result

    @pytest.mark.parametrize(
        "selected_programs",
        [
            pytest.param(["a"], id="One selection"),
            pytest.param(["a", "b"], id="Multiple selection"),
            pytest.param("", id="No selection"),
            pytest.param([], id="Empty selection"),
        ],
    )
    def test_multiplechoiceanswer_get_detailed_summary(
        self,
        selected_programs: Optional[List[str]],
    ):
        # Define test data.
        MultipleChoiceAnswer.objects.all().delete()
        mca = MultipleChoiceAnswer.objects.create(
            user=EpicUser.objects.first(), question=LinkagesQuestion.objects.first()
        )
        selected_ids = [
            Program.objects.get(name=p_name).id for p_name in selected_programs
        ]
        mca.selected_programs.set(selected_ids)
        mca.save()

        # Define expectations
        expected_result = {sp: 1 for sp in selected_programs}
        expected_result["no_valid_response"] = 0 if any(selected_programs) else 1

        # Run test
        detailed_summary = mca.get_detailed_summary(MultipleChoiceAnswer.objects.all())

        # Verify final expectations
        assert detailed_summary == expected_result
