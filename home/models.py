from django.db import models
from django.contrib.auth.models import User

# Thông tin tài khoản sinh viên
class StudentsAccount(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField()
    gender = models.IntegerField()
    student_id = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    job = models.CharField(max_length=50)
    other=models.CharField(max_length=45)

    class Meta:
        db_table = 'account_students'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Tài liệu đề xuất
class RecommendDocument(models.Model):
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=1024, null=True, blank=True)
    source = models.CharField(max_length=64, null=True, blank=True)  # ví dụ: 'gutenberg', 'openlibrary'
    source_id = models.CharField(max_length=128, null=True, blank=True)
    url = models.TextField(null=True, blank=True)  # link đến sách
    format = models.CharField(max_length=512, null=True, blank=True)  # ví dụ: pdf, epub
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommend_book'

    def is_pdf(self):
        if self.url and self.url.lower().endswith(".pdf"):
            return True
        return False

    def get_link(self):
        return self.url or ""

    def __str__(self):
        return self.title



# Khóa học gốc
class CourseModule(models.Model):
    code = models.CharField(max_length=20, primary_key=True)  # code làm khóa chính
    name = models.CharField(max_length=255)
    credits = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('passed', 'Đã hoàn thành'),
            ('studying', 'Đang học'),
            ('not_started', 'Chưa học'),
        ]
    )
    register_status = models.CharField(
        max_length=50,
        choices=[
            ('registered','Đã đăng ký'),
            ('not_register','Chưa đăng ký'),
        ]
    )

    class Meta:
        db_table = 'course_module'

    def __str__(self):
        return f"{self.code} - {self.name}"


# Khóa học của sinh viên
class RecommendCourse(models.Model):
    student_id = models.CharField(max_length=20)  # lưu student_id từ StudentsAccount
    code = models.CharField(max_length=50)         # mã khóa học
    name = models.CharField(max_length=255)
    credits = models.IntegerField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('passed', 'Đã hoàn thành'),
            ('studying', 'Đang học'),
            ('not_started', 'Chưa học'),
        ]
    )

    class Meta:
        db_table = 'mycourse'

    def __str__(self):
        return f"{self.student} - {self.code}"

# Danh sách bài học
class ListLesson(models.Model):
    course = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        db_column='code',
        to_field='code'
    )
    lesson_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='lessons_videos/', blank=True, null=True)  # thêm dòng này

    class Meta:
        db_table = 'list_lesson'

    def __str__(self):
        return f"{self.lesson_name} ({self.course.name})"

class Teacher(models.Model):
    teacher_name = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'teacher'

    def __str__(self):
        return f"{self.teacher_name} - {self.course_name}"

class UserAction(models.Model):
    ACTION_CHOICES = [
        ('play', 'Play video'),
        ('pause', 'Pause video'),
        ('back', 'Back to list'),
        ('done', 'Mark as done'),
    ]
    user = models.ForeignKey(
        StudentsAccount,
        to_field='student_id',
        on_delete=models.CASCADE
    )
    video = models.ForeignKey(ListLesson, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)

    class Meta:
        db_table = "user_action"

    def __str__(self):
        return f"{self.user} - {self.video} - {self.action}"

class UserActionBook(models.Model):
    student_id = models.CharField(max_length=20)  # thay vì User mặc định
    book = models.ForeignKey(RecommendDocument, on_delete=models.CASCADE)
    action = models.CharField(
        max_length=50,
        choices=[
            ('view', 'Xem'),
            ('read', 'Đọc'),
            ('download', 'Tải xuống')
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # số giây đọc (nếu có)

    class Meta:
        db_table = 'user_action_book'

    def __str__(self):
        return f"{self.student_id} - {self.book.title} ({self.action})"