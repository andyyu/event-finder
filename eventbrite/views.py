from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests
import json

def index(request): # handle landing page
  categories = requests.get("https://www.eventbriteapi.com/v3/categories/?token=6ZV47C6V2UXZXIRB3KEQ")
  categories = categories.json()['categories']
  template = loader.get_template('eventbrite/index.html')
  context = {
    'categories': categories,
  }
  return HttpResponse(template.render(context, request))

def results(request): # events results page
  # build categories from index
  chosen_ids = request.POST.getlist('category')
  id_string = ""
  category_string = ""
  for c_id in chosen_ids:
    category = requests.get("https://www.eventbriteapi.com/v3/categories/" + c_id + "/?token=6ZV47C6V2UXZXIRB3KEQ")
    category_name = category.json()['name']
    category_string += category_name + ', '
    id_string += c_id + ','
  id_string = id_string[:-1]

  # build categories from pagination
  if ('categories' in request.GET and request.GET.get('categories') != ''):
    id_string = str(request.GET.get('categories'))
  category_string = category_string[:-2]

  # Eventbrite API calls with category IDs and page #s
  page = str(request.GET.get('page'))
  event_json = requests.get("https://www.eventbriteapi.com/v3/events/search/?categories=" + id_string + "&page=" + page + "&token=6ZV47C6V2UXZXIRB3KEQ")
  event_data = json.loads(event_json.text)  # turn Request object to dict
  events = event_data['events']
  page_data = event_data['pagination']

  # pagination
  p_num = page_data['page_number']
  page_data['has_next'] = (page_data['page_count'] != p_num) # false if last page, true o.w.
  page_data['has_previous'] = (p_num != 1) # false if first page, true o.w.
  if (page_data['has_next']):
    page_data['next_page'] = p_num + 1
  if (page_data['has_previous']):
    page_data['previous_page'] = p_num -1

  # data to be passed in to template
  context = { 
    'events': events,
    'page_data': page_data,
    'categories': {'cat_string': category_string, 'ids': id_string}
  }
  template = loader.get_template('eventbrite/results.html')
  return HttpResponse(template.render(context))