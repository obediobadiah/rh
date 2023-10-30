
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_control

from rh.models import *

from .forms import *
from .models import *


@cache_control(no_store=True)
@login_required
def index_project_report_view(request, project):
    """Project Monthly Report View"""
    project = get_object_or_404(Project, pk=project)
    project_reports = ProjectMonthlyReport.objects.all()
    project_reports_todo = project_reports.filter(state__in=['todo', 'pending'])
    project_report_complete = project_reports.filter(state='complete')
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)
    context = {
        'project': project,
        'parent_page': parent_page,
        'project_reports': project_reports,
        'project_reports_todo': project_reports_todo,
        'project_report_complete': project_report_complete,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/views/monthly_reports_view_base.html', context)


@cache_control(no_store=True)
@login_required
def create_project_monthly_report_view(request, project):
    """Project Monthly Report Creation View"""
    project = get_object_or_404(Project, pk=project)
    project_state = project.state

    # Get all existing activity plans for the project
    activity_plans = project.activityplan_set.select_related('activity_domain', 'activity_type', 'activity_detail')
    # Get all existing target locaitions for the project
    target_locations = project.targetlocation_set.select_related('province', 'district').all()
    
    # Create Q objects for each location type
    province_q = Q(id__in=[location.province.id for location in target_locations if location.province])
    district_q = Q(id__in=[location.district.id for location in target_locations if location.district])
    zone_q = Q(id__in=[location.zone.id for location in target_locations if location.zone])

    # Collect provinces, districts, and zones using a single query for each
    target_location_provinces = Location.objects.filter(province_q)
    target_location_districts = Location.objects.filter(district_q)
    target_location_zones = Location.objects.filter(zone_q)

    # Create the Project Monthly Report form
    report_form = ProjectMonthlyReportForm(request.POST or None, initial={'project': project, 'state': 'todo'})

    # Create the activity plan formset with initial data from the project
    ActivityReportFormset = inlineformset_factory(
        ProjectMonthlyReport,
        ActivityPlanReport,
        form=ActivityPlanReportForm,
        extra=len(activity_plans),
        can_delete=True,
    )

    activity_report_formset = ActivityReportFormset(
        request.POST or None,
    )

    location_report_formsets = []
    for activity_report in activity_report_formset.forms:
        # Create a target location formset for each activity plan form
        location_report_formset = TargetLocationReportFormSet(
            request.POST or None,
            instance=activity_report.instance,
            prefix=f'locations_report_{activity_report.prefix}'
        )
        for location_report_form in location_report_formset.forms:
            # Create a disaggregation formset for each target location form
            disaggregation_report_formset = DisaggregationReportFormSet(
                request.POST or None,
                instance=location_report_form.instance,
                prefix=f'disaggregation_report_{location_report_form.prefix}'
            )
            location_report_form.disaggregation_report_formset = disaggregation_report_formset


        # Loop through the forms in the formset and set queryset values for specific fields
        for i, form in enumerate(location_report_formset.forms):
            if i < len(target_locations):
                target_location = target_locations[i]
                form.fields['province'].queryset = Location.objects.filter(id__in=target_location_provinces)
                form.fields['district'].queryset = Location.objects.filter(id__in=target_location_districts)
                form.fields['zone'].queryset = Location.objects.filter(id__in=target_location_zones)

        location_report_formsets.append(location_report_formset)


    # Loop through the forms in the formset and set initial and queryset values for specific fields
    for i, form in enumerate(activity_report_formset.forms):
        if i < len(activity_plans):
            activity_plan = activity_plans[i]
            form.initial = {'activity_plan': activity_plan, 'project_id': project}
            form.fields['indicator'].queryset = activity_plan.indicators.all()
    
    if request.method == 'POST':
        if report_form.is_valid():
            monthly_report = report_form.save()
            if activity_report_formset.is_valid():
                # Save valid activity plan forms
                for activity_report_form in activity_report_formset:
                    if activity_report_form.cleaned_data.get('indicator'):
                        activity_report = activity_report_form.save(commit=False)
                        activity_report.monthly_report = monthly_report
                        activity_report.save()

                # Process target location forms and their disaggregation forms
                for location_report_formset in location_report_formsets:
                    if location_report_formset.is_valid():
                        for location_report_form in location_report_formset:
                            if location_report_form.cleaned_data != {}:
                                if location_report_form.cleaned_data.get(
                                        'province') and location_report_form.cleaned_data.get('district'):

                                    location_report = location_report_form.save(commit=False)
                                    location_report.activity_plan_report = activity_report
                                    location_report.save()

                            if hasattr(location_report_form, 'disaggregation_report_formset'):
                                disaggregation_report_formset = location_report_form.disaggregation_report_formset
                                if disaggregation_report_formset.is_valid():

                                    # Delete the exisiting instances of the disaggregation location and create new
                                    # based on the indicator disaggregations
                                    location_report_form.instance.disaggregationlocationreport_set.all().delete()

                                    for disaggregation_report_form in disaggregation_report_formset:
                                        if disaggregation_report_form.cleaned_data != {} and disaggregation_report_form.cleaned_data.get('target') > 0:
                                            disaggregation_report_instance = disaggregation_report_form.save(commit=False)
                                            disaggregation_report_instance.target_location = location_report
                                            disaggregation_report_instance.save()

                # activity_report_formset.save()
                return redirect('create_project_monthly_report', project=project.pk)
            else:
                # TODO:
                # Handle invalid activity_plan_formset
                # Add error handling code here
                pass


    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)
    
    combined_formset = zip(activity_report_formset.forms, location_report_formsets)

    context = {
        'project': project,
        'activity_plans': activity_plans,
        'report_form': report_form,
        'activity_report_formset': activity_report_formset,
        'location_report_formset': location_report_formset,
        'combined_formset': combined_formset,
        'parent_page': parent_page,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/forms/monthly_report_form.html', context)


@cache_control(no_store=True)
@login_required
def details_monthly_progress_view(request, pk):
    """Project Monthly Report Read View"""
    project = get_object_or_404(Project, pk=pk)
    project_state = project.state
    parent_page = {
        'in-progress': 'active_projects',
        'draft': 'draft_projects',
        'done': 'completed_projects',
        'archive': 'archived_projects'
    }.get(project_state, None)
    context = {
        'project': project,
        'parent_page': parent_page,
        'project_view': False,
        'financial_view': False,
        'reports_view': True,
    }

    return render(request, 'project_reports/views/monthly_report_view.html', context)