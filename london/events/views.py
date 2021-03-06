import datetime

from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.generic import DetailView, ListView

from django_ical.views import ICalFeed

from london.events.models import Event


class EventDetailView(DetailView):
    model = Event
    context_object_name = 'event'


class AllEvents(ListView):
    model = Event
    context_object_name = 'events'
    template_name = 'all.html'


class NextEvents(ListView):
    model = Event
    template_name = 'next.html'
    context_object_name = 'events'
    
    def get_queryset(self):
        return Event.objects.filter(
                    date__gte = datetime.date.today()
                ).order_by(
                    'date'
                )


class NextEventJSON(ListView):
    def get(self, request, *args, **kwargs):
        events = Event.objects.filter(
                    date__gte = datetime.date.today()
                ).order_by(
                    'date'
                )[:2]
        event = events[0]
        
        now = datetime.datetime.now()
        ends = datetime.datetime.combine(event.date, event.ends)
        if now > ends:
            event = events[1]
        
        data = {
            'title': event.title,
            'pub': event.pub.name,
            'date': event.date.isoformat(),
            'starts': event.starts.isoformat(),
            'ends': event.ends.isoformat(),
            'time_until': event.time_until(),
        }
        
        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )


class PreviousEvents(ListView):
    model = Event
    template_name = 'previously.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
                    date__lte = datetime.date.today()
                ).order_by(
                    'date'
                )


class EventsICalFeed(ICalFeed):
    product_id = '-//PUBSTANDARDS//PUBCAL 1.0//EN'
    timezone = 'Europe/London'
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return u'Stuff'
    
    def item_start_datetime(self, item):
        return datetime.datetime.combine( item.date, datetime.time( 18, 0, 0 ) )
    
    def item_end_datetime(self, item):
        return datetime.datetime.combine( item.date, datetime.time( 23, 30, 0 ) )
        
    def item_location(self, item):
        if item.pub.address:
            return '%s, %s' % ( item.pub.name, item.pub.address )
        else:
            return item.pub.name


class NextEventsICalFeed(EventsICalFeed):
    def items(self):
        return Event.objects.filter(date__gte = datetime.date.today()).order_by('date')


class AllEventsICalFeed(EventsICalFeed):
    def items(self):
        return Event.objects.all().order_by('date')
