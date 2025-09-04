from django.shortcuts import render, redirect
from .models import StudentsAccount, RecommendDocument, CourseModule,RecommendCourse
from .models import ListLesson, Teacher, UserAction, ListLesson,  UserActionBook
from signup.models import Student
from .forms import DocumentUploadForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from llama_cpp import Llama
from datetime import datetime
from django.db.models.functions import TruncDate
from django.db.models import Sum
from django.db import models
from django.utils.timezone import now
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from llama_cpp import Llama
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import calendar
import json

def index(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    try:
        student_acc = StudentsAccount.objects.get(email=email)
    except StudentsAccount.DoesNotExist:
        return redirect('login')

    # Lấy duration theo ngày (giữ giây)
    actions = UserAction.objects.filter(user=student_acc).order_by("timestamp")
    daily_duration = {}
    for action in actions:
        date_str = action.timestamp.date().strftime("%Y-%m-%d")
        daily_duration[date_str] = daily_duration.get(date_str, 0) + action.duration

    action_dates = list(daily_duration.keys())
    action_seconds = list(daily_duration.values())  # dữ liệu giây gửi sang JS

    # Các thống kê khác
    mycourse = RecommendCourse.objects.filter(student_id=student_acc.student_id) 
    ongoing_courses = mycourse.filter(status="studying").count() 
    completed_courses = mycourse.filter(status="passed").count() 
    documents_count = RecommendDocument.objects.count() 
    total_courses = mycourse.count()
    avg_progress = round((completed_courses / total_courses) * 100, 2) if total_courses else 0
    # Lấy 5 sách gần đây sinh viên đọc
    # Lấy 5 sách gần đây sinh viên đọc
    recent_books = UserActionBook.objects.filter(
        student_id=student_acc.student_id
    ).order_by('-timestamp')[:5]

    # Lấy 5 sách khác mà sinh viên chưa đọc (ví dụ cùng source với các sách đang học)
    similar_books = UserActionBook.objects.exclude(
        student_id=student_acc.student_id
    ).order_by('-timestamp')[:5]

    return render(request, "home/home.html", {
        "user": student_acc,
        "action_dates": json.dumps(action_dates),
        "action_counts": json.dumps(action_seconds),
        "ongoing_courses": ongoing_courses,
        "completed_courses": completed_courses, 
        "documents_count": documents_count, 
        "avg_progress": avg_progress, 
        "recent_books": recent_books,
        "similar_books": similar_books,
    })


def dashboard_view(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    try:
        student_acc = StudentsAccount.objects.get(email=email)
    except StudentsAccount.DoesNotExist:
        return redirect('login')

    # Lấy duration theo ngày (giữ giây)
    actions = UserAction.objects.filter(user=student_acc).order_by("timestamp")
    daily_duration = {}
    for action in actions:
        date_str = action.timestamp.date().strftime("%Y-%m-%d")
        daily_duration[date_str] = daily_duration.get(date_str, 0) + action.duration

    action_dates = list(daily_duration.keys())
    action_seconds = list(daily_duration.values())  # dữ liệu giây gửi sang JS

    # Các thống kê khác
    mycourse = RecommendCourse.objects.filter(student_id=student_acc.student_id) 
    ongoing_courses = mycourse.filter(status="studying").count() 
    completed_courses = mycourse.filter(status="passed").count() 
    documents_count = RecommendDocument.objects.count() 
    total_courses = mycourse.count()
    avg_progress = round((completed_courses / total_courses) * 100, 2) if total_courses else 0
    # Lấy 5 sách gần đây sinh viên đọc
    # Lấy 5 sách gần đây sinh viên đọc
    recent_books = UserActionBook.objects.filter(
        student_id=student_acc.student_id
    ).order_by('-timestamp')[:5]

    # Lấy 5 sách khác mà sinh viên chưa đọc (ví dụ cùng source với các sách đang học)
    similar_books = UserActionBook.objects.exclude(
        student_id=student_acc.student_id
    ).order_by('-timestamp')[:5]

    return render(request, "home/home.html", {
        "user": student_acc,
        "action_dates": json.dumps(action_dates),
        "action_counts": json.dumps(action_seconds),
        "ongoing_courses": ongoing_courses,
        "completed_courses": completed_courses, 
        "documents_count": documents_count, 
        "avg_progress": avg_progress, 
        "recent_books": recent_books,
        "similar_books": similar_books,
    })


def account_view(request):
    email = request.session.get('user_email')

    if not email:
        return redirect('login')

    try:
        user = StudentsAccount.objects.get(email=email)
        approved = True

        if request.method == "POST":
            user.first_name = request.POST.get("first_name", user.first_name)
            user.student_id = request.POST.get("student_id", user.student_id)
            user.account_type = request.POST.get("account_type", user.account_type)
            user.phone = request.POST.get("phone", user.phone)
            dob = request.POST.get("dob")
            if dob:
                try:
                    user.birthday = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    messages.error(request, "Ngày sinh không hợp lệ.")
            user.job = request.POST.get("career", user.job)
            user.other = request.POST.get("other", user.other)

            user.save()
            messages.success(request, "Cập nhật thông tin thành công!")

    except StudentsAccount.DoesNotExist:
        try:
            user = Student.objects.get(email=email)
            approved = False
        except Student.DoesNotExist:
            return redirect('login')

    return render(request, 'home/account.html', {
        'user': user,
        'approved': approved
    })

def calendar_view(request):
    today = datetime.today()
    year = today.year
    month = today.month

    cal = calendar.Calendar(firstweekday=0)
    month_days = [day for day in cal.itermonthdates(year, month)]

    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    context = {
        'year': year,
        'month': month,
        'today': today,
        'month_days': month_days,
        'weekdays': weekdays,
    }
    return render(request, 'home/calendar.html', context)

def courses_view(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    student = StudentsAccount.objects.get(email=email)

    # Khóa học đã đăng ký
    my_courses = RecommendCourse.objects.filter(student_id=student.student_id)

    # Nếu chưa có khóa học nào → gợi ý toàn bộ
    if not my_courses.exists():
        suggested_courses = CourseModule.objects.all()
    else:
        # Khóa học chưa đăng ký
        registered_codes = my_courses.values_list('code', flat=True)
        available_courses = CourseModule.objects.exclude(code__in=registered_codes)

        # ========================================
        # 1. Tính tổng thời lượng học trong ngày
        # ========================================
        today = now().date()
        total_today = UserAction.objects.filter(
            user=student,
            timestamp__date=today
        ).aggregate(total=Sum("duration"))["total"] or 0

        # Ngưỡng phân loại
        HIGH_ACTIVITY = 2 * 60 * 60   # > 2 giờ/ngày
        LOW_ACTIVITY = 30 * 60        # < 30 phút/ngày

        # ========================================
        # 2. Gợi ý dựa vào hành vi
        # ========================================
        if total_today >= HIGH_ACTIVITY:
            # Học chăm chỉ → gợi ý khóa học nhiều tín chỉ
            suggested_courses = available_courses.order_by("-credits")[:10]
        elif total_today <= LOW_ACTIVITY:
            # Học ít → gợi ý khóa học ngắn / ít tín chỉ
            suggested_courses = available_courses.order_by("credits")[:10]
        else:
            # Trung bình → gợi ý theo tên
            suggested_courses = available_courses.order_by("name")[:10]

    return render(request, "home/courses.html", {
        "my_courses": my_courses,
        "suggested_courses": suggested_courses
    })
'''
=================================================================
Mục đề xuất sách
==================================================================
'''
def get_similar_books(book, all_books, top_n=5):
    if not book:
        return []

    corpus = [b.title + " " + (b.author or "") for b in all_books]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    book_idx = list(all_books).index(book)
    cosine_sim = cosine_similarity(tfidf_matrix[book_idx], tfidf_matrix).flatten()

    similar_indices = cosine_sim.argsort()[-top_n-1:-1][::-1]
    return [list(all_books)[i] for i in similar_indices if i != book_idx]

def documents_view(request):
    recommend_books = RecommendDocument.objects.all().order_by("-id")

    paginator = Paginator(recommend_books, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Upload
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home:documents')
    else:
        form = DocumentUploadForm()

    # Sách đã đọc gần đây (theo student_id giả lập)
    student_id = "demo_user"  # sau này lấy từ session/login
    recent_actions = UserActionBook.objects.filter(student_id=student_id).order_by("-timestamp")[:5]
    recent_books = [a.book for a in recent_actions]

    # Nếu có sách đã đọc thì gợi ý sách tương tự cuốn gần nhất
    similar_books = []
    if recent_books:
        similar_books = get_similar_books(recent_books[0], recommend_books, top_n=5)

    return render(request, 'home/documents.html', {
        'page_obj': page_obj,
        'recommend_count': paginator.count,
        'form': form,
        'recent_books': recent_books,
        'similar_books': similar_books,
    })

def register_course(request, code):
    """API cho nút 'Đăng ký' trong template"""
    if request.method == "POST":
        email = request.session.get('user_email')
        if not email:
            return JsonResponse({"success": False, "message": "Bạn chưa đăng nhập."})

        student = StudentsAccount.objects.get(email=email)
        course = get_object_or_404(CourseModule, code=code)

        # Kiểm tra đã đăng ký chưa
        if RecommendCourse.objects.filter(student_id=student.student_id, code=course.code).exists():
            return JsonResponse({"success": False, "message": "Bạn đã đăng ký khóa học này."})

        # Tạo bản ghi mới
        RecommendCourse.objects.create(
            student_id=student.student_id,
            code=course.code,
            name=course.name,
            credits=course.credits,
            status="studying"   # hoặc "pending", tùy bạn định nghĩa
        )
        return JsonResponse({"success": True, "message": "Đăng ký thành công!"})

    return JsonResponse({"success": False, "message": "Phương thức không hợp lệ."})

def course_detail(request, code):
    # Lấy email từ session
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    # Lấy thông tin student
    student = get_object_or_404(StudentsAccount, email=email)

    # Lấy khóa học
    course_module = get_object_or_404(CourseModule, code=code)

    # Lấy các bài học trong khóa học
    lessons = ListLesson.objects.filter(course=course_module)

    # Kiểm tra xem student đã đăng ký khóa học chưa
    registered = RecommendCourse.objects.filter(student_id=student.student_id, code=course_module.code).exists()

    return render(request, 'home/course_detail.html', {
        'course': course_module,
        'lessons': lessons,
        'registered': registered,
        'student': student
    })


def notification_view(request):
    return render(request, 'home/notification.html')

def results_view(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    student = StudentsAccount.objects.get(email=email)
    # Lấy toàn bộ dữ liệu RecommendCourse
    my_courses = RecommendCourse.objects.filter(status="passed").count()

    # Truyền sang template
    return render(request, 'home/results.html', {'recommend_courses': my_courses})

def teachers(request):
    teachers = Teacher.objects.all()
    return render(request, "home/teachers.html", {"teachers": teachers})

def courses_current(request):
    email = request.session.get('user_email')
    if not email:
        return redirect('login')

    student = StudentsAccount.objects.get(email=email)

    # Khóa học đã đăng ký
    my_courses = RecommendCourse.objects.filter(student_id=student)

    # Lấy danh sách mã khóa học đã đăng ký
    registered_codes = my_courses.values_list('code', flat=True)

    # Khóa học gợi ý (hiện có nhưng chưa đăng ký)
    suggested_courses = CourseModule.objects.exclude(code__in=registered_codes)

    return render(request, 'home/centers.html', {
        'my_courses': my_courses,
        'suggested_courses': suggested_courses
    })


def help_page(request):
    return render(request, 'home/help.html')

def login_view(request):
    return render(request, "login/login.html")
#=========== chatbot====================
def chat(request):
    return render(request, "home/chat.html")
# ==============================
# Load model PhoGPT-4B-Chat GGUF khi server start
# ==============================
llm = Llama(
    model_path=r"C:\Users\dungdam\.cache\huggingface\hub\models--vinai--PhoGPT-4B-Chat-gguf\snapshots\192f8ac548e5012d28d8703111842c49fef39271\PhoGPT-4B-Chat-Q4_K_M.gguf",
    n_gpu_layers=-1,   # -1 = dùng toàn bộ GPU
    n_ctx=8192
)

# ==============================
# Hàm tìm kiếm Google offline (Selenium)
# ==============================
def search_web(query, max_results=2):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.google.com/search?q={query}")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = []

    for g in soup.find_all('div', class_='tF2Cxc')[:max_results]:
        title = g.find('h3').text if g.find('h3') else ''
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else ''
        results.append(f"{title}\n{snippet}")

    driver.quit()
    return " ".join(results)

# ==============================
# Hàm tạo reply từ model
# ==============================
def generate_reply(user_message):
    # Step 1: search web để lấy nội dung tham khảo
    web_content = search_web(user_message)

    # Step 2: feed web content vào PhoGPT-4B-Chat
    prompt = f"""
    Bạn là trợ lý AI thông minh.
    Trả lời bằng TIẾNG VIỆT, ngắn gọn, trọng tâm, 1 câu nếu có thể.
    Nếu câu hỏi liên quan đến nội dung bạn không biết, hoặc cần tạo hình ảnh, âm thanh, video... thì trả lời: "Tôi không thể thực hiện yêu cầu này".
    Không lặp lại câu hỏi, không hỏi lại người dùng.
    Thông tin tham khảo: {web_content}
    Câu hỏi: {user_message}
    Trả lời AI:"""

    output = llm(prompt, max_tokens=512, temperature=0.7,stop=["\n", "Người dùng:", "AI:"])
    return output['choices'][0]['text'].strip() if output.get('choices') else "[AI không trả lời được]"

# ==============================
# View API chat
# ==============================
def chat_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()
            if not message:
                reply = "Xin vui lòng nhập tin nhắn"
            else:
                try:
                    reply = generate_reply(message)
                except Exception as e:
                    print("Lỗi generate_reply:", e)
                    reply = "[AI không trả lời được, lỗi GPU hoặc web]"
            return JsonResponse({"reply": reply})
        except Exception as e:
            print("Lỗi chat_api:", e)
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)

#==============================================#
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(ListLesson, id=lesson_id)
    return render(request, "home/lessons.html", {"lesson": lesson})

def log_action(request, lesson_id):
    if request.method == "POST":
        action = request.POST.get("action")
        if action in ['play', 'pause', 'back', 'done']:
            try:
                email = request.session.get('user_email')
                student_acc = StudentsAccount.objects.get(email=email)
                lesson = ListLesson.objects.get(id=lesson_id)

                # Tạo hoặc cập nhật duration trong ngày hôm nay
                today = now().date()
                
                # Lấy tất cả play chưa có duration hôm nay
                plays_today = UserAction.objects.filter(
                    user=student_acc,
                    video=lesson,
                    action="play",
                    timestamp__date=today
                ).order_by("timestamp")
                
                # Nếu action là play
                if action == "play":
                    UserAction.objects.create(
                        user=student_acc,
                        video=lesson,
                        action="play",
                        duration=0,
                        timestamp=now()
                    )
                else:
                    # Tính duration từ play gần nhất hôm nay
                    last_play = plays_today.filter(duration=0).last()
                    if last_play:
                        end_time = now()
                        duration = (end_time - last_play.timestamp).total_seconds()
                        last_play.duration = duration
                        last_play.save()
                    
                    # Tạo record cho action hiện tại
                    UserAction.objects.create(
                        user=student_acc,
                        video=lesson,
                        action=action,
                        duration=0,  # chỉ lưu duration cho play → pause/back/done sẽ update play
                        timestamp=now()
                    )

                # **Cập nhật tổng thời gian học hôm nay**
                total_duration_today = UserAction.objects.filter(
                    user=student_acc,
                    timestamp__date=today
                ).aggregate(total=models.Sum('duration'))['total'] or 0

                # Có thể lưu record tổng thời gian hôm nay vào một bảng khác nếu muốn,
                # hoặc chỉ hiển thị trực tiếp trong index.

                return JsonResponse({"status": "ok", "action": action, "today_duration": total_duration_today})

            except ListLesson.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Lesson not found"}, status=404)
            except StudentsAccount.DoesNotExist:
                return JsonResponse({"status": "error", "message": "User not found"}, status=404)
        else:
            return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)
    return JsonResponse({"status": "error", "message": "POST request required"}, status=400)






