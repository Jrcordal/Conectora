from django.shortcuts import render, redirect, get_object_or_404
from .models import ClientProfile, Project, IntakeDocument
from .forms import ClientProfileForm, IntakeForm
from .decorators import authorized_required
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
# Create your views here.



@login_required
@authorized_required
def dashboard(request):
 
    return render(request, 'clients/dashboard.html')




@login_required
@authorized_required
def profile_form(request):
    profile, created = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save()  # guarda directamente en la DB

            return redirect('clients:dashboard')

    else:
        form = ClientProfileForm(instance=profile)

    return render(request, 'clients/profile_form.html', {
        'form': form,
        'profile': profile,
    })



@login_required
@authorized_required
def intake_create(request):
    from .tasks import matching_pipeline  #
    client = get_object_or_404(ClientProfile, user=request.user)

    if request.method == "POST":
        form = IntakeForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                # 1) Crear el Project (uno nuevo por cada Intake)
                project = Project.objects.create(
                    client=client,
                    created_at= timezone.now()
                    # si quisieras campos adicionales, añádelos aquí
                )

                # 2) Crear Intake y vincularlo al Project + client/created_by
                intake = form.save(commit=False)
                intake.project = project
                intake.client = client
                intake.created_by = request.user
                intake.created_at= timezone.now()
                intake.save()

                # 3) Múltiples documentos (si en el form/plantilla lo llamas "documents")
                for f in request.FILES.getlist('intakedocuments'):
                    IntakeDocument.objects.create(
                        intake=intake,
                        file=f,
                        original_name=getattr(f, 'name', ''),
                        size_bytes = getattr(f,'size',None),
                    )

                # 4) Encolar la task DESPUÉS del commit
                transaction.on_commit(
                    lambda: matching_pipeline.delay(intake.id, project.id)
                )

            messages.success(
                request,
                "Intake created correctly. Matching being processed in the background"
            )
            return redirect('clients:dashboard')
            #return redirect("projects:detail", project_id=project.id)
    else:
        form = IntakeForm()

    return render(request, "clients/intake_form.html", {"form": form})