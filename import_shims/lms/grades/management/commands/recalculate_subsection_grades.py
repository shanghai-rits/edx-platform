"""Deprecated import support. Auto-generated by import_shims/generate_shims.sh."""
# pylint: disable=redefined-builtin,wrong-import-position,wildcard-import,useless-suppression,line-too-long

from import_shims.warn import warn_deprecated_import

warn_deprecated_import('grades.management.commands.recalculate_subsection_grades', 'lms.djangoapps.grades.management.commands.recalculate_subsection_grades')

from lms.djangoapps.grades.management.commands.recalculate_subsection_grades import *
