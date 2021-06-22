"""
Tests for certificate generation handler
"""
import logging
from unittest import mock

import ddt
from edx_toggles.toggles.testutils import override_waffle_flag

from common.djangoapps.student.tests.factories import CourseEnrollmentFactory, UserFactory
from lms.djangoapps.certificates.generation_handler import (
    CERTIFICATES_USE_UPDATED,
    _can_generate_allowlist_certificate,
    _can_generate_certificate_for_status,
    _can_generate_v2_certificate,
    can_generate_certificate_task,
    generate_allowlist_certificate_task,
    generate_certificate_task,
    generate_regular_certificate_task,
    is_on_certificate_allowlist,
    is_using_v2_course_certificates,
    _set_allowlist_cert_status,
    _set_v2_cert_status
)
from lms.djangoapps.certificates.data import CertificateStatuses
from lms.djangoapps.certificates.models import GeneratedCertificate
from lms.djangoapps.certificates.tests.factories import (
    CertificateAllowlistFactory,
    CertificateInvalidationFactory,
    GeneratedCertificateFactory
)
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

log = logging.getLogger(__name__)

BETA_TESTER_METHOD = 'lms.djangoapps.certificates.generation_handler._is_beta_tester'
COURSE_OVERVIEW_METHOD = 'lms.djangoapps.certificates.generation_handler.get_course_overview_or_none'
CCX_COURSE_METHOD = 'lms.djangoapps.certificates.generation_handler._is_ccx_course'
ID_VERIFIED_METHOD = 'lms.djangoapps.verify_student.services.IDVerificationService.user_is_verified'
PASSING_GRADE_METHOD = 'lms.djangoapps.certificates.generation_handler._has_passing_grade'
WEB_CERTS_METHOD = 'lms.djangoapps.certificates.generation_handler.has_html_certificates_enabled'


@mock.patch(ID_VERIFIED_METHOD, mock.Mock(return_value=True))
@mock.patch(WEB_CERTS_METHOD, mock.Mock(return_value=True))
@ddt.ddt
class AllowlistTests(ModuleStoreTestCase):
    """
    Tests for handling allowlist certificates
    """

    def setUp(self):
        super().setUp()

        # Create user, a course run, and an enrollment
        self.user = UserFactory()
        self.course_run = CourseFactory()
        self.course_run_key = self.course_run.id  # pylint: disable=no-member
        self.enrollment = CourseEnrollmentFactory(
            user=self.user,
            course_id=self.course_run_key,
            is_active=True,
            mode="verified",
        )

        # Add user to the allowlist
        CertificateAllowlistFactory.create(course_id=self.course_run_key, user=self.user)

    def test_is_on_allowlist(self):
        """
        Test the presence of the user on the allowlist
        """
        assert is_on_certificate_allowlist(self.user, self.course_run_key)

    def test_is_on_allowlist_false(self):
        """
        Test the absence of the user on the allowlist
        """
        u = UserFactory()
        CourseEnrollmentFactory(
            user=u,
            course_id=self.course_run_key,
            is_active=True,
            mode="verified",
        )
        CertificateAllowlistFactory.create(course_id=self.course_run_key, user=u, allowlist=False)
        assert not is_on_certificate_allowlist(u, self.course_run_key)

    @ddt.data(
        (CertificateStatuses.deleted, True),
        (CertificateStatuses.deleting, True),
        (CertificateStatuses.downloadable, False),
        (CertificateStatuses.error, True),
        (CertificateStatuses.generating, True),
        (CertificateStatuses.notpassing, True),
        (CertificateStatuses.restricted, True),
        (CertificateStatuses.unavailable, True),
        (CertificateStatuses.audit_passing, True),
        (CertificateStatuses.audit_notpassing, True),
        (CertificateStatuses.honor_passing, True),
        (CertificateStatuses.unverified, True),
        (CertificateStatuses.invalidated, True),
        (CertificateStatuses.requesting, True))
    @ddt.unpack
    def test_generation_status(self, status, expected_response):
        """
        Test handling of certificate statuses
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=status,
        )

        assert _can_generate_certificate_for_status(u, key) == expected_response

    def test_generation_status_for_none(self):
        """
        Test handling of certificate statuses for a non-existent cert
        """
        assert _can_generate_certificate_for_status(None, None)

    def test_handle_invalid(self):
        """
        Test handling of an invalid user/course run combo
        """
        u = UserFactory()

        assert not _can_generate_allowlist_certificate(u, self.course_run_key)
        assert not generate_allowlist_certificate_task(u, self.course_run_key)
        assert not generate_certificate_task(u, self.course_run_key)
        assert _set_allowlist_cert_status(u, self.course_run_key) is None

    def test_handle_valid(self):
        """
        Test handling of a valid user/course run combo
        """
        assert _can_generate_allowlist_certificate(self.user, self.course_run_key)
        assert generate_allowlist_certificate_task(self.user, self.course_run_key)

    def test_handle_valid_general_methods(self):
        """
        Test handling of a valid user/course run combo for the general (non-allowlist) generation methods
        """
        assert can_generate_certificate_task(self.user, self.course_run_key)
        assert generate_certificate_task(self.user, self.course_run_key)

    def test_can_generate_not_verified(self):
        """
        Test handling when the user's id is not verified
        """
        with mock.patch(ID_VERIFIED_METHOD, return_value=False):
            assert not _can_generate_allowlist_certificate(self.user, self.course_run_key)
            assert _set_allowlist_cert_status(self.user, self.course_run_key) == CertificateStatuses.unverified

    def test_can_generate_not_enrolled(self):
        """
        Test handling when user is not enrolled
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CertificateAllowlistFactory.create(course_id=key, user=u)
        assert not _can_generate_allowlist_certificate(u, key)
        assert _set_allowlist_cert_status(u, key) is None

    def test_can_generate_audit(self):
        """
        Test handling when user is enrolled in audit mode
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="audit",
        )
        CertificateAllowlistFactory.create(course_id=key, user=u)

        assert not _can_generate_allowlist_certificate(u, key)
        assert _set_allowlist_cert_status(u, key) is None

    def test_can_generate_not_allowlisted(self):
        """
        Test handling when user is not on the certificate allowlist.
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        assert not _can_generate_allowlist_certificate(u, key)
        assert _set_allowlist_cert_status(u, key) is None

    def test_can_generate_invalidated(self):
        """
        Test handling when user is on the invalidate list
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        cert = GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=CertificateStatuses.downloadable
        )
        CertificateAllowlistFactory.create(course_id=key, user=u)
        CertificateInvalidationFactory.create(
            generated_certificate=cert,
            invalidated_by=self.user,
            active=True
        )

        assert not _can_generate_allowlist_certificate(u, key)
        assert _set_allowlist_cert_status(u, key) == CertificateStatuses.unavailable

    def test_can_generate_web_cert_disabled(self):
        """
        Test handling when web certs are not enabled
        """
        with mock.patch(WEB_CERTS_METHOD, return_value=False):
            assert not _can_generate_allowlist_certificate(self.user, self.course_run_key)
            assert _set_allowlist_cert_status(self.user, self.course_run_key) is None

    def test_can_generate_no_overview(self):
        """
        Test handling when the course overview is missing
        """
        with mock.patch(COURSE_OVERVIEW_METHOD, return_value=None):
            assert not _can_generate_allowlist_certificate(self.user, self.course_run_key)
            assert _set_allowlist_cert_status(self.user, self.course_run_key) is None

    def test_cert_status_downloadable(self):
        """
        Test cert status when status is already downloadable
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=CertificateStatuses.downloadable
        )

        assert _set_allowlist_cert_status(u, key) is None


@override_waffle_flag(CERTIFICATES_USE_UPDATED, active=True)
@mock.patch(ID_VERIFIED_METHOD, mock.Mock(return_value=True))
@mock.patch(CCX_COURSE_METHOD, mock.Mock(return_value=False))
@mock.patch(PASSING_GRADE_METHOD, mock.Mock(return_value=True))
@mock.patch(WEB_CERTS_METHOD, mock.Mock(return_value=True))
@ddt.ddt
class CertificateTests(ModuleStoreTestCase):
    """
    Tests for handling course certificates
    """

    def setUp(self):
        super().setUp()

        # Create user, a course run, and an enrollment
        self.user = UserFactory()
        self.course_run = CourseFactory()
        self.course_run_key = self.course_run.id  # pylint: disable=no-member
        self.enrollment = CourseEnrollmentFactory(
            user=self.user,
            course_id=self.course_run_key,
            is_active=True,
            mode="verified",
        )

    def test_handle_valid(self):
        """
        Test handling of a valid user/course run combo.
        """
        assert _can_generate_v2_certificate(self.user, self.course_run_key)
        assert can_generate_certificate_task(self.user, self.course_run_key)
        assert generate_certificate_task(self.user, self.course_run_key)

    def test_handle_valid_task(self):
        """
        Test handling of a valid user/course run combo.

        We test generate_certificate_task() and generate_regular_certificate_task() separately since they both
        generate a cert.
        """
        assert generate_regular_certificate_task(self.user, self.course_run_key)

    @override_waffle_flag(CERTIFICATES_USE_UPDATED, active=False)
    def test_handle_invalid(self):
        """
        Test handling of an invalid user/course run combo
        """
        other_user = UserFactory()
        assert not _can_generate_v2_certificate(other_user, self.course_run_key)
        assert not generate_certificate_task(other_user, self.course_run_key)
        assert not generate_regular_certificate_task(other_user, self.course_run_key)

    def test_is_using_updated_true(self):
        """
        Test the updated flag
        """
        assert is_using_v2_course_certificates(self.course_run_key)

    @ddt.data(
        (CertificateStatuses.deleted, True),
        (CertificateStatuses.deleting, True),
        (CertificateStatuses.downloadable, False),
        (CertificateStatuses.error, True),
        (CertificateStatuses.generating, True),
        (CertificateStatuses.notpassing, True),
        (CertificateStatuses.restricted, True),
        (CertificateStatuses.unavailable, True),
        (CertificateStatuses.audit_passing, True),
        (CertificateStatuses.audit_notpassing, True),
        (CertificateStatuses.honor_passing, True),
        (CertificateStatuses.unverified, True),
        (CertificateStatuses.invalidated, True),
        (CertificateStatuses.requesting, True))
    @ddt.unpack
    def test_generation_status(self, status, expected_response):
        """
        Test handling of certificate statuses
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=status,
        )

        assert _can_generate_certificate_for_status(u, key) == expected_response

    def test_generation_status_for_none(self):
        """
        Test handling of certificate statuses for a non-existent cert
        """
        assert _can_generate_certificate_for_status(None, None)

    def test_can_generate_not_verified(self):
        """
        Test handling when the user's id is not verified
        """
        with mock.patch(ID_VERIFIED_METHOD, return_value=False):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) == CertificateStatuses.unverified

    def test_can_generate_ccx(self):
        """
        Test handling when the course is a CCX (custom edX) course
        """
        with mock.patch(CCX_COURSE_METHOD, return_value=True):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) is None

    def test_can_generate_beta_tester(self):
        """
        Test handling when the user is a beta tester
        """
        with mock.patch(BETA_TESTER_METHOD, return_value=True):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) is None

    def test_can_generate_failing_grade(self):
        """
        Test handling when the user does not have a passing grade
        """
        with mock.patch(PASSING_GRADE_METHOD, return_value=False):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) == CertificateStatuses.notpassing

    def test_can_generate_not_enrolled(self):
        """
        Test handling when user is not enrolled
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        assert not _can_generate_v2_certificate(u, key)
        assert _set_v2_cert_status(u, key) is None

    def test_can_generate_audit(self):
        """
        Test handling when user is enrolled in audit mode
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="audit",
        )

        assert not _can_generate_v2_certificate(u, key)
        assert _set_v2_cert_status(u, key) is None

    def test_can_generate_invalidated(self):
        """
        Test handling when user is on the invalidate list
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        cert = GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=CertificateStatuses.downloadable
        )
        CertificateInvalidationFactory.create(
            generated_certificate=cert,
            invalidated_by=self.user,
            active=True
        )

        assert not _can_generate_v2_certificate(u, key)
        assert _set_v2_cert_status(u, key) == CertificateStatuses.unavailable

    def test_can_generate_web_cert_disabled(self):
        """
        Test handling when web certs are not enabled
        """
        with mock.patch(WEB_CERTS_METHOD, return_value=False):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) is None

    def test_can_generate_no_overview(self):
        """
        Test handling when the course overview is missing
        """
        with mock.patch(COURSE_OVERVIEW_METHOD, return_value=None):
            assert not _can_generate_v2_certificate(self.user, self.course_run_key)
            assert _set_v2_cert_status(self.user, self.course_run_key) is None

    def test_cert_status_downloadable(self):
        """
        Test cert status when status is already downloadable
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=CertificateStatuses.downloadable
        )

        assert _set_v2_cert_status(u, key) is None

    def test_cert_status_none(self):
        """
        Test cert status when the user has no cert
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )

        assert _set_v2_cert_status(u, key) == CertificateStatuses.notpassing

    def test_cert_status_generating(self):
        """
        Test cert status when status is generating
        """
        u = UserFactory()
        cr = CourseFactory()
        key = cr.id  # pylint: disable=no-member
        CourseEnrollmentFactory(
            user=u,
            course_id=key,
            is_active=True,
            mode="verified",
        )
        GeneratedCertificateFactory(
            user=u,
            course_id=key,
            mode=GeneratedCertificate.MODES.verified,
            status=CertificateStatuses.generating
        )

        assert _set_v2_cert_status(u, key) == CertificateStatuses.notpassing
