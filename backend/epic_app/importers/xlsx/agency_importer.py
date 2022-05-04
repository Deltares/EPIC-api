import csv
from pathlib import Path
from typing import Dict, List, Union

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import ValidationError

from epic_app.importers.xlsx.base_importer import BaseEpicImporter
from epic_app.models.models import Agency, Program


class EpicAgencyImporter(BaseEpicImporter):
    class XlsxLineObject(BaseEpicImporter.XlsxLineObject):
        agency: str
        program: str

        @classmethod
        def from_xlsx_row(cls, xlsx_row):
            new_line = cls()
            new_line.agency = cls.get_valid_cell(xlsx_row, 0)
            new_line.program = cls.get_valid_cell(xlsx_row, 1)
            return new_line

    def _import_agencies(self, agencies_dictionary: Dict[str, List[XlsxLineObject]]):
        missing_programs = []
        for agency_csvobjs in agencies_dictionary.values():
            for csv_obj in agency_csvobjs:
                if Program.get_program_by_name(csv_obj.program.lower()) is None:
                    missing_programs.append(csv_obj.program)
        if any(missing_programs):
            str_mp = ", ".join(set(missing_programs))
            raise ValidationError(
                f"The provided programs do not exist in the current database: \n{str_mp}"
            )

        # Remove all previous agency objects.
        Agency.objects.all().delete()
        for agency_name, agency_csvobj in agencies_dictionary.items():
            c_agency = Agency(name=agency_name)
            c_agency.save()
            for csvobj in agency_csvobj:
                existing_program: Program = Program.get_program_by_name(csvobj.program)
                existing_program.agencies.add(c_agency)

    def import_file(self, input_file: Union[InMemoryUploadedFile, Path]):
        """
        Imports saved Agencies into the database and adds the relationships to existent Programs.

        Args:
            input_file (Union[InMemoryUploadedFile, Path]): File containing EPIC Agencies.
        """
        Agency.objects.all().delete()
        line_objects = self._get_xlsx_line_objects(input_file)
        _headers = line_objects.pop(0)
        self._import_agencies(self.group_entity("agency", line_objects))