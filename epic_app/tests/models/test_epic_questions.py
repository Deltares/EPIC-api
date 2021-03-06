import pytest
from django.db import IntegrityError, transaction

from epic_app.models.epic_questions import (
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
def EpicQuestionsFixture(epic_test_db: pytest.fixture):
    """
    Dummy fixture just to load a default db from dummy_db.

    Args:
        epic_test_db (pytest.fixture): Fixture to load for the whole file tests.
    """
    pass


@pytest.mark.django_db
class TestQuestion:
    def test_question_data(self):
        # Define data
        q_title = "Aliqua culpa consequat eiusmod eu voluptate quis proident."
        q_program = Program.objects.all().first()
        assert not Question.objects.filter(title=q_title).exists()

        # Create instance
        q_created = Question(title=q_title, program=q_program)
        q_created.save()

        # Verify final expectations
        assert Question.objects.filter(title=q_title, program=q_program).exists()
        assert str(q_created) == q_title[0:15]

    def test_delete_question_program_deletes_in_cascade(self):
        # Define data
        q_title = "Aliqua culpa consequat eiusmod eu voluptate quis proident."
        q_program = Program.objects.all().first()
        assert not Question.objects.filter(title=q_title).exists()

        # Create instance
        q_created = Question(title=q_title, program=q_program)
        q_created.save()
        assert Question.objects.filter(title=q_title).exists()
        q_created.program.delete()

        assert not Question.objects.filter(title=q_title).exists()

    def test_question_cannot_add_twice_title_program_pair(self):
        # Define data
        q_title = "Aliqua culpa consequat eiusmod eu voluptate quis proident."
        q_program = Program.objects.all().first()
        assert not Question.objects.filter(title=q_title, program=q_program).exists()

        # Try adding instances
        Question(title=q_title, program=q_program).save()
        with transaction.atomic():
            with pytest.raises(IntegrityError) as e_info:
                Question(title=q_title, program=q_program).save()

        assert Question.objects.filter(title=q_title, program=q_program).exists()


@pytest.mark.django_db
class TestNationalFrameworkQuestion:
    def test_nationalframeworkquestion_data(self):
        nfq_title = "Cupidatat nisi nisi esse exercitation dolor laborum cillum."
        nfq_description = "Dolore esse labore duis commodo aliquip."

        # Verify initial expectations
        assert not Question.objects.filter(title=nfq_title).exists()
        assert not NationalFrameworkQuestion.objects.filter(title=nfq_title).exists()

        # Create new question.
        nfq = NationalFrameworkQuestion(
            title=nfq_title,
            program=Program.objects.all().first(),
            description=nfq_description,
        )
        nfq.save()

        # Verify final expectations.
        assert Question.objects.filter(title=nfq_title).exists()
        assert NationalFrameworkQuestion.objects.filter(title=nfq_title).exists()
        assert isinstance(nfq, Question)


@pytest.mark.django_db
class TestKeyAgencyActionsQuestion:
    def test_nationalframeworkquestion_data(self):
        kaaq_title = "Cupidatat nisi nisi esse exercitation dolor laborum cillum."
        kaaq_description = "Dolore esse labore duis commodo aliquip."

        # Verify initial expectations
        assert not Question.objects.filter(title=kaaq_title).exists()
        assert not KeyAgencyActionsQuestion.objects.filter(title=kaaq_title).exists()

        # Create new question.
        kaaq = KeyAgencyActionsQuestion(
            title=kaaq_title,
            program=Program.objects.all().first(),
            description=kaaq_description,
        )
        kaaq.save()

        # Verify final expectations.
        assert Question.objects.filter(title=kaaq_title).exists()
        assert KeyAgencyActionsQuestion.objects.filter(title=kaaq_title).exists()
        assert isinstance(kaaq, Question)


@pytest.mark.django_db
class TestEvolutionQuestion:
    def test_evolutionquestion_data(self):
        evq_title = "Cupidatat nisi nisi esse exercitation dolor laborum cillum."
        nascent_description = "Dolore esse labore duis commodo aliquip."
        engaged_description = "Commodo in ad eiusmod nostrud sint ut nisi amet."
        capable_description = (
            "Eu enim dolor proident dolor labore cillum esse voluptate."
        )
        effective_description = "Pariatur ipsum id quis cupidatat minim."

        # Verify initial expectations
        assert not Question.objects.filter(title=evq_title).exists()
        assert not EvolutionQuestion.objects.filter(title=evq_title).exists()

        # Create new question.
        evq = EvolutionQuestion(
            title=evq_title,
            program=Program.objects.all().first(),
            nascent_description=nascent_description,
            engaged_description=engaged_description,
            capable_description=capable_description,
            effective_description=effective_description,
        )
        evq.save()

        # Verify final expectations.
        assert Question.objects.filter(title=evq_title).exists()
        assert EvolutionQuestion.objects.filter(title=evq_title).exists()
        assert isinstance(evq, Question)


@pytest.mark.django_db
class TestLinkagesQuestion:
    def test_linkagesquestion_data(self):
        # Define initial data.
        lq_title = "Id adipisicing labore magna est sunt duis amet nostrud labore est aute ullamco."
        lq_program: Program = Program.objects.all().last()

        # Verify initial expectations
        assert not LinkagesQuestion.objects.filter(
            title=lq_title, program=lq_program
        ).exists()

        # Create new LinkagesQuestion
        lq_created = LinkagesQuestion(title=lq_title, program=lq_program)
        lq_created.save()

        # Verify final expectations
        assert LinkagesQuestion.objects.filter(
            title=lq_title, program=lq_program
        ).exists()
        assert isinstance(lq_created, Question)

    def test_linkages_constrained_one_per_program(self):
        # Get one existing linkage question.
        l_question: LinkagesQuestion = LinkagesQuestion.objects.all().first()
        q_title = "Ad magna aliqua eiusmod sint est."

        # Verify initial expectations.
        assert q_title != l_question

        # Run test
        with transaction.atomic():
            with pytest.raises(IntegrityError) as e_info:
                LinkagesQuestion(title=q_title, program=l_question.program).save()

        # Verify final expectations.
        assert (
            str(e_info.value)
            == "UNIQUE constraint failed: epic_app_question.program_id"
        )
