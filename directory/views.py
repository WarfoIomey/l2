from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from directory.models import Researches, Subgroups, ReleationsFT, Fractions, DirectionsGroup
import simplejson as json


@csrf_exempt
@login_required
def directory_researches(request):
    """GET: получение списка исследований для лаборатории. POST: добавление нового исследования"""
    return_result = {}
    if request.method == "POST":
        research = json.loads(request.POST["research"])
        if not research["title"] or not research["id"]:
            return_result = {"ok": False}
        else:
            if research["id"] == -1:
                research_obj = Researches(subgroup=Subgroups.objects.get(pk=research["lab_group"]))
            else:
                research_obj = Researches.objects.get(pk=research["id"])
            research_obj.title = research["title"]
            if not research["preparation"]:
                research["preparation"] = "Не требуется"
            research_obj.preparation = research["preparation"]
            if not research["quota_oms"] or research["quota_oms"] < 0:
                research["quota_oms"] = -1
            research_obj.quota_oms = research["quota_oms"]
            research_obj.save()
            # Fractions.objects.filter(research=research_obj).delete()
            fractions_pk = []
            for key in research["fraction"].keys():
                tube_relation = ReleationsFT.objects.get(pk=key.split("-")[1])
                for fraction in research["fraction"][key]["fractions"]:
                    if fraction["pk"] == -1:
                        fraction_obj = Fractions(title=fraction["title"], research=research_obj,
                                                 units=fraction["units"],
                                                 relation=tube_relation, ref_m=json.dumps(fraction["ref_m"]),
                                                 ref_f=json.dumps(fraction["ref_f"]))
                    else:
                        fraction_obj = Fractions.objects.get(pk=fraction["pk"])
                        fraction_obj.title = fraction["title"]
                        fraction_obj.research = research_obj
                        fraction_obj.units = fraction["units"]
                        fraction_obj.ref_m = fraction["ref_m"]
                        fraction_obj.ref_f = fraction["ref_f"]
                        fractions_pk.append(fraction["pk"])
                    fraction_obj.save()
            fractions = Fractions.objects.filter(research=research_obj)
            for fraction in fractions:
                if fraction.pk not in fractions_pk:
                    fraction.delete()
            return_result = {"ok": True, "id": research_obj.pk, "title": research_obj.title}
    elif request.method == "GET":
        return_result = {"researches": []}
        subgroup_id = request.GET["lab_group"]
        researches = Researches.objects.filter(subgroup__pk=subgroup_id)
        for research in researches:
            resdict = {"pk": research.pk, "title": research.title, "tubes": {}, "tubes_c": 0}
            fractions = Fractions.objects.filter(research=research)
            for fraction in fractions:
                if fraction.relation.pk not in resdict["tubes"].keys():
                    resdict["tubes_c"] += 1
                    resdict["tubes"][fraction.relation.pk] = {"id": fraction.relation.pk,
                                                              "color": fraction.relation.tube.color,
                                                              "title": fraction.relation.tube.title}
            return_result["researches"].append(resdict)

    return HttpResponse(json.dumps(return_result), content_type="application/json")  # Создание JSON


@csrf_exempt
@login_required
def directory_researches_list(request):
    """GET: получение списка исследований для лаборатории. POST: добавление нового исследования"""
    return_result = []
    if request.method == "GET":
        lab_id = request.GET["lab_id"]
        researches = Researches.objects.filter(subgroup__podrazdeleniye__pk=lab_id)
        for research in researches:
            return_result.append({"pk": research.pk, "fields": {"id_lab_fk": lab_id, "ref_title": research.title}})

    return HttpResponse(json.dumps(return_result), content_type="application/json")  # Создание JSON


@csrf_exempt
@login_required
def directory_research(request):
    """GET: получение исследования и фракций"""
    return_result = {}
    if request.method == "GET":
        id = int(request.GET["id"])
        research = Researches.objects.get(pk=id)
        return_result["title"] = research.title
        return_result["quota"] = research.quota_oms
        return_result["preparation"] = research.preparation
        return_result["fractiontubes"] = {}
        fractions = Fractions.objects.filter(research=research)
        for fraction in fractions:
            if "tube-" + str(fraction.relation.pk) not in return_result["fractiontubes"].keys():
                return_result["fractiontubes"]["tube-" + str(fraction.relation.pk)] = {"fractions": [],
                                                                                       "color": fraction.relation.tube.color,
                                                                                       "title": fraction.relation.tube.title,
                                                                                       "sel": "tube-" + str(
                                                                                           fraction.relation.pk)}
            ref_m = fraction.ref_m
            ref_f = fraction.ref_f
            if isinstance(ref_m, str):
                ref_m = json.loads(ref_m)
            if isinstance(ref_f, str):
                ref_f = json.loads(ref_f)
            return_result["fractiontubes"]["tube-" + str(fraction.relation.pk)]["fractions"].append(
                {"title": fraction.title, "units": fraction.units, "ref_m": ref_m,
                 "ref_f": ref_f, "pk": fraction.pk});

        '''
        sel: id,
        color: color,
        title: title,
        '''
    return HttpResponse(json.dumps(return_result), content_type="application/json")  # Создание JSON


@csrf_exempt
@login_required
def directory_researches_group(request):
    """GET: получение списка исследований для группы. POST: добавление новой или выбор существующей группы и привязка исследований к ней"""
    return_result = {}
    if request.method == "GET":
        return_result = {"researches": []}
        subgroup_id = request.GET["lab_group"]
        gid = int(request.GET["gid"])
        researches = Researches.objects.filter(subgroup__pk=subgroup_id)

        for research in researches:
            resdict = {"pk": research.pk, "title": research.title}
            if gid < 0:
                if not research.direction:
                    return_result["researches"].append(resdict)
            else:
                if research.direction and research.direction.pk == gid:
                    return_result["researches"].append(resdict)

    elif request.method == "POST":
        gid = int(request.POST["group"])
        if gid < 0:
            direction = DirectionsGroup()
            direction.save()
        else:
            direction = DirectionsGroup.objects.get(pk=gid)
        tmp_researches = Researches.objects.filter(direction=direction)
        for v in tmp_researches:
            v.direction = None
            v.save()

        researches = json.loads(request.POST["researches"])
        for k in researches.keys():
            if researches[k]:
                if k == "" or not k.isdigit() or not Researches.objects.filter(pk=k).exists(): continue
                research = Researches.objects.get(pk=k)
                research.direction = direction
                research.save()

        return_result["gid"] = direction.pk

    return HttpResponse(json.dumps(return_result), content_type="application/json")  # Создание JSON


@csrf_exempt
@login_required
def directory_get_directions(request):
    """GET: получение списка групп (по направлениям)"""
    return_result = {}
    if request.method == "GET":
        return_result = {"directions": {}}
        subgroup_id = request.GET["lab_group"]
        researches = Researches.objects.filter(subgroup__pk=subgroup_id)
        for research in researches:
            if not research.direction: continue
            if research.direction.pk not in return_result["directions"].keys():
                return_result["directions"][research.direction.pk] = []
            return_result["directions"][research.direction.pk].append(research.title)

    return HttpResponse(json.dumps(return_result), content_type="application/json")  # Создание JSON
