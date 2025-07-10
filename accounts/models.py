from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

ROLES = (
    ('citizen', 'Citizen'),
    ('officer', 'Officer'),
    ('admin', 'Admin'),
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, phone, aadhaar, role, password=None):
        if not email:
            raise ValueError("Email is required")
        if not aadhaar or len(aadhaar) != 12:
            raise ValueError("Aadhaar must be 12 digits")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            aadhaar=aadhaar,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, aadhaar, password):
        user = self.create_user(email, name, phone, aadhaar, role='admin', password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=10)
    aadhaar = models.CharField(max_length=12, unique=True)
    role = models.CharField(max_length=10, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone', 'aadhaar']

    def __str__(self):
        return self.email

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

COMPLAINT_STATUS = (
    ('Pending', 'Pending'),
    ('In Progress', 'In Progress'),
    ('Resolved', 'Resolved'),
)

class Complaint(models.Model):
    citizen = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)  # ✅ Add this line
    title = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='complaints/photos/', null=True, blank=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=20, choices=COMPLAINT_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.citizen.name}"

class ComplaintAssignment(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE)
    officer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'officer'})
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.complaint.title} → {self.officer.name}"


from django.core.validators import MinValueValidator, MaxValueValidator

class Testimonial(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 (worst) and 5 (best)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Testimonial by {self.user.name} ({self.rating}⭐)"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

