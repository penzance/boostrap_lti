import unittest
from django.test import RequestFactory
from django_auth_lti import const
from mock import patch, ANY, DEFAULT, Mock
from basic_lti_app.views import lti_launch

@patch.multiple('basic_lti_app.views', render=DEFAULT)
class BasicLTIAppViewsTests(unittest.TestCase):
    longMessage = True

    def setUp(self):

        self.request = RequestFactory().post('/fake-path')
        self.request.user = Mock(name='user_mock')
        self.request.user.is_authenticated.return_value = True


        self.request.session = {
            'LTI_LAUNCH': {
                'lis_course_offering_sourcedid' : '5',
                'roles' : [const.INSTRUCTOR,const.TEACHING_ASSISTANT,const.ADMINISTRATOR,const.CONTENT_DEVELOPER],
            }
        }

    @patch('basic_lti_app.views.redirect')
    def test_get_lti_param(self, mock_redirect, render):
        """
        Test that get_table_name_from_canvas_role is called with the correct id
        """
        lti_launch(self.request)
        mock_redirect.assert_called_with('basic_lti_app:main')
