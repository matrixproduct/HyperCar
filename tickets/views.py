from django.views import View
from django.views.generic.base import TemplateView
from django.http.response import HttpResponse, Http404
from django.shortcuts import render
from collections import deque

####################################
# List of services

# service names and the corresponding times required
service_dic = {'Change oil': 2, 'Inflate tires': 5, 'Get diagnostic test': 30}
# service names
service_list = service_dic.keys()
# service urls and names [[url, name],...]
service_html_list = [['_'.join(service.lower().split()), service] for service in service_list]
service_html_list[2][0] = 'diagnostic'
# service urls
service_urls = [item[0] for item in service_html_list]
# service dic usrls [{url: time},...]
service_dic_urls = {}
for item in service_html_list:
    service_dic_urls[item[0]] = service_dic[item[1]]

# service priorities
service_names_prior = {'Change oil': 1, 'Inflate tires': 2, 'Get diagnostic test': 3}
service_priority = {}
for item in service_html_list:
    service_priority[item[0]] = service_names_prior[item[1]]
# processing list
processing_html_list = service_html_list[:]
processing_html_list[2][1] = 'Get diagnostic'

####################################


# line of cars {service name urls : [tickets]}
line_of_cars = {}

#  initialize line
for item in service_urls:
    line_of_cars[item] = deque([])

# initialize tickets
max_num = 1000
all_tickets = [False] * max_num  # True for an occupied ticket , False otherwise

# returns the first unoccupied ticket
def get_ticket():
    return all_tickets.index(False) + 1

# issues new ticket and returns its value
def new_ticket():
    n = get_ticket()
    all_tickets[n - 1] = True
    return n

# calculates waiting time
def waiting_time(service):
    t = 0
    for serv, tickets in line_of_cars.items():
        if service_priority[serv] <=  service_priority[service]:
            t += service_dic_urls[serv] * len(tickets)
    return t

# calculates queue for each service and returns dict: {url_serv: [name_serv, quue length]}
def queue_service():
    queue = {}
    for item in processing_html_list:
        serv = item[0]
        queue[serv] = [item[1], len(line_of_cars[serv])]
    return queue

# determines the next ticket
def next_ticket():
    for item in service_urls:
        if len(line_of_cars[item]) != 0:
            return line_of_cars[item][0]
    return 0  # if queue is empty
# determines the next ticket and removes it from the queue
def pop_next_ticket():
    for item in service_urls:
        if len(line_of_cars[item]) != 0:
            ticket = line_of_cars[item].popleft()  # pop ticket from the queue
            all_tickets[ticket - 1] = False  # release ticket number
            return ticket
    return 0  # if queue is empty

last_processed_ticket = 0

##########################
#  Http request handlers #
##########################

# Welcome page
class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')

# Show menu
class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html', context={'service_html_list': service_html_list})

# Get new ticket
class GetTicket(View):
    def get(self, request, service, *args, **kwargs):
        if service not in service_urls:
            raise Http404
        # calculate waiting time
        t = waiting_time(service)
        # add car to the line of cars
        ticket = new_ticket()
        line_of_cars[service].append(ticket)
        return render(request, 'tickets/getticket.html', context={
                     'ticket': ticket, "minutes_to_wait": t})

# # Processing
# class Processing(TemplateView):
#     template_name = 'tickets/processing.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # create a dictionary with the queue info
#         context['queue'] = queue_service()
#         return context


# Processing
class Processing(View):
    def get(self, request, *args, **kwargs):
        # create a dictionary with the queue info
        context = {'queue': queue_service()}
        return render(request, 'tickets/processing.html', context)

    def post(self, request, *args, **kwargs):
        global last_processed_ticket
        # get the next ticket and remove it from the queue
        ticket = pop_next_ticket()
        # update the last processed ticket
        last_processed_ticket = ticket
        print("post", ticket)
        return render(request, 'tickets/next.html', context={
                     'ticket': ticket})

# Show next ticket
class Next(View):
    def get(self, request, *args, **kwargs):
        global last_processed_ticket
        # get the last processed ticket
        ticket = last_processed_ticket
        print("get", ticket)
        return render(request, 'tickets/next.html', context={
                     'ticket': ticket})
    def post(self, request, *args, **kwargs):
        global last_processed_ticket
        # get the next ticket and remove it from the queue
        ticket = pop_next_ticket()
        # update the last processed ticket
        last_processed_ticket = ticket
        print("post", ticket)
        return render(request, 'tickets/next.html', context={
                     'ticket': ticket})
