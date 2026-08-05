"""
Páginas da plataforma web do DisGeNET cube:
  - about: static page com os autores e a descrição do projeto
  - search: pesquisa de doenças com dropdown filter+pagination
  - stats: custom page com gráficos estatísticos (JSON API para Chart.js)
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum

from .models import DimDisease, DimDiseaseType, DimGene, FactGda, FactVda, DimSource, DimVariant


def about(request):
    """Static page describing the project and the team."""
    try:
        n_diseases = DimDisease.objects.count()
        n_genes = DimGene.objects.count()
        n_gda = FactGda.objects.count()
        n_vda = FactVda.objects.count()
        n_disease_types = DimDiseaseType.objects.count()
        n_variants = DimVariant.objects.count()
        n_sources = DimSource.objects.count()
    except Exception:
        n_diseases = n_genes = n_gda = n_vda = '–'
        n_disease_types = n_variants = n_sources = '–'

    context = {
        'n_diseases': n_diseases,
        'n_genes': n_genes,
        'n_gda': n_gda,
        'n_vda': n_vda,
        'n_disease_types': n_disease_types,
        'n_variants': n_variants,
        'n_sources': n_sources,
    }
    return render(request, 'disgenet_app/about.html', context)


def search(request):
    if request.method == 'POST':
        name_filter = request.POST.get('nameFilter', '').strip()
        type_filter = request.POST.get('typeFilter', '').strip()
        sort_by = request.POST.get('sortBy', '').strip()
        per_page = request.POST.get('perPage', '15').strip()
        page_number = 1
    else:
        name_filter = request.GET.get('nameFilter', '').strip()
        type_filter = request.GET.get('typeFilter', '').strip()
        sort_by = request.GET.get('sortBy', '').strip()
        per_page = request.GET.get('perPage', '15').strip()
        page_number = request.GET.get('page', 1)

    diseases_qs = (
        DimDisease.objects
        .select_related('typeID')
        .annotate(
            gda_count=Count('factgda', distinct=True),
            avg_score=Avg('factgda__score'),
        )
    )

    if name_filter:
        diseases_qs = diseases_qs.filter(name__icontains=name_filter)

    if type_filter:
        diseases_qs = diseases_qs.filter(typeID__typeID=type_filter)

    selected_type = None
    if type_filter:
        selected_type = DimDiseaseType.objects.filter(typeID=type_filter).first()

    if sort_by == 'name':
        diseases_qs = diseases_qs.order_by('name')
    elif sort_by == 'gda_count':
        diseases_qs = diseases_qs.order_by('-gda_count', 'name')
    elif sort_by == 'avg_score':
        diseases_qs = diseases_qs.order_by('-avg_score', 'name')
    else:
        diseases_qs = diseases_qs.order_by('name')
    
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 15

    if per_page not in [15, 30, 50]:
        per_page = 15

    paginator = Paginator(diseases_qs, per_page)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    disease_types = DimDiseaseType.objects.order_by('name')

    has_filters = bool(name_filter or type_filter or sort_by or per_page != 15)

    context = {
        'page_obj': page_obj,
        'disease_types': disease_types,
        'currentNameFilter': name_filter,
        'currentTypeFilter': type_filter,
        'currentSort': sort_by,
        'currentPerPage': per_page,
        'selectedType': selected_type,
        'total_results': paginator.count,
        'hasFilters': has_filters,
    }
    return render(request, 'disgenet_app/search.html', context)


def stats(request):
    overview_top_genes = list(
        DimGene.objects.annotate(
            gda_count=Count('factgda', distinct=True),
            avg_score=Avg('factgda__score')
        ).order_by('-gda_count')[:10]
    )

    overview_top_sources = list(
        DimSource.objects.annotate(
            gda_count=Count('factgda', distinct=True)
        ).order_by('-gda_count')[:8]
    )

    top_gda_sources = list(
        DimSource.objects.annotate(
            gda_count=Count('factgda', distinct=True)
        ).order_by('-gda_count')[:8]
    )
    top_gda_genes = list(
        DimGene.objects.annotate(
            gda_count=Count('factgda', distinct=True),
            avg_score=Avg('factgda__score')
        ).order_by('-gda_count')[:10]
    )
    top_disease_types = list(
        DimDiseaseType.objects.annotate(
            disease_count=Count('diseases', distinct=True)
        ).order_by('-disease_count')
    )
    top_vda_sources = list(
        DimSource.objects.annotate(
            vda_count=Count('factvda', distinct=True)
        ).order_by('-vda_count')[:8]
    )
    
    top_vda_variants = list(
        DimVariant.objects.annotate(
            vda_count=Count('factvda', distinct=True)
        ).order_by('-vda_count')[:10]
    )   
    return render(request, 'disgenet_app/stats.html', {
        'top_gda_sources': top_gda_sources,
        'top_gda_genes': top_gda_genes,
        'top_disease_types': top_disease_types,
        'top_vda_sources': top_vda_sources,
        'top_vda_variants': top_vda_variants,
        'overview_top_genes': overview_top_genes,
        'overview_top_sources': overview_top_sources,
    })


def api_scores_distribution(request):
    try:
        buckets = {}
        for i in range(10):
            lo = round(i * 0.1, 1)
            hi = round((i + 1) * 0.1, 1)
            count = FactGda.objects.filter(score__gte=lo, score__lt=hi).count()
            buckets[f'{lo:.1f}–{hi:.1f}'] = count

        return JsonResponse({
            'labels': list(buckets.keys()),
            'data': list(buckets.values())
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_gda_by_year(request):
    try:
        rows = (
            FactGda.objects
            .filter(year__isnull=False, year__gte=1990)
            .values('year')
            .annotate(count=Count('FactGDAKey'))
            .order_by('year')
        )
        labels = [r['year'] for r in rows]
        data = [r['count'] for r in rows]
        return JsonResponse({'labels': labels, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_disease_types_pie(request):
    try:
        rows = (
            DimDiseaseType.objects
            .annotate(count=Count('diseases', distinct=True))
            .order_by('-count')
        )
        labels = [r.name or r.typeID for r in rows]
        data = [r.count for r in rows]
        return JsonResponse({'labels': labels, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_vda_scores_distribution(request):
    try:
        buckets = {}
        for i in range(10):
            lo = round(i * 0.1, 1)
            hi = round((i + 1) * 0.1, 1)
            count = FactVda.objects.filter(score__gte=lo, score__lt=hi).count()
            buckets[f'{lo:.1f}–{hi:.1f}'] = count

        return JsonResponse({
            'labels': list(buckets.keys()),
            'data': list(buckets.values())
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_vda_by_year(request):
    try:
        rows = (
            FactVda.objects
            .filter(year__isnull=False, year__gte=1990)
            .values('year')
            .annotate(count=Count('FactVDAKey'))
            .order_by('year')
        )
        labels = [r['year'] for r in rows]
        data = [r['count'] for r in rows]
        return JsonResponse({'labels': labels, 'data': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def disease_detail(request, disease_id):
    disease = get_object_or_404(
        DimDisease.objects.select_related('typeID'),
        diseaseID=disease_id
    )

    gda_qs = (
        FactGda.objects
        .filter(diseaseID=disease)
        .select_related('geneID', 'sourceID')
    )

    genes = (
        gda_qs.values('geneID__geneID', 'geneID__name')
        .annotate(
            gda_count=Count('FactGDAKey'),
            avg_score=Avg('score')
        )
        .order_by('-gda_count', '-avg_score')[:10]
    )

    sources = (
        gda_qs.values('sourceID__sourceID', 'sourceID__name')
        .annotate(gda_count=Count('FactGDAKey'))
        .order_by('-gda_count')[:10]
    )

    stats = gda_qs.aggregate(
        gda_count=Count('FactGDAKey'),
        avg_score=Avg('score'),
        total_npmid=Sum('nPmid')
    )

    yearly = (
        gda_qs.exclude(year__isnull=True)
        .values('year')
        .annotate(count=Count('FactGDAKey'))
        .order_by('year')
    )

    context = {
        'disease': disease,
        'genes': genes,
        'sources': sources,
        'stats': stats,
        'yearly': yearly,
    }
    return render(request, 'disgenet_app/disease_detail.html', context)