from django.shortcuts import (render, redirect)
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf import settings
from ims_lti_py.tool_config import ToolConfig
from django.http import HttpResponse
from canvas_sdk.methods import enrollments
from canvas_sdk.utils import get_all_list_data
from canvas_sdk.exceptions import CanvasAPIError
from canvas_sdk import RequestContext

SDK_CONTEXT = request_context = RequestContext(**settings.CANVAS_SDK_SETTINGS)

# Create your views here.

TOOL_NAME = "basic_lti_app"

@require_http_methods(['GET'])
def index(request):
    """
    Show the index file
    """
    return render(request, 'basic_lti_app/index.html')

@login_required()
@require_http_methods(['POST'])
def lti_launch(request):
    """
    This method is here to build the LTI_LAUNCH dictionary containing all
    the LTI parameters and place it into the session. This is nessesary as we 
    need to access these parameters throughout the application and they are only 
    available the first time the application loads.
    """
    if request.user.is_authenticated():
        return redirect('basic_lti_app:main')
    else:
        return render(request, 'basic_lti_app/error.html', {'message': 'Error: user is not authenticated!'})

@login_required()
@require_http_methods(['GET'])
def main(request):
    """
    The main method dipslay the default view which is the map_view.
    """
    canvas_course_id = request.session['LTI_LAUNCH']['custom_canvas_course_id']
    users = get_all_list_data(SDK_CONTEXT, enrollments.list_enrollments_courses, canvas_course_id)

    lti_params_dict = request.session.get('LTI_LAUNCH', {})

    return render(request, 'basic_lti_app/lti_view.html', {'request': request, 'lti_params_dict': lti_params_dict, 'enrollments': users})

@require_http_methods(['GET'])
def tool_config(request):
    """
    This produces a Canvas specific XML config that can be used to
    add this tool to the Canvas LMS
    """
    if request.is_secure():
        host = 'https://' + request.get_host()
    else:
        host = 'http://' + request.get_host()

    url = host + reverse('basic_lti_app:lti_launch')

    lti_tool_config = ToolConfig(
        title='Basic LTI App',
        launch_url=url,
        secure_launch_url=url,
    )
    account_nav_params = {
        'enabled': 'true',
        # optionally, supply a different URL for the link:
        # 'url': 'http://library.harvard.edu',
        'text': 'basic lti app',
    }
    lti_tool_config.set_ext_param('canvas.instructure.com', 'privacy_level', 'public')
    lti_tool_config.set_ext_param('canvas.instructure.com', 'course_navigation', account_nav_params)
    lti_tool_config.description = 'This LTI app shows all the LTI parameters'

    resp = HttpResponse(lti_tool_config.to_xml(), content_type='text/xml', status=200)
    return resp
