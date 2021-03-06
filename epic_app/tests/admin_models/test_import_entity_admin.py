from io import BytesIO
from pathlib import Path
from typing import Tuple
from wsgiref.simple_server import WSGIRequestHandler

import pytest
from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.test import RequestFactory

from epic_app.admin_models.generate_entity_admin import LnkAdmin
from epic_app.admin_models.import_entity_admin import (
    AgencyAdmin,
    AreaAdmin,
    EvoAdmin,
    ImportEntityAdmin,
    KaaAdmin,
    NfqAdmin,
)
from epic_app.models.epic_questions import (
    EvolutionQuestion,
    KeyAgencyActionsQuestion,
    NationalFrameworkQuestion,
)
from epic_app.models.models import Agency, Area, Group, Program
from epic_app.tests import test_data_dir
from epic_app.tests.importers import default_epic_domain_data, full_epic_domain_data
from epic_app.tests.request_helper import _create_get_request, _create_post_request


def _get_xlsx_inmemoryfile(filename: str) -> InMemoryUploadedFile:
    test_file: Path = test_data_dir / "xlsx" / filename
    assert test_file.is_file()
    with test_file.open("rb") as csv_file:
        file_io = BytesIO(csv_file.read())
        file_io.name = test_file.name
        file_io.seek(0)
    in_memory_file = InMemoryUploadedFile(
        file_io,
        None,
        file_io.name,
        "application/vnd.ms-excel",
        len(file_io.getvalue()),
        None,
    )
    return in_memory_file


def _get_model_admin_site(model_type: models.Model) -> ImportEntityAdmin:
    reg_model = next(
        (r_model for r_model in admin.site._registry if r_model is model_type), None
    )
    assert reg_model is not None, f"No {str(model_type)} was registered an admin model."

    return admin.site._registry[reg_model]


def _validate_fixture_data_before_import():
    # Verify initial expectations
    assert len(Area.objects.all()) > 1, "Is the data fixture invoked?"
    assert len(Agency.objects.all()) > 1, "Is the data fixture invoked?"
    assert len(Group.objects.all()) > 1, "Is the data fixture invoked?"
    assert len(Program.objects.all()) > 1, "Is the data fixture invoked?"


class TestImportEntityAdmin:

    import_model_cases = {
        Area: dict(
            admin_site=AreaAdmin,
            filename="initial_epic_data.xlsx",
        ),
        Agency: dict(admin_site=AgencyAdmin, filename="agency_data.xlsx"),
        NationalFrameworkQuestion: dict(
            admin_site=NfqAdmin, filename="nationalframeworkquestions.xlsx"
        ),
        KeyAgencyActionsQuestion: dict(
            admin_site=KaaAdmin, filename="keyagencyactionsquestions.xlsx"
        ),
        EvolutionQuestion: dict(
            admin_site=EvoAdmin, filename="evolutionquestions.xlsx"
        ),
    }

    @pytest.mark.parametrize(
        "model_admin_testcase",
        import_model_cases.items(),
        ids=import_model_cases.keys(),
    )
    def test_importentitymodel_is_initialized(
        self, model_admin_testcase: Tuple[models.Model, dict]
    ):
        model_type, dict_values = model_admin_testcase
        assert admin.site.is_registered(model_type)
        model_admin = _get_model_admin_site(model_type)

        assert isinstance(model_admin, dict_values["admin_site"])
        assert isinstance(model_admin, ImportEntityAdmin)
        assert model_admin.change_list_template == "import_changelist.html"
        assert any("import-xlsx/" in str(t_url) for t_url in model_admin.urls)

    @pytest.mark.parametrize("model_type", import_model_cases.keys())
    def test_get_import_xlsx_returns_success_code(self, model_type: models.Model):
        # This test only verifies we got a different page where the import will take place.
        rf = RequestFactory()
        request = rf.get("import-xlsx/")
        admin_site: ImportEntityAdmin = _get_model_admin_site(model_type)
        r_result = admin_site.import_xlsx(request)
        assert r_result is not None
        assert r_result.status_code == 200

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "model_admin_testcase",
        import_model_cases.items(),
        ids=import_model_cases.keys(),
    )
    def test_post_import_xlsx_with_valid_data_imports_and_redirects(
        self, model_admin_testcase: Tuple[models.Model, dict], full_epic_domain_data
    ):
        # Define request.
        model_type, dict_values = model_admin_testcase
        xlsx_file = _get_xlsx_inmemoryfile(dict_values["filename"])
        admin_site = _get_model_admin_site(model_type)
        post_request = _create_post_request("import_xlsx/")
        post_request.FILES["xlsx_file"] = xlsx_file

        # Verify initial expectations
        _validate_fixture_data_before_import()

        # Run test
        r_result = admin_site.import_xlsx(post_request)

        # Verify final expectations
        assert r_result is not None
        # Status code is redirected.
        assert r_result.status_code == 302
        assert r_result.url == ".."

        # Note, these results could change with 'newer' test data versions.
        assert len(model_type.objects.all()) > 0

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "model_admin_testcase",
        import_model_cases.items(),
        ids=import_model_cases.keys(),
    )
    def test_post_import_xlsx_with_empty_data_cleans_db_and_redirects(
        self, model_admin_testcase, full_epic_domain_data
    ):
        # Define request.
        model_type, _ = model_admin_testcase
        admin_site = _get_model_admin_site(model_type)
        post_request = _create_post_request("import-xlsx/")
        post_request.FILES["xlsx_file"] = None

        # Verify initial expectations
        _validate_fixture_data_before_import()

        # Run test
        r_result = admin_site.import_xlsx(post_request)

        # Verify final expectations
        assert r_result is not None
        # Status code is redirected.
        assert r_result.status_code == 302
        assert r_result.url == ".."
