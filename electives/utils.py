"""
SJBIT Elective Allocation Engine
─────────────────────────────────
First-Come-First-Served allocation based on submission timestamp AND preference ranking.
Algorithm:
  1. Get all pending preferences sorted by: submission time (earliest first), then rank (1st choice first)
  2. For each preference in order:
     - If student already has 3 allocations (1 OPEN + 1 PROFESSIONAL + 1 ABILITY) → skip
     - If course has seats AND matches student's allocation needs → allocate
     - Else → waitlist
  3. Students get THREE confirmed allocations:
     - One OPEN elective (NOT from their own department)
     - One PROFESSIONAL elective (can be from any department)
     - One ABILITY ENHANCEMENT elective (can be from any department)
  4. Allocation priority:
     - Students submit up to 5 preferences (must include at least 1 OPEN, 1 PROFESSIONAL, 1 ABILITY)
     - System tries to allocate based on FCFS (submission time) and preference rank
     - Each student gets exactly 3 courses (1 of each type)
"""

from django.db import transaction
from django.utils import timezone
from .models import Preference, Allocation, Waitlist, AllocationRun, Course


def _get_preference_key(pref):
    """Return sorting key: (submission_time, rank)."""
    return (pref.submitted_at, pref.rank)


@transaction.atomic
def run_allocation(run_by='system', reset=False):
    if reset:
        Allocation.objects.all().delete()
        Waitlist.objects.all().delete()
        Course.objects.all().update(enrolled_count=0)
        Preference.objects.all().update(status='pending')

    allocated = waitlisted = rejected = 0
    
    # Reset enrolled counts
    Course.objects.filter(is_active=True).update(enrolled_count=0)
    
    # Get all pending preferences sorted by submission time (FCFS) then rank
    all_pending = list(
        Preference.objects.filter(status='pending')
        .select_related('student', 'course')
        .order_by('submitted_at', 'rank')
    )
    
    # Track which students have been allocated and what types
    # Format: {student_id: {'open': bool, 'professional': bool, 'ability': bool}}
    student_allocations = {}
    
    # Track waitlist positions per course
    waitlist_positions = {}
    
    for pref in all_pending:
        student = pref.student
        course = pref.course
        
        # Initialize student allocation tracking if not exists
        if student.id not in student_allocations:
            student_allocations[student.id] = {'open': False, 'professional': False, 'ability': False}
        
        # Check if student already has all 3 allocations
        alloc_status = student_allocations[student.id]
        if alloc_status['open'] and alloc_status['professional'] and alloc_status['ability']:
            pref.status = 'rejected'
            pref.save(update_fields=['status'])
            rejected += 1
            continue
        
        # Check if student needs this type of course
        needs_open = not alloc_status['open'] and course.category == 'open'
        needs_professional = not alloc_status['professional'] and course.category == 'professional'
        needs_ability = not alloc_status['ability'] and course.category == 'ability'
        
        if not (needs_open or needs_professional or needs_ability):
            # Student doesn't need this type of course (already has one)
            pref.status = 'rejected'
            pref.save(update_fields=['status'])
            rejected += 1
            continue
        
        # For OPEN electives: Check if course is from student's own department
        if course.category == 'open' and student.department and course.department:
            if student.department.code == course.department.code:
                # Student trying to select OPEN elective from their own department - reject
                pref.status = 'rejected'
                pref.save(update_fields=['status'])
                rejected += 1
                continue
        
        # Check course availability
        if course.enrolled_count < course.total_seats:
            # Allocate to this course
            Allocation.objects.update_or_create(
                student=student, course=course,
                defaults=dict(
                    status='confirmed',
                    preference_rank=pref.rank,
                    priority_score=0,  # No priority score needed for FCFS
                    allocated_by='system',
                    allocated_at=timezone.now(),
                )
            )
            pref.status = 'allocated'
            pref.save(update_fields=['status'])
            course.enrolled_count += 1
            course.save(update_fields=['enrolled_count'])
            
            # Update student allocation tracking
            if course.category == 'open':
                student_allocations[student.id]['open'] = True
            elif course.category == 'professional':
                student_allocations[student.id]['professional'] = True
            elif course.category == 'ability':
                student_allocations[student.id]['ability'] = True
            
            allocated += 1
        else:
            # Waitlist
            if course.id not in waitlist_positions:
                waitlist_positions[course.id] = Waitlist.objects.filter(course=course, is_active=True).count() + 1
            
            Allocation.objects.update_or_create(
                student=student, course=course,
                defaults=dict(
                    status='waitlisted',
                    preference_rank=pref.rank,
                    priority_score=0,
                    allocated_by='system'
                )
            )
            Waitlist.objects.get_or_create(
                student=student, course=course,
                defaults=dict(
                    position=waitlist_positions[course.id],
                    is_active=True
                )
            )
            waitlist_positions[course.id] += 1
            pref.status = 'waitlisted'
            pref.save(update_fields=['status'])
            waitlisted += 1
    
    return AllocationRun.objects.create(
        run_by=run_by,
        total_allocated=allocated,
        total_waitlisted=waitlisted,
        total_rejected=rejected,
    )


@transaction.atomic
def promote_waitlist(course):
    """Promote next in waitlist when a seat frees up."""
    if course.available_seats <= 0:
        return None
    nxt = Waitlist.objects.filter(course=course, is_active=True).order_by('position').first()
    if not nxt:
        return None
    student = nxt.student
    Allocation.objects.filter(student=student, course=course).update(
        status='confirmed', allocated_by='waitlist', allocated_at=timezone.now()
    )
    Preference.objects.filter(student=student, course=course).update(status='allocated')
    nxt.is_active   = False
    nxt.promoted_at = timezone.now()
    nxt.save()
    course.enrolled_count = min(course.enrolled_count + 1, course.total_seats)
    course.save(update_fields=['enrolled_count'])
    # Re-number remaining
    for i, w in enumerate(Waitlist.objects.filter(course=course, is_active=True).order_by('position'), 1):
        w.position = i
        w.save(update_fields=['position'])
    return student


def check_eligibility(student, course):
    """Return (ok: bool, reason: str)."""
    if student.semester not in course.semesters_list:
        return False, f'Course not available for Semester {student.semester}.'
    
    # For OPEN electives: Students cannot select courses from their own department
    if course.category == 'open' and student.department and course.department:
        if student.department.code == course.department.code:
            return False, f'OPEN electives must be from other departments. This course is from your own department ({course.department.code}).'
    
    from .models import CourseHistory
    hist = CourseHistory.objects.filter(student=student, course_code=course.code).first()
    if hist:
        if hist.hist_type == 'completed':
            return False, 'You have already completed this course.'
        if hist.hist_type == 'scheduled':
            return False, 'This course is already scheduled in a future semester.'
        if hist.hist_type == 'ongoing':
            return False, 'You are currently enrolled in this course.'
    if course.available_seats <= 0:
        return False, 'No seats available (you may still join the waitlist).'
    return True, 'Eligible'
