from django.db.models.fields import DateTimeField
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
import matplotlib.pyplot as plt
from moodle.settings import EMAIL_HOST_USER
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import numpy as np


def home(request):
    return render(request, 'myapp/home.html')


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Hi {username}, your account was created successfully')
            return redirect('home')
    else:
        form = UserRegisterForm()

    return render(request, 'myapp/register.html', {'form': form})


@login_required()
def createdcourses(request):
    data = Courses.objects.filter(user=request.user)
    return render(request, 'myapp/createdcourses.html', {'data': data})


@login_required()
def profile(request):
    return render(request, 'myapp/profile.html')
# Create your views here.


@login_required
def sendaddrequest(request, course_id):
    from_user = request.user
    related_course = Courses.objects.get(id=course_id)
    add_request, created = EnrollRequest.objects.get_or_create(from_user=from_user, related_course=related_course)
    user_in_courses = Courses.objects.filter(users_enrolled__in=[request.user.id])
    if created:
        messages.success(request, f'Hi {request.user.username}, your request is sent')
    else:
        messages.success(request, f'Hi {request.user.username},add_request already sent')
    course = Courses.objects.get(id=course_id)
    all_add_requests = EnrollRequest.objects.filter(related_course=course)
    return render(request, 'myapp/courseinfo.html', {'all_add_requests': all_add_requests, 'course': course})


@login_required
def acceptaddrequest(request, request_id):
    add_request = EnrollRequest.objects.get(id=request_id)
    course = Courses.objects.get(id=add_request.related_course.id)
    course.users_enrolled.add(add_request.from_user)
    messages.success(request, f'Added Successfully')
    add_request.delete()
    all_add_requests = EnrollRequest.objects.filter(related_course=course)
    return render(request, 'myapp/courseinfocreated.html', {'all_add_requests': all_add_requests, 'course': course})

@login_required
def joincoursestudent(request,course_id):
    if request.method == "POST":
        form = joincoursestudentForm(request.POST)
        if form.is_valid():
            code = request.POST.get('code')
            course = Courses.objects.get(id=course_id)
            if code == course.codestudent:
                course.users_enrolled.add(request.user)
                messages.success(request, f'Added Successfully')
            else:
                messages.warning(request, f'wrong code')
            return redirect('courseinfo',course_id=course_id)
    else:
        form = joincoursestudentForm()
    return render(request, 'myapp/joincoursestudent.html',{'form': form})

@login_required
def joincourseta(request,course_id):
    if request.method == "POST":
        form = joincoursetaForm(request.POST)
        if form.is_valid():
            code = request.POST.get('code')
            course = Courses.objects.get(id=course_id)
            if code == course.codeta:
                course.ta.add(request.user)
                course.users_enrolled.add(request.user)
                messages.success(request, f'Added Successfully')
            else:
                messages.warning(request, f'wrong code')
            return redirect('courseinfo',course_id=course_id)
    else:
        form = joincoursetaForm()
    return render(request, 'myapp/joincoursestudent.html',{'form': form})  



@login_required
def courseinfo(request, course_id):
    course = Courses.objects.get(id=course_id)
    assignments = Assignment.objects.filter(related_course=course)
    total = 0 #percentage of student
    coursetotal = 0
    percentage = 0
    meansper = []
    for i in assignments:
        submission = Submission.objects.filter(assignme = i)
        l = []
        for j in submission:
            if j.marksgot != -1:
                l.append(j.marksgot)
        l = np.array(l)
        mean = np.mean(l)
        meansper.append(mean*i.weightage/i.totalmarks)
    meanofclass = np.sum(np.array(meansper))
    for i in assignments:
        submission = Submission.objects.filter(submitter= request.user,assignme = i)
        for j in submission:
            if j.marksgot != -1:
                total = total+ j.marksgot/i.totalmarks*(i.weightage)
        coursetotal += i.totalmarks
        percentage += i.weightage
    form_1 = change_disable()
    if request.method == "POST":
        form_1= change_disable(request.POST)
        if form_1.is_valid():
            
            course.creater_disable = form_1.cleaned_data.get('creater_disable')
            course.save()
            #form_1.save()
        return redirect('courseinfo',course_id = course_id)
    progress = 0
    total_weightage = 0
    if request.user in course.users_enrolled.all() and request.user not in course.ta.all():
        assignments = Assignment.objects.filter(related_course = course)
        for i in assignments:
            total_weightage += i.weightage
            submission = Submission.objects.filter(assignme = i, submitter = request.user)
            if  submission.exists():
                progress += i.weightage
        progress = progress/(total_weightage)*100
    discussions = DiscussionForum.objects.filter(course = course)
    return render(request, 'myapp/courseinfo.html', {'course': course, 'assignments': assignments , 'form_1':form_1, 'coursetotal':coursetotal,'total':total, 'percentage':percentage,'meanofclass': meanofclass,'progress':progress,'discussions':discussions})

@login_required
def courseinfocreated(request, course_id):
    course = Courses.objects.get(id=course_id)
    all_add_requests = EnrollRequest.objects.filter(related_course=course)
    assignments = Assignment.objects.filter(related_course=course)
    coursetotal = 0
    percentage = 0
    for i in assignments:
        percentage += i.weightage
        coursetotal += i.totalmarks
    # assignments = course.assignments.all()
    meansper = []
    perc = []
    names = []
    for i in assignments:
        submission = Submission.objects.filter(assignme = i)
        l = []
        if submission.exists():
            for j in submission:
                if j.marksgot != -1:
                    l.append(j.marksgot)
        mean = 0
        if len(l) != 0:
            l = np.array(l)
            mean = np.mean(l)
        meansper.append(mean*i.weightage/i.totalmarks)
        names.append(i.title)
        perc.append(i.weightage)
    plt.figure()
    X_axis = np.arange(len(names))
    plt.bar(X_axis - 0.2, meansper, 0.4, label = 'percentage of means of Assignments')
    plt.bar(X_axis +0.2, perc, 0.4, label = 'weightage of Assignments')
    plt.xticks(X_axis, names)
    plt.xlabel("Assignments")
    plt.ylabel("Percentages")
    plt.title("Course Analysis")
    plt.legend()
    plt.savefig("myapp/static/myapp/course.jpg")
    meanformeanper = np.sum(np.array(meansper))
    varformeanper = np.var(np.array(meansper))
    discussions = DiscussionForum.objects.filter(course = course)
    form_1 = change_disable()
    if request.method == "POST":
        form_1= change_disable(request.POST)
        if form_1.is_valid():
            
            course.creater_disable = form_1.cleaned_data.get('creater_disable')
            course.save()
            #form_1.save()
        return redirect('courseinfocreated',course_id = course_id)
    return render(request, 'myapp/courseinfocreated.html', {'all_add_requests': all_add_requests,'form_1':form_1, 'course': course, 'assignments': assignments,'coursetotal':coursetotal, 'percentage':percentage,'meanformeanper':meanformeanper,'varformeanper':varformeanper,'discussions':discussions})


@login_required
def viewAssignment(request, assignment_id):
    assignment = Assignment.objects.get(id=assignment_id)
    submission = Submission.objects.filter(assignme = assignment)
    l = []
    for i in submission:
        if i.marksgot != -1:
            l.append(i.marksgot)
    l = np.array(l)
    var = np.var(l)
    mean = np.mean(l)
    plt.figure()
    plt.hist(l)
    plt.savefig("myapp/static/myapp/assignment.jpg")
    assignment_creater = assignment.related_course.user
    nowtime = datetime.datetime.now
    #assignment.complete = assignment.deadline < nowtime
    if request.user == assignment_creater or request.user in assignment.related_course.ta.all():
        submissions = Submission.objects.filter(assignme=assignment)
    else:
        submissions = Submission.objects.filter(submitter=request.user, assignme=assignment)
    return render(request, 'myapp/assignment.html', {'assignment': assignment, 'submissions': submissions, 'nowtime':nowtime,'var':var,'mean':mean})


@login_required
def createnewcourse(request):
    if request.method == "POST":
        form = courseForm(request.POST)
        if form.is_valid():
            name = request.POST.get('course_name')
            codeta = request.POST.get('codeta')
            codestudent = request.POST.get('codestudent')
            course = Courses.objects.create(course_name=name, user=request.user,codestudent = codestudent,codeta = codeta)
            course.users_enrolled.add(request.user)
            course.ta.add(request.user)
            data = Courses.objects.filter(user=request.user)
            messages.success(request, f'Added Successfully')
            return redirect('createdcourses')
    else:
        form = courseForm()
    return render(request, 'myapp/createnewcourse.html', {'form': form})


@login_required
def courseslist(request):
    courses = Courses.objects.all()
    return render(request, "myapp/courseslist.html", {'courses': courses})


@login_required
def enrolledcourses(request):
    data = Courses.objects.filter(users_enrolled__in=[request.user.id])
    return render(request, 'myapp/enrolledcourses.html', {'data': data})

@login_required
def tacourses(request):
    data = Courses.objects.filter(ta__in=[request.user.id])
    return render(request, 'myapp/enrolledcourses.html', {'data': data})

@login_required
def upload_assignment(request, course_id):
    if request.method == 'POST':
        form = UploadAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = Assignment(uploadfile=request.FILES['uploadfile'])
            instance.related_course = Courses.objects.get(id=course_id)
            instance.title = form.cleaned_data.get('title')
            instance.totalmarks = form.cleaned_data.get('totalmarks')
            instance.deadline = form.cleaned_data.get('deadline')
            instance.weightage= form.cleaned_data.get('weightage')
            instance.save()
            return redirect('courseinfocreated',course_id=course_id)
    else:
            form=UploadAssignmentForm()
    return render(request,'myapp/addassignment.html', {'form':form})
		
@login_required
def addsubmission(request,assignment_id):
    if request.method == 'POST':
        form = UploadSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = Assignment.objects.get(id = assignment_id)
            submission = Submission.objects.filter(assignme = assignment,submitter = request.user)
            if submission.exists():
                submission.delete()
            instance = Submission(ansfile = request.FILES['ansfile'])
            instance.assignme = Assignment.objects.get(id=assignment_id)
            instance.submitter = request.user
            instance.save()
            return redirect('viewAssignment',assignment_id=assignment_id)
    else:
        form = UploadSubmissionForm()
    return render(request,'myapp/addsubmission.html',{'form':form })
 
@login_required
def editprofile(request):
    if request.method == "POST":
        form = editForm(request.POST)
        if form.is_valid():
            newfirstname = form.cleaned_data.get('newfirstname')
            newlastname = form.cleaned_data.get('newlastname')
            newemail = form.cleaned_data.get('newemail')
            request.user.first_name = newfirstname
            request.user.last_name = newlastname
            request.user.email = newemail
            request.user.save()
            messages.success(request,f'Updated Successfully')
            return redirect('home')
    else:
        form = editForm()
    return render(request,'myapp/editprofile.html',{'form': form})
    	


@login_required
def uploadcsv(request,assignment_id):
	if "GET" == request.method:
		return render(request, 'myapp/uploadcsvfile.html',{'assignment_id': assignment_id})
	csv_file = request.FILES["csv_file"]
	if not csv_file.name.endswith('.csv'):
		messages.error(request,'File is not CSV type')
		return redirect("uploadcsv",assignment_id=assignment_id)
	file_data = csv_file.read().decode("utf-8")
	lines = file_data.split("\n")
	req_assignment = Assignment.objects.get(id=assignment_id)
	submissions=Submission.objects.filter(assignme = req_assignment)
	for line in lines:
		fields = line.split(",")
		for submission in submissions:
			if submission.submitter.username==fields[0]:
				submission.marksgot = fields[1]
				submission.feedback = fields[2]
				submission.save()
				messages.success(request, f'marks of {fields[0]} updated!')
	return redirect('viewAssignment',assignment_id=assignment_id)

@login_required
def explore(request, course_id):
    course = Courses.objects.get(id = course_id)
    creatercourse = course.user
    students = course.users_enrolled
    tas = course.ta
    usersall = get_user_model().objects.all()
    return render(request,'myapp/explore.html',{'course': course,'usersall' : usersall})

@login_required
def inviteta(request, course_id, user_id):
    course = Courses.objects.get(id = course_id)
    receipient = get_user_model().objects.get(id = user_id)
    body = "Here is the code to join the course " + str(course.course_name) + " "+ str(course.codeta) + ". Hurry Up!!"
    email = EmailMessage(
        'Join the course as a TA',
        body,
        settings.EMAIL_HOST_USER,
        [str(receipient.email)],
        )

    email.fail_silently=False
    email.send()
    messages.success(request, f'sent Successfully')
    return redirect('explore',course_id=course_id)
@login_required
def invitestudent(request, course_id, user_id):
    course = Courses.objects.get(id = course_id)
    body = "Here is the code to join the course " + str(course.course_name) + " "+str(course.codestudent) + ". Hurry Up!!"
    receipient = get_user_model().objects.get(id = user_id)
    email = EmailMessage(
        'Join The Course as a Student',
        body,
        settings.EMAIL_HOST_USER,
        [receipient.email],
        )

    email.fail_silently=False
    email.send()
    messages.success(request, f'sent Successfully')
    return redirect('explore',course_id=course_id)
		
	
@login_required
def addcomment(request,dis_id):
    discussion = DiscussionForum.objects.get(id = dis_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            
            name = request.user.username
            body = form.cleaned_data.get('comment_body')

            c = Comment(discussion = discussion, commentor_name=name, comment_body=body,date_added = datetime.datetime.now())
            c.save()

        return redirect('discthread',dis_id = dis_id)    
        
    
    else:
        form = CommentForm()
    
       
    return render(request, 'myapp/addcomment.html', {'form':form})
		
	

@login_required
def direct_message(request):
    if request.method == 'POST':
        form = DM(request.POST)
        if form.is_valid():
            from_name = request.user.username
            body = form.cleaned_data.get('what_mess')   
            to_name = form.cleaned_data.get('to_user')
            c = DirectMessage.objects.create(fromuser = from_name, what_mess = body , to_user = to_name)

            c.save()
        return  render(request , 'myapp/home.html') 
    else:

        form = DM()
    to_message = DirectMessage.objects.filter(to_user = request.user.username)
    your_message = DirectMessage.objects.filter(fromuser = request.user.username)

    return render(request , 'myapp/direct_message.html',{'form':form , 'to_message':to_message , 'your_message':your_message})	   
    
    
@login_required
def todo(request , course_id):
    course = Courses.objects.get(id = course_id)
    if request.user in course.users_enrolled.all() and request.user not in course.ta.all():
        assignments = Assignment.objects.filter(related_course = course)
        required = []
        for i in assignments:
            submission = Submission.objects.filter(assignme = i, submitter = request.user)
            if not submission.exists():
                required.append(i)
        return render(request,'myapp/todo.html',{'required': required, 'course':course})
    else:
        assignments = Assignment.objects.filter(related_course = course)
        required = []
        for i in assignments:
            submissions = Submission.objects.filter(assignme = i, marksgot = -1)
            if submissions.exists():
                required.append(i)
        return render(request,'myapp/todo.html',{'required': required,'course':course})


@login_required
def adddiscthread(request,course_id):
    course = Courses.objects.get(id = course_id)
    instance = DiscussionForum(course = course)
    instance.save()
    return redirect('courseinfo',course_id = course_id)
    
@login_required
def discthread(request,dis_id):
    discussion = DiscussionForum.objects.get(id = dis_id)
    comments = Comment.objects.filter(discussion = discussion)
    return render(request,'myapp/discussion.html',{'discussion':discussion,'comments':comments})    
    
    
