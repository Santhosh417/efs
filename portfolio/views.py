from django.shortcuts import render
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomerSerializer
from weasyprint import HTML, CSS
from django.conf import settings
from django.template.loader import render_to_string
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse

now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html', {'portfolio': home})


@login_required
def customer_new(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            customers = Customer.objects.all()
            return render(request, 'portfolio/customer_list.html', {'customers': customers})

    else:
        form = CustomerForm()
    return render(request, 'portfolio/customer_new.html', {'form': form})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html', {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investments})

    else:
        form = InvestmentForm()
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.save()
            investments = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investments})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    print(sum_recent_value['recent_value__sum'])

    overall_investment_results = sum_recent_value['recent_value__sum'] - sum_acquired_value['acquired_value__sum']
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    overall_stocks_results = sum_current_stocks_value - float(sum_of_initial_stock_value)

    overall_initial_amount = float(sum_current_stocks_value) + float(sum_acquired_value['acquired_value__sum'])
    overall_recent_amount = float(sum_current_stocks_value) + float(sum_recent_value['recent_value__sum'])
    overall_total = overall_recent_amount - overall_initial_amount

    return render(request, 'portfolio/portfolio.html', {'customer': customer,
                                                        'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,
                                                        'overall_investment_results': overall_investment_results,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,
                                                        'overall_initial_amount': overall_initial_amount,
                                                        'overall_recent_amount': overall_recent_amount,
                                                        'overall_total': overall_total,
                                                        'overall_stocks_results': overall_stocks_results, })


# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self, request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)

@login_required
def portfolio_pdf(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    print(customer.id)
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    # overall_investment_results = sum_recent_value-sum_acquired_value
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()
    html_string = render_to_string('portfolio/portfolio_pdf.html', {'customer': customer,
                                                       'investments': investments,
                                                       'stocks': stocks,
                                                       'sum_acquired_value': sum_acquired_value,
                                                       'sum_recent_value': sum_recent_value,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,})

    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=portfolio_{}.pdf'.format(customer.name)
    response['Content-Transfer-Encoding'] = 'binary'
    result = HTML(string=html_string).write_pdf(response,
                                                stylesheets=[CSS(
                                                    settings.STATIC_ROOT + '/css/pdf.css')])
    return response


@login_required
def portfolio_pdf_email(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)
    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    # Initialize the value of the stocks
    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()
    # create invoice e-mail
    subject = '{} Portfolio'.format(customer.name)
    message = 'Hello {},\n' \
              'Please find the attachment for the e-copy of the you portfolio. \n' \
              'Contact us in case you need assistance of any sort, our team is happy to assist you. \n' \
              'Team Eagle Financial Services'.format(customer.name)
    email = EmailMessage(subject,
                         message,
                         'admin@efs.com',
                         [customer.email])

    html = render_to_string('portfolio/portfolio_pdf.html',
                            {'customers': customer,
                             'investments': investments,
                             'stocks': stocks,
                             'sum_acquired_value': sum_acquired_value,
                             'sum_recent_value': sum_recent_value,
                             'sum_current_stocks_value': sum_current_stocks_value,
                             'sum_of_initial_stock_value': sum_of_initial_stock_value, })
    out = BytesIO()
    HTML(string=html,base_url=request.build_absolute_uri()).write_pdf(out,
                                stylesheets=[CSS(settings.STATIC_ROOT + '/css/pdf.css')])
    email.attach('Portfolio_{}.pdf'.format(customer.name),
                 out.getvalue(),
                 'application/pdf')
    #send e-mail
    email.send()
    return render(request, 'portfolio/pdf_sent.html')
