import logging
import urllib

from django.conf import settings
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from mitxmako.shortcuts import render_to_response, render_to_string
#from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from lxml import etree

from module_render import render_module, make_track_function, I4xSystem
from models import StudentModule
from student.models import UserProfile
from multicourse import multicourse_settings

import courseware.content_parser as content_parser
import courseware.modules

import courseware.grades as grades

log = logging.getLogger("mitx.courseware")

etree.set_default_parser(etree.XMLParser(dtd_validation=False, load_dtd=False,
                                         remove_comments = True))

template_imports={'urllib':urllib}

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def gradebook(request):
    if 'course_admin' not in content_parser.user_groups(request.user):
        raise Http404

    # TODO: This should be abstracted out. We repeat this logic many times. 
    if 'coursename' in request.session: coursename = request.session['coursename'] 
    else: coursename = None

    student_objects = User.objects.all()[:100]
    student_info = [{'username' :s.username,
                     'id' : s.id,
                     'email': s.email,
                     'grade_info' : grades.grade_sheet(s,coursename), 
                     'realname' : UserProfile.objects.get(user = s).name
                     } for s in student_objects]

    return render_to_response('gradebook.html',{'students':student_info})

@login_required
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def profile(request, student_id = None):
    ''' User profile. Show username, location, etc, as well as grades .
        We need to allow the user to change some of these settings .'''

    if student_id == None:
        student = request.user
    else: 
        print content_parser.user_groups(request.user)
        if 'course_admin' not in content_parser.user_groups(request.user):
            raise Http404
        student = User.objects.get( id = int(student_id))

    user_info = UserProfile.objects.get(user=student) # request.user.profile_cache # 

    if 'coursename' in request.session: coursename = request.session['coursename']
    else: coursename = None

    context={'name':user_info.name,
             'username':student.username,
             'location':user_info.location,
             'language':user_info.language,
             'email':student.email,
             'format_url_params' : content_parser.format_url_params,
             'csrf':csrf(request)['csrf_token']
             }
    context.update(grades.grade_sheet(student,coursename))

    return render_to_response('profile.html', context)

def render_accordion(request,course,chapter,section):
    ''' Draws navigation bar. Takes current position in accordion as
        parameter. Returns (initialization_javascript, content)'''
    if not course:
        course = "6.002 Spring 2012"

    toc=content_parser.toc_from_xml(content_parser.course_file(request.user,course), chapter, section)
    active_chapter=1
    for i in range(len(toc)):
        if toc[i]['active']:
            active_chapter=i
    context=dict([['active_chapter',active_chapter],
                  ['toc',toc], 
                  ['course_name',course],
                  ['format_url_params',content_parser.format_url_params],
                  ['csrf',csrf(request)['csrf_token']]] + \
                     template_imports.items())
    return render_to_string('accordion.html',context)

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def render_section(request, section):
    ''' TODO: Consolidate with index 
    '''
    user = request.user
    if not settings.COURSEWARE_ENABLED:
        return redirect('/')

    if 'coursename' in request.session: coursename = request.session['coursename']
    else: coursename = None

#    try: 
    dom = content_parser.section_file(user, section, coursename)
    #except:
     #   raise Http404

    accordion=render_accordion(request, '', '', '')

    module_ids = dom.xpath("//@id")
    
    if user.is_authenticated():
        module_object_preload = list(StudentModule.objects.filter(student=user, 
                                                                  module_id__in=module_ids))
    else:
        module_object_preload = []
    
    module=render_module(user, request, dom, module_object_preload)

    if 'init_js' not in module:
        module['init_js']=''

    context={'init':module['init_js'],
             'accordion':accordion,
             'content':module['content'],
             'csrf':csrf(request)['csrf_token']}

    result = render_to_response('courseware.html', context)
    return result


@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def index(request, course=None, chapter="Using the System", section="Hints"): 
    ''' Displays courseware accordion, and any associated content. 
    ''' 
    user = request.user
    if not settings.COURSEWARE_ENABLED:
        return redirect('/')

    if course==None:
        if not settings.ENABLE_MULTICOURSE:
            course = "6.002 Spring 2012"
        elif 'coursename' in request.session:
            course = request.session['coursename']
        else:
            course = settings.COURSE_DEFAULT

    # Fixes URLs -- we don't get funny encoding characters from spaces
    # so they remain readable
    ## TODO: Properly replace underscores
    course=course.replace("_"," ")
    chapter=chapter.replace("_"," ")
    section=section.replace("_"," ")

    # use multicourse module to determine if "course" is valid
    #if course!=settings.COURSE_NAME.replace('_',' '):
    if not multicourse_settings.is_valid_course(course):
        return redirect('/')

    #import logging
    #log = logging.getLogger("mitx")
    #log.info(  "DEBUG: "+str(user) )

    request.session['coursename'] = course		# keep track of current course being viewed in django's request.session

    dom = content_parser.course_file(user,course)	# also pass course to it, for course-specific XML path
    dom_module = dom.xpath("//course[@name=$course]/chapter[@name=$chapter]//section[@name=$section]/*[1]", 
                           course=course, chapter=chapter, section=section)
    if len(dom_module) == 0:
        module = None
    else:
        module = dom_module[0]

    accordion=render_accordion(request, course, chapter, section)

    module_ids = dom.xpath("//course[@name=$course]/chapter[@name=$chapter]//section[@name=$section]//@id", 
                           course=course, chapter=chapter, section=section)

    if user.is_authenticated():
        module_object_preload = list(StudentModule.objects.filter(student=user, 
                                                                  module_id__in=module_ids))
    else:
        module_object_preload = []
    

    module=render_module(user, request, module, module_object_preload)

    if 'init_js' not in module:
        module['init_js']=''

    context={'init':module['init_js'],
             'accordion':accordion,
             'content':module['content'],
             'COURSE_TITLE':multicourse_settings.get_course_title(course),
             'csrf':csrf(request)['csrf_token']}

    result = render_to_response('courseware.html', context)
    return result


def modx_dispatch(request, module=None, dispatch=None, id=None):
    ''' Generic view for extensions. '''
    if not request.user.is_authenticated():
        return redirect('/')

    # Grab the student information for the module from the database
    s = StudentModule.objects.filter(student=request.user, 
                                     module_id=id)
    #s = StudentModule.get_with_caching(request.user, id)
    if len(s) == 0 or s is None:
        log.debug("Couldnt find module for user and id " + str(module) + " " + str(request.user) + " "+ str(id))
        raise Http404
    s = s[0]

    oldgrade = s.grade
    oldstate = s.state

    dispatch=dispatch.split('?')[0]

    ajax_url = settings.MITX_ROOT_URL + '/modx/'+module+'/'+id+'/'

    # get coursename if stored
    if 'coursename' in request.session: coursename = request.session['coursename']
    else: coursename = None

    # Grab the XML corresponding to the request from course.xml
    xml = content_parser.module_xml(request.user, module, 'id', id, coursename)

    # Create the module
    system = I4xSystem(track_function = make_track_function(request), 
                       render_function = None, 
                       ajax_url = ajax_url,
                       filestore = None
                       )
    instance=courseware.modules.get_module_class(module)(system, 
                                                         xml, 
                                                         id, 
                                                         state=oldstate)
    # Let the module handle the AJAX
    ajax_return=instance.handle_ajax(dispatch, request.POST)
    # Save the state back to the database
    s.state=instance.get_state()
    if instance.get_score(): 
        s.grade=instance.get_score()['score']
    if s.grade != oldgrade or s.state != oldstate:
        s.save()
    # Return whatever the module wanted to return to the client/caller
    return HttpResponse(ajax_return)

def quickedit(request, id=None):
    '''
    quick-edit capa problem.

    Maybe this should be moved into capa/views.py
    Or this should take a "module" argument, and the quickedit moved into capa_module.
    '''
    print "WARNING: UNDEPLOYABLE CODE. FOR DEV USE ONLY."
    print "In deployed use, this will only edit on one server"
    print "We need a setting to disable for production where there is"
    print "a load balanacer"
    if not request.user.is_staff():
        return redirect('/')

    # get coursename if stored
    if 'coursename' in request.session: coursename = request.session['coursename']
    else: coursename = None

    def get_lcp(coursename,id):
        # Grab the XML corresponding to the request from course.xml
        module = 'problem'
        xml = content_parser.module_xml(request.user, module, 'id', id, coursename)
    
        ajax_url = settings.MITX_ROOT_URL + '/modx/'+module+'/'+id+'/'
    
        # Create the module (instance of capa_module.Module)
        system = I4xSystem(track_function = make_track_function(request), 
                           render_function = None, 
                           ajax_url = ajax_url,
                           filestore = None,
                           coursename = coursename,
                           role = 'staff' if request.user.is_staff else 'student',		# TODO: generalize this
                           )
        instance=courseware.modules.get_module_class(module)(system, 
                                                             xml, 
                                                             id,
                                                             state=None)
        lcp = instance.lcp
        pxml = lcp.tree
        pxmls = etree.tostring(pxml,pretty_print=True)

        return instance, pxmls

    instance, pxmls = get_lcp(coursename,id)

    # if there was a POST, then process it
    msg = ''
    if 'qesubmit' in request.POST:
        action = request.POST['qesubmit']
        if "Revert" in action:
            msg = "Reverted to original"
        elif action=='Change Problem':
            key = 'quickedit_%s' % id
            if not key in request.POST:
                msg = "oops, missing code key=%s" % key
            else:
                newcode = request.POST[key]

                # see if code changed
                if str(newcode)==str(pxmls) or '<?xml version="1.0"?>\n'+str(newcode)==str(pxmls):
                    msg = "No changes"
                else:
                    # check new code
                    isok = False
                    try:
                        newxml = etree.fromstring(newcode)
                        isok = True
                    except Exception,err:
                        msg = "Failed to change problem: XML error \"<font color=red>%s</font>\"" % err
    
                    if isok:
                        filename = instance.lcp.fileobject.name
                        fp = open(filename,'w')		# TODO - replace with filestore call?
                        fp.write(newcode)
                        fp.close()
                        msg = "<font color=green>Problem changed!</font> (<tt>%s</tt>)"  % filename
                        instance, pxmls = get_lcp(coursename,id)

    lcp = instance.lcp

    # get the rendered problem HTML
    phtml = instance.get_problem_html()

    context = {'id':id,
               'msg' : msg,
               'lcp' : lcp,
               'filename' : lcp.fileobject.name,
               'pxmls' : pxmls,
               'phtml' : phtml,
               'init_js':instance.get_init_js(),
               }

    result = render_to_response('quickedit.html', context)
    return result
